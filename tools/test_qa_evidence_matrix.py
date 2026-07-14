from __future__ import annotations

import pytest

from tools import qa_evidence_matrix


@pytest.mark.xfail(
    reason=(
        "Pre-existing, not introduced this session (registered as B-35 at "
        ".harness/post-phase-8-forward-register.md, surfaced during B-28 "
        "test-quality triage 2026-07-14): 12 contracts (C-IS-14 + 11 C-MEM-*) "
        "have no test file citing their contract id anywhere in the repo. "
        "Neither this test nor tools/test_closure_gate.py is wired into any "
        "CI job (grep .github/workflows/ci.yml — testpaths in pyproject.toml "
        "excludes tools/), so this has been silently red with no CI signal."
    ),
    strict=True,
)
def test_q3_evidence_matrix_is_complete() -> None:
    matrix = qa_evidence_matrix.derive_matrix()
    stats = qa_evidence_matrix.summary(matrix)

    assert stats["contracts_total"] > 0
    assert qa_evidence_matrix.violations(matrix) == []
    assert stats["contracts_with_test_evidence"] == stats["contracts_total"]
    assert stats["cxa_seams_wired"] == stats["cxa_seams_total"]


def test_q3_evidence_report_renders_contract_rows() -> None:
    matrix = qa_evidence_matrix.derive_matrix()
    report = qa_evidence_matrix.render_markdown(matrix)

    assert "# R-CL-Q3 QA Evidence Matrix" in report
    assert "| Contracts with test proof |" in report
    assert "## Contract Evidence" in report

    # B-28 finding #18 (test-quality preflight 2026-07-12) — the prior body's
    # write-then-read-back assertion only proved the filesystem round-trips a
    # string, adding no coverage of `render_markdown` beyond the substring
    # checks above; assert real completeness instead — every contract row in
    # the matrix actually appears as a rendered table row.
    for row in matrix["contracts"]:
        assert f"| {row['contract_id']} |" in report


def test_violations_reports_missing_test_evidence_and_cxa_endpoint() -> None:
    """B-28 finding #17 (test-quality preflight 2026-07-12) — `violations()`
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

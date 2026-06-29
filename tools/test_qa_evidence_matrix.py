from __future__ import annotations

from tools import qa_evidence_matrix


def test_q3_evidence_matrix_is_complete() -> None:
    matrix = qa_evidence_matrix.derive_matrix()
    stats = qa_evidence_matrix.summary(matrix)

    assert stats["contracts_total"] > 0
    assert qa_evidence_matrix.violations(matrix) == []
    assert stats["contracts_with_test_evidence"] == stats["contracts_total"]
    assert stats["cxa_seams_wired"] == stats["cxa_seams_total"]


def test_q3_evidence_report_renders_contract_rows(tmp_path) -> None:
    matrix = qa_evidence_matrix.derive_matrix()
    report = qa_evidence_matrix.render_markdown(matrix)

    assert "# R-CL-Q3 QA Evidence Matrix" in report
    assert "| Contracts with test proof |" in report
    assert "## Contract Evidence" in report

    out = tmp_path / "matrix.md"
    out.write_text(report, encoding="utf-8")
    assert out.read_text(encoding="utf-8") == report

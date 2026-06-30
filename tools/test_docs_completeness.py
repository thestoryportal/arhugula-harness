from __future__ import annotations

from pathlib import Path

from tools.docs_completeness import EVIDENCE_MATRIX, REQUIRED_DOCS, validate


def _write_minimal_repo(root: Path) -> None:
    (root / "docs").mkdir()
    (root / ".harness").mkdir()
    (root / "README.md").write_text(
        "# Repo\n\nSee [docs](docs/README.md).\n",
        encoding="utf-8",
    )
    for doc in REQUIRED_DOCS:
        (root / doc).write_text(
            f"# {doc.stem}\n\n## Source Grounding\n\nGrounded in `README.md`.\n",
            encoding="utf-8",
        )
    (root / EVIDENCE_MATRIX).write_text(
        "# R-CL-D1 Documentation Completeness Matrix\n\n"
        "## Audience Coverage\n\n"
        "## Public Surface Coverage\n\n"
        "## Automated Completeness Gate\n\n"
        "## Operator Readthrough Checklist\n\n"
        "`README.md` `examples/README.md` `harness.toml.example` "
        "`harness-runtime/src/harness_runtime/cli/app.py` "
        "`harness-runtime/src/harness_runtime/config_source.py` "
        "`harness-runtime/src/harness_runtime/types.py` "
        "`harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py` "
        "`deploy/self-hosted-local/README.md` `deploy/managed-cloud/README.md` "
        "`deploy/images/README.md` `tools/q4_packaging_gate.py` "
        "`.harness/roadmap_status.md`\n",
        encoding="utf-8",
    )


def test_docs_completeness_accepts_complete_suite(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)

    report = validate(tmp_path)

    assert report.ready is True
    assert {check.name for check in report.checks if not check.ok} == set()


def test_docs_completeness_rejects_missing_required_doc(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    (tmp_path / "docs" / "reference.md").unlink()

    report = validate(tmp_path)

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "required-docs" in failed
    assert "docs/reference.md" in failed["required-docs"]


def test_docs_completeness_rejects_readme_without_docs_link(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    (tmp_path / "README.md").write_text("# Repo\n", encoding="utf-8")

    report = validate(tmp_path)

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "readme-discovery" in failed
    assert "docs/README.md" in failed["readme-discovery"]


def test_docs_completeness_rejects_doc_without_source_grounding(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    (tmp_path / "docs" / "architecture.md").write_text("# Architecture\n", encoding="utf-8")

    report = validate(tmp_path)

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "source-grounding" in failed
    assert "docs/architecture.md" in failed["source-grounding"]


def test_docs_completeness_rejects_broken_local_link(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    (tmp_path / "docs" / "README.md").write_text(
        "# Docs\n\n[missing](missing.md)\n\n## Source Grounding\n",
        encoding="utf-8",
    )

    report = validate(tmp_path)

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "markdown-links" in failed
    assert "missing.md" in failed["markdown-links"]

from __future__ import annotations

from pathlib import Path

from tools.closure_certification import (
    CERTIFICATION,
    REQUIRED_SECTIONS,
    REQUIRED_SOURCE_PATHS,
    REQUIRED_TOKENS,
    validate,
)


def _complete_certification() -> str:
    source_lines = "\n".join(f"- `{source}`" for source in REQUIRED_SOURCE_PATHS)
    token_lines = "\n".join(f"- {name}: {token}" for name, token in REQUIRED_TOKENS)
    sections = "\n\n".join(f"{section}\n\ncomplete" for section in REQUIRED_SECTIONS)
    return (
        "# R-CL-C1 Closure Certification\n\n"
        f"{sections}\n\n"
        "## Source Paths\n\n"
        f"{source_lines}\n\n"
        "## Required Tokens\n\n"
        f"{token_lines}\n"
    )


def _write_minimal_repo(root: Path) -> None:
    for source in REQUIRED_SOURCE_PATHS:
        path = root / source
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{source}\n", encoding="utf-8")
    cert = root / CERTIFICATION
    cert.parent.mkdir(parents=True, exist_ok=True)
    cert.write_text(_complete_certification(), encoding="utf-8")


def test_closure_certification_accepts_complete_artifact(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)

    report = validate(tmp_path)

    assert report.ready is True
    assert {check.name for check in report.checks if not check.ok} == set()


def test_closure_certification_rejects_missing_artifact(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    (tmp_path / CERTIFICATION).unlink()

    report = validate(tmp_path)

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "certification-exists" in failed


def test_closure_certification_rejects_missing_section(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    cert = tmp_path / CERTIFICATION
    cert.write_text(
        _complete_certification().replace("## Completeness Critic", ""), encoding="utf-8"
    )

    report = validate(tmp_path)

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "sections" in failed
    assert "Completeness Critic" in failed["sections"]


def test_closure_certification_rejects_missing_source_reference(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    cert = tmp_path / CERTIFICATION
    cert.write_text(
        _complete_certification().replace("tools/q4_packaging_gate.py", "tools/not-q4.py"),
        encoding="utf-8",
    )

    report = validate(tmp_path)

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "source-paths" in failed
    assert "tools/q4_packaging_gate.py" in failed["source-paths"]


def test_closure_certification_rejects_missing_coverage_token(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    cert = tmp_path / CERTIFICATION
    cert.write_text(_complete_certification().replace("123/123", "122/123"), encoding="utf-8")

    report = validate(tmp_path)

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "coverage-tokens" in failed
    assert "contract-proof-count" in failed["coverage-tokens"]


def test_closure_certification_rejects_broken_local_link(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    cert = tmp_path / CERTIFICATION
    cert.write_text(_complete_certification() + "\n[broken](missing.md)\n", encoding="utf-8")

    report = validate(tmp_path)

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "markdown-links" in failed
    assert "missing.md" in failed["markdown-links"]

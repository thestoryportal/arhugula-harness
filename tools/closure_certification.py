#!/usr/bin/env python3
"""Provider-free closure certification gate for R-CL-C1."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CERTIFICATION = Path(".harness/closure-certification.md")

REQUIRED_SECTIONS: tuple[str, ...] = (
    "## Certification Matrix",
    "## Source Evidence",
    "## Phase-9 Bounded-Residual Review",
    "## Completeness Critic",
    "## Review and Tenant Policy",
    "## Ship Evidence",
    "## Post-Merge Disposition",
)

REQUIRED_SOURCE_PATHS: tuple[str, ...] = (
    ".harness/audit/Closure_Gate_v1.md",
    "tools/closure_gate.py",
    ".harness/r-cl-q1-review.json",
    "tools/q1_review_gate.py",
    ".harness/r-cl-q2-security-review.md",
    ".harness/r-cl-q3-qa-evidence-matrix.md",
    "tools/qa_evidence_matrix.py",
    "tools/q4_packaging_gate.py",
    "deploy/images/README.md",
    "deploy/self-hosted-local/README.md",
    "deploy/managed-cloud/README.md",
    ".harness/r-cl-d1-docs-completeness.md",
    "tools/docs_completeness.py",
    "docs/README.md",
    ".harness/01-planning/01-harness-planning/00-harness-research/phase-9-retirement-criteria.md",
    "Project_Roadmap_v1.md",
    ".harness/roadmap_status.md",
    "tools/dashboard/roadmap.html",
)

REQUIRED_TOKENS: tuple[tuple[str, str], ...] = (
    ("arc", "R-CL-C1"),
    ("dimension-built", "built"),
    ("dimension-activated", "activated"),
    ("dimension-tested", "tested"),
    ("dimension-reviewed", "reviewed"),
    ("dimension-documented", "documented"),
    ("contract-proof-count", "123/123"),
    ("cxa-proof-count", "31/31"),
    ("adr-count", "11/11 ADR"),
    ("phase-q1", "R-CL-Q1"),
    ("phase-q2", "R-CL-Q2"),
    ("phase-q3", "R-CL-Q3"),
    ("phase-q4", "R-CL-Q4"),
    ("phase-d1", "R-CL-D1"),
    ("phase-9", "Phase-9"),
    ("tenant-policy", "tenant policy"),
    ("closure-check", "just closure-certification-check"),
    ("closure-gate", "just closure-gate"),
    ("codex-check", "just codex-check"),
    ("full-check", "just check"),
)

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class CertificationReport:
    ready: bool
    checks: tuple[CheckResult, ...]


def _ok(name: str, detail: str) -> CheckResult:
    return CheckResult(name=name, ok=True, detail=detail)


def _fail(name: str, detail: str) -> CheckResult:
    return CheckResult(name=name, ok=False, detail=detail)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _certification_exists_check(root: Path) -> CheckResult:
    path = root / CERTIFICATION
    if not path.is_file():
        return _fail("certification-exists", f"{CERTIFICATION.as_posix()} is missing")
    return _ok("certification-exists", f"{CERTIFICATION.as_posix()} exists")


def _sections_check(root: Path) -> CheckResult:
    path = root / CERTIFICATION
    if not path.is_file():
        return _fail("sections", f"{CERTIFICATION.as_posix()} is missing")
    content = _read(path)
    missing = [section for section in REQUIRED_SECTIONS if section not in content]
    if missing:
        return _fail("sections", f"missing sections: {missing}")
    return _ok("sections", f"{len(REQUIRED_SECTIONS)} required sections present")


def _source_paths_check(root: Path) -> CheckResult:
    path = root / CERTIFICATION
    if not path.is_file():
        return _fail("source-paths", f"{CERTIFICATION.as_posix()} is missing")
    content = _read(path)
    missing_refs = [source for source in REQUIRED_SOURCE_PATHS if source not in content]
    missing_files = [source for source in REQUIRED_SOURCE_PATHS if not (root / source).exists()]
    if missing_refs or missing_files:
        return _fail(
            "source-paths",
            f"missing refs={missing_refs or 'none'} missing files={missing_files or 'none'}",
        )
    return _ok("source-paths", f"{len(REQUIRED_SOURCE_PATHS)} source paths cited and present")


def _coverage_tokens_check(root: Path) -> CheckResult:
    path = root / CERTIFICATION
    if not path.is_file():
        return _fail("coverage-tokens", f"{CERTIFICATION.as_posix()} is missing")
    content = _read(path)
    missing = [name for name, token in REQUIRED_TOKENS if token not in content]
    if missing:
        return _fail("coverage-tokens", f"missing tokens: {missing}")
    return _ok("coverage-tokens", f"{len(REQUIRED_TOKENS)} closure tokens present")


def _normalise_link_target(raw: str) -> str | None:
    target = raw.strip()
    if not target or target.startswith("#"):
        return None
    lowered = target.lower()
    if lowered.startswith(("http://", "https://", "mailto:")):
        return None
    return target.split("#", 1)[0]


def _markdown_link_check(root: Path) -> CheckResult:
    path = root / CERTIFICATION
    if not path.is_file():
        return _fail("markdown-links", f"{CERTIFICATION.as_posix()} is missing")
    failures: list[str] = []
    for raw_target in MARKDOWN_LINK_RE.findall(_read(path)):
        target = _normalise_link_target(raw_target)
        if target is None:
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            failures.append(f"link escapes repo: {raw_target}")
            continue
        if not resolved.exists():
            failures.append(f"broken link: {raw_target}")
    if failures:
        return _fail("markdown-links", "; ".join(failures))
    return _ok("markdown-links", "local markdown links resolve")


def validate(root: Path = ROOT) -> CertificationReport:
    checks = (
        _certification_exists_check(root),
        _sections_check(root),
        _source_paths_check(root),
        _coverage_tokens_check(root),
        _markdown_link_check(root),
    )
    return CertificationReport(ready=all(check.ok for check in checks), checks=checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit non-zero when incomplete")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    args = parser.parse_args(argv)

    report = validate(args.root)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        for check in report.checks:
            status = "ok" if check.ok else "fail"
            print(f"{status}: {check.name}: {check.detail}")
        print(f"ready: {'yes' if report.ready else 'no'}")

    if args.check and not report.ready:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

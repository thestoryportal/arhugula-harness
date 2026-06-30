#!/usr/bin/env python3
"""Provider-free documentation completeness gate for R-CL-D1."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_MATRIX = Path(".harness/r-cl-d1-docs-completeness.md")
REQUIRED_DOCS: tuple[Path, ...] = (
    Path("docs/README.md"),
    Path("docs/tutorial-first-workflow.md"),
    Path("docs/how-to-operate-runtime.md"),
    Path("docs/how-to-deploy.md"),
    Path("docs/reference.md"),
    Path("docs/architecture.md"),
)
GROUNDING_HEADING = "## Source Grounding"
README_DOC_LINK = "docs/README.md"
REQUIRED_MATRIX_SOURCES: tuple[str, ...] = (
    "README.md",
    "examples/README.md",
    "harness.toml.example",
    "harness-runtime/src/harness_runtime/cli/app.py",
    "harness-runtime/src/harness_runtime/config_source.py",
    "harness-runtime/src/harness_runtime/types.py",
    "harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py",
    "deploy/self-hosted-local/README.md",
    "deploy/managed-cloud/README.md",
    "deploy/images/README.md",
    "tools/q4_packaging_gate.py",
    ".harness/roadmap_status.md",
)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class DocsReport:
    ready: bool
    checks: tuple[CheckResult, ...]


def _ok(name: str, detail: str) -> CheckResult:
    return CheckResult(name=name, ok=True, detail=detail)


def _fail(name: str, detail: str) -> CheckResult:
    return CheckResult(name=name, ok=False, detail=detail)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _required_docs_check(root: Path) -> CheckResult:
    missing = [path.as_posix() for path in REQUIRED_DOCS if not (root / path).is_file()]
    if missing:
        return _fail("required-docs", f"missing required docs: {missing}")
    return _ok("required-docs", f"{len(REQUIRED_DOCS)} required docs present")


def _readme_discovery_check(root: Path) -> CheckResult:
    readme = root / "README.md"
    if not readme.is_file():
        return _fail("readme-discovery", "README.md is missing")
    content = _read(readme)
    if README_DOC_LINK not in content:
        return _fail("readme-discovery", f"README.md must link to {README_DOC_LINK}")
    return _ok("readme-discovery", "README.md links to docs/README.md")


def _source_grounding_check(root: Path) -> CheckResult:
    missing = [
        path.as_posix()
        for path in REQUIRED_DOCS
        if (root / path).is_file() and GROUNDING_HEADING not in _read(root / path)
    ]
    if missing:
        return _fail("source-grounding", f"docs missing source grounding: {missing}")
    return _ok("source-grounding", "all required docs have source grounding sections")


def _evidence_matrix_check(root: Path) -> CheckResult:
    matrix_path = root / EVIDENCE_MATRIX
    if not matrix_path.is_file():
        return _fail("evidence-matrix", f"{EVIDENCE_MATRIX.as_posix()} is missing")
    content = _read(matrix_path)
    missing_sources = [source for source in REQUIRED_MATRIX_SOURCES if source not in content]
    required_sections = (
        "## Audience Coverage",
        "## Public Surface Coverage",
        "## Automated Completeness Gate",
        "## Operator Readthrough Checklist",
    )
    missing_sections = [section for section in required_sections if section not in content]
    if missing_sources or missing_sections:
        return _fail(
            "evidence-matrix",
            f"missing sources={missing_sources or 'none'} "
            f"missing sections={missing_sections or 'none'}",
        )
    return _ok("evidence-matrix", "D1 evidence matrix covers audiences and source paths")


def _normalise_link_target(raw: str) -> str | None:
    target = raw.strip()
    if not target or target.startswith("#"):
        return None
    lowered = target.lower()
    if lowered.startswith(("http://", "https://", "mailto:")):
        return None
    return target.split("#", 1)[0]


def _markdown_link_check(root: Path) -> CheckResult:
    checked_files = (Path("README.md"), EVIDENCE_MATRIX, *REQUIRED_DOCS)
    failures: list[str] = []
    for relative_file in checked_files:
        path = root / relative_file
        if not path.is_file():
            continue
        for raw_target in MARKDOWN_LINK_RE.findall(_read(path)):
            target = _normalise_link_target(raw_target)
            if target is None:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                failures.append(f"{relative_file.as_posix()}: link escapes repo: {raw_target}")
                continue
            if not resolved.exists():
                failures.append(f"{relative_file.as_posix()}: broken link: {raw_target}")
    if failures:
        return _fail("markdown-links", "; ".join(failures))
    return _ok("markdown-links", f"local markdown links resolve in {len(checked_files)} files")


def validate(root: Path = ROOT) -> DocsReport:
    checks = (
        _required_docs_check(root),
        _readme_discovery_check(root),
        _source_grounding_check(root),
        _evidence_matrix_check(root),
        _markdown_link_check(root),
    )
    return DocsReport(ready=all(check.ok for check in checks), checks=checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero when docs are incomplete",
    )
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

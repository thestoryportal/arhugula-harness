#!/usr/bin/env python3
"""Provider-free U-MEM-25/C-MEM-20 memory closeout evidence checker."""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN_DIR = Path("design" + "-substrate")
PRD = DESIGN_DIR / "PRD_v1_2.md"
SPEC = DESIGN_DIR / ("Spec" + "_Memory_Substrate_v1.md")
MEMORY_DOC = Path("docs/memory-substrate.md")
DOCS_INDEX = Path("docs/README.md")
EVIDENCE_PACKET = Path(".harness/u-mem-25-memory-closeout-evidence.md")
MATRIX_SOURCE = Path("harness-runtime/src/harness_runtime/memory_verification_suite.py")

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
R_MEM_HEADING_RE = re.compile(r"^###\s+(R-MEM-\d{2})\b", re.MULTILINE)
C_MEM_HEADING_RE = re.compile(r"^##\s+(C-MEM-\d{2})\b", re.MULTILINE)


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class MemoryCloseoutReport:
    ready: bool
    checks: tuple[CheckResult, ...]


def _ok(name: str, detail: str) -> CheckResult:
    return CheckResult(name=name, ok=True, detail=detail)


def _fail(name: str, detail: str) -> CheckResult:
    return CheckResult(name=name, ok=False, detail=detail)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _ids_from_headings(
    root: Path, relative_path: Path, pattern: re.Pattern[str]
) -> tuple[str, ...]:
    content = _read(root / relative_path)
    return tuple(dict.fromkeys(pattern.findall(content)))


def r_mem_ids(root: Path = ROOT) -> tuple[str, ...]:
    """Return R-MEM ids from the memory PRD source of truth."""

    return _ids_from_headings(root, PRD, R_MEM_HEADING_RE)


def c_mem_ids(root: Path = ROOT) -> tuple[str, ...]:
    """Return C-MEM ids from the memory substrate spec source of truth."""

    return _ids_from_headings(root, SPEC, C_MEM_HEADING_RE)


def _normalise_link_target(raw: str) -> str | None:
    target = raw.strip()
    if not target or target.startswith("#"):
        return None
    lowered = target.lower()
    if lowered.startswith(("http://", "https://", "mailto:")):
        return None
    return target.split("#", 1)[0]


def validate_markdown_links(root: Path, paths: tuple[Path, ...]) -> None:
    """Raise AssertionError when a checked local markdown link is broken."""

    failures: list[str] = []
    resolved_root = root.resolve()
    for relative_file in paths:
        path = root / relative_file
        if not path.is_file():
            failures.append(f"{relative_file.as_posix()}: file is missing")
            continue
        for raw_target in MARKDOWN_LINK_RE.findall(_read(path)):
            target = _normalise_link_target(raw_target)
            if target is None:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(resolved_root)
            except ValueError:
                failures.append(f"{relative_file.as_posix()}: link escapes repo: {raw_target}")
                continue
            if not resolved.exists():
                failures.append(f"{relative_file.as_posix()}: broken link: {raw_target}")
    if failures:
        raise AssertionError("; ".join(failures))


def _required_files_check(root: Path) -> CheckResult:
    required = (PRD, SPEC, MEMORY_DOC, DOCS_INDEX, EVIDENCE_PACKET, MATRIX_SOURCE)
    missing = [path.as_posix() for path in required if not (root / path).is_file()]
    if missing:
        return _fail("required-files", f"missing required files: {missing}")
    return _ok("required-files", f"{len(required)} required files present")


def _docs_index_check(root: Path) -> CheckResult:
    content = _read(root / DOCS_INDEX)
    if "memory-substrate.md" not in content:
        return _fail("docs-index", "docs/README.md must link to docs/memory-substrate.md")
    return _ok("docs-index", "docs/README.md links to docs/memory-substrate.md")


def _memory_doc_sections_check(root: Path) -> CheckResult:
    content = _read(root / MEMORY_DOC)
    required_sections = (
        "## Operator Policy Guide",
        "## Maintainer Architecture Notes",
        "## Migration Notes",
        "## Source Grounding",
    )
    missing = [section for section in required_sections if section not in content]
    if missing:
        return _fail("memory-doc-sections", f"missing sections: {missing}")
    return _ok(
        "memory-doc-sections", "operator, maintainer, migration, and grounding sections present"
    )


def _evidence_sections_check(root: Path) -> CheckResult:
    content = _read(root / EVIDENCE_PACKET)
    required_sections = (
        "## R-MEM Closeout Matrix",
        "## C-MEM Closeout Matrix",
        "## Review Evidence",
        "## Remaining Gates And Blockers",
    )
    missing = [section for section in required_sections if section not in content]
    if missing:
        return _fail("evidence-sections", f"missing sections: {missing}")
    return _ok("evidence-sections", "R-MEM, C-MEM, review, and blocker sections present")


def _id_coverage_check(root: Path) -> CheckResult:
    content = _read(root / EVIDENCE_PACKET)
    missing_r = [memory_id for memory_id in r_mem_ids(root) if memory_id not in content]
    missing_c = [contract_id for contract_id in c_mem_ids(root) if contract_id not in content]
    if missing_r or missing_c:
        return _fail(
            "id-coverage", f"missing R-MEM={missing_r or 'none'} C-MEM={missing_c or 'none'}"
        )
    return _ok("id-coverage", "all R-MEM and C-MEM ids are mapped in the evidence packet")


def _evidence_tokens_check(root: Path) -> CheckResult:
    content = _read(root / EVIDENCE_PACKET)
    required_tokens = (
        "harness-runtime/src/harness_runtime/memory_verification_suite.py",
        "LIVE_CREDENTIAL_GATES",
        "tools/memory_closeout_check.py",
        "just memory-closeout-check",
        "just codex-review",
    )
    missing = [token for token in required_tokens if token not in content]
    if missing:
        return _fail("evidence-tokens", f"missing required evidence tokens: {missing}")
    return _ok("evidence-tokens", "implementation, live-gate, checker, and review tokens present")


def _markdown_links_check(root: Path) -> CheckResult:
    try:
        validate_markdown_links(root, (DOCS_INDEX, MEMORY_DOC, EVIDENCE_PACKET))
    except AssertionError as exc:
        return _fail("markdown-links", str(exc))
    return _ok("markdown-links", "local markdown links resolve in memory docs and evidence")


def validate(root: Path = ROOT) -> MemoryCloseoutReport:
    checks = (
        _required_files_check(root),
        _docs_index_check(root),
        _memory_doc_sections_check(root),
        _evidence_sections_check(root),
        _id_coverage_check(root),
        _evidence_tokens_check(root),
        _markdown_links_check(root),
    )
    return MemoryCloseoutReport(ready=all(check.ok for check in checks), checks=checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="exit non-zero when closeout evidence is incomplete"
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

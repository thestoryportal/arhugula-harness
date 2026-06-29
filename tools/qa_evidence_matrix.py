#!/usr/bin/env python3
"""Q3 evidence matrix for contract and CXA closure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPT_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_SCRIPT_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_REPO_ROOT))

from tools.semantic_overlay import overlay  # noqa: E402

REPO_ROOT = overlay.REPO_ROOT
DEFAULT_REPORT = REPO_ROOT / ".harness" / "r-cl-q3-qa-evidence-matrix.md"


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _iter_test_files() -> list[Path]:
    files: list[Path] = []
    for package in overlay.PACKAGES:
        tests_dir = REPO_ROOT / package / "tests"
        if tests_dir.is_dir():
            files.extend(sorted(tests_dir.rglob("test_*.py")))
    files.extend(sorted((REPO_ROOT / "tools").glob("test_*.py")))
    return files


def _test_contract_index() -> dict[str, list[str]]:
    index: dict[str, set[str]] = {}
    for path in _iter_test_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for contract_id in overlay.RE_CONTRACT.findall(text):
            index.setdefault(contract_id, set()).add(_rel(path))
    return {key: sorted(value) for key, value in sorted(index.items())}


def _canonical_contract_files(graph: dict[str, Any]) -> dict[str, list[str]]:
    head_files = overlay.canonical_head_md_files()
    keyspace = graph["indices"]["spec_contract_to_files"]
    return {
        contract_id: sorted(files)
        for contract_id, files in sorted(keyspace.items())
        if any(path in head_files for path in files)
    }


def _source_files_for(graph: dict[str, Any], contract_id: str) -> list[str]:
    return [
        file_id.removeprefix("file:")
        for file_id in graph["indices"]["contract_to_files"].get(contract_id, [])
    ]


def derive_matrix() -> dict[str, Any]:
    graph = overlay.derive()
    tests_by_contract = _test_contract_index()
    contracts = []
    for contract_id, declaration_files in _canonical_contract_files(graph).items():
        contracts.append(
            {
                "contract_id": contract_id,
                "declaration_files": declaration_files,
                "source_files": _source_files_for(graph, contract_id),
                "test_files": tests_by_contract.get(contract_id, []),
            }
        )

    return {
        "contracts": contracts,
        "cxa": {
            "total": graph["stats"]["cxa_seams_total"],
            "wired": graph["stats"]["cxa_seams_wired"],
            "missing": graph["orphans"]["cxa_seam_missing_endpoint"],
        },
    }


def summary(matrix: dict[str, Any]) -> dict[str, int]:
    contracts = matrix["contracts"]
    missing = [row for row in contracts if not row["test_files"]]
    cxa = matrix["cxa"]
    return {
        "contracts_total": len(contracts),
        "contracts_with_test_evidence": len(contracts) - len(missing),
        "contracts_missing_test_evidence": len(missing),
        "cxa_seams_total": int(cxa["total"]),
        "cxa_seams_wired": int(cxa["wired"]),
        "cxa_seams_missing_endpoint": len(cxa["missing"]),
    }


def violations(matrix: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for row in matrix["contracts"]:
        if not row["test_files"]:
            out.append(f"{row['contract_id']} has no test proof")
    for missing in matrix["cxa"]["missing"]:
        out.append(f"{missing['edge_label']} has a missing CXA endpoint")
    return out


def render_markdown(matrix: dict[str, Any]) -> str:
    stats = summary(matrix)
    lines = [
        "# R-CL-Q3 QA Evidence Matrix",
        "",
        "Status: evidence for `.harness/audit/Closure_Gate_v1.md` G2.3.",
        "",
        "## Summary",
        "",
        "| Predicate | Value |",
        "| --- | ---: |",
        "| Contracts with test proof | "
        f"{stats['contracts_with_test_evidence']}/{stats['contracts_total']} |",
        f"| Contracts missing test proof | {stats['contracts_missing_test_evidence']} |",
        f"| CXA seams wired | {stats['cxa_seams_wired']}/{stats['cxa_seams_total']} |",
        f"| CXA seams missing endpoint | {stats['cxa_seams_missing_endpoint']} |",
        "",
        "## Product Probes",
        "",
        "| Tier | Probe | Evidence |",
        "| --- | --- | --- |",
        "| In-process | Track B runtime flow | "
        "`harness-runtime/tests/integration/test_track_b_e2e.py` |",
        "| Local API/tool | R100 AC2 tool-step E2E | "
        "`harness-runtime/tests/integration/test_r100_ac2_tool_step_e2e.py` |",
        "| Live substrate | Environment-gated smoke path | "
        "`harness-runtime/tests/integration/test_r_cl_p3_live_multi_tier_e2e.py` |",
        "",
        "## Contract Evidence",
        "",
        "| Contract | Source carriers | Test proofs | First proof |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in matrix["contracts"]:
        first_proof = row["test_files"][0] if row["test_files"] else "MISSING"
        lines.append(
            f"| {row['contract_id']} | {len(row['source_files'])} | "
            f"{len(row['test_files'])} | `{first_proof}` |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when required proof is missing")
    parser.add_argument("--json", action="store_true", help="print the matrix as JSON")
    parser.add_argument(
        "--write-report",
        nargs="?",
        const=str(DEFAULT_REPORT),
        help="write the markdown report, optionally to a custom path",
    )
    args = parser.parse_args(argv)

    matrix = derive_matrix()

    if args.write_report:
        report = Path(args.write_report)
        report.write_text(render_markdown(matrix), encoding="utf-8")
        print(f"wrote {_rel(report)}")

    if args.json:
        print(json.dumps(matrix, indent=2))

    failures = violations(matrix)
    if args.check and failures:
        print("Q3 evidence gaps:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    stats = summary(matrix)
    print(
        "q3 evidence OK "
        f"contracts={stats['contracts_with_test_evidence']}/{stats['contracts_total']} "
        f"cxa={stats['cxa_seams_wired']}/{stats['cxa_seams_total']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

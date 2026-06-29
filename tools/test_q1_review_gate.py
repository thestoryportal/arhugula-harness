from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import q1_review_gate


def _lane(name: str, findings: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "lane": name,
        "status": "passed",
        "findings": findings or [],
        "notes": f"{name} pass complete",
    }


def _report() -> dict[str, Any]:
    return {
        "phase": "R-CL-Q1",
        "generated_at": "2026-06-29T06:00:00+00:00",
        "packages": [
            {
                "package": package,
                "lanes": [
                    _lane("codex"),
                    _lane("code_review"),
                    _lane("simplify"),
                ],
            }
            for package in q1_review_gate.REQUIRED_PACKAGES
        ],
        "non_package_surfaces": [
            {
                "surface": surface,
                "lanes": [
                    _lane("codex"),
                    _lane("code_review"),
                    _lane("simplify"),
                ],
            }
            for surface in q1_review_gate.REQUIRED_NON_PACKAGE_SURFACES
        ],
        "clean_checkout_walkthrough": {
            "status": "passed",
            "commands": ["git clean checkout smoke", "just check"],
            "notes": "fresh checkout reached green",
        },
        "verification_commands": [
            {
                "command": "just check",
                "status": "passed",
                "notes": "fixed point green",
            }
        ],
    }


def test_complete_q1_report_has_no_violations() -> None:
    report = q1_review_gate.Q1ReviewReport.model_validate(_report())

    assert q1_review_gate.validate_report(report) == []


def test_missing_required_review_lane_is_a_violation() -> None:
    raw = _report()
    raw["packages"][0]["lanes"] = [_lane("codex"), _lane("simplify")]
    report = q1_review_gate.Q1ReviewReport.model_validate(raw)

    violations = q1_review_gate.validate_report(report)

    assert any("missing lanes" in violation for violation in violations)
    assert any("code_review" in violation for violation in violations)


def test_missing_required_non_package_surface_is_a_violation() -> None:
    raw = _report()
    raw["non_package_surfaces"] = [
        {
            "surface": "tools/",
            "lanes": [_lane("codex"), _lane("code_review"), _lane("simplify")],
        }
    ]
    report = q1_review_gate.Q1ReviewReport.model_validate(raw)

    violations = q1_review_gate.validate_report(report)

    assert any("missing non-package surfaces" in violation for violation in violations)
    assert any("justfile" in violation for violation in violations)
    assert any("harness.toml.example" in violation for violation in violations)


def test_open_finding_is_a_violation() -> None:
    raw = _report()
    raw["packages"][1]["lanes"][0]["findings"] = [
        {
            "id": "Q1-CORE-001",
            "severity": "important",
            "status": "open",
            "path": "harness-core/src/harness_core/types.py",
            "line": 12,
            "summary": "Open review finding",
            "recommendation": "Close the finding before Q1 sign-off.",
        }
    ]
    report = q1_review_gate.Q1ReviewReport.model_validate(raw)

    violations = q1_review_gate.validate_report(report)

    assert violations == ["harness-is/codex/Q1-CORE-001 remains open"]


def test_risk_accepted_finding_is_not_closed_for_q1() -> None:
    raw = _report()
    raw["packages"][2]["lanes"][1]["findings"] = [
        {
            "id": "Q1-AS-001",
            "severity": "minor",
            "status": "risk_accepted",
            "path": "harness-as/src/harness_as/skills.py",
            "summary": "Accepted residual without evidence",
            "recommendation": "Record the acceptance evidence.",
            "evidence": "accepted by reviewer",
        }
    ]
    report = q1_review_gate.Q1ReviewReport.model_validate(raw)

    violations = q1_review_gate.validate_report(report)

    assert violations == ["harness-as/code_review/Q1-AS-001 risk_accepted is not closed for Q1"]


def test_failed_devex_walkthrough_or_missing_just_check_is_a_violation() -> None:
    raw = _report()
    raw["clean_checkout_walkthrough"]["status"] = "failed"
    raw["verification_commands"] = [
        {"command": "just codex-check", "status": "passed", "notes": "provider-free green"}
    ]
    report = q1_review_gate.Q1ReviewReport.model_validate(raw)

    violations = q1_review_gate.validate_report(report)

    assert "clean checkout walkthrough is failed" in violations
    assert "missing passing `just check` verification command" in violations


def test_non_passing_verification_command_is_a_violation() -> None:
    raw = _report()
    raw["verification_commands"].append(
        {"command": "important gate", "status": "blocked", "notes": "not done"}
    )
    report = q1_review_gate.Q1ReviewReport.model_validate(raw)

    violations = q1_review_gate.validate_report(report)

    assert "non-passing verification commands: important gate (blocked)" in violations


def test_cli_check_returns_nonzero_for_invalid_report(tmp_path: Path) -> None:
    raw = _report()
    raw["packages"].pop()
    report_path = tmp_path / "q1-review.json"
    report_path.write_text(json.dumps(raw), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, "tools/q1_review_gate.py", "--check", str(report_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 1
    assert "missing packages" in proc.stderr


def test_cli_schema_exports_machine_readable_schema() -> None:
    proc = subprocess.run(
        [sys.executable, "tools/q1_review_gate.py", "--schema"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0
    schema = json.loads(proc.stdout)
    assert schema["title"] == "Q1ReviewReport"

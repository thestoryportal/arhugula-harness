#!/usr/bin/env python3
"""R-CL-Q1 structured review artifact gate.

This is the provider-free half of the Q1 review/simplification sweep: it checks
that a typed review artifact contains every required package + review lane, no
open findings, required tooling/root-file surfaces, a clean-checkout DevEx
walkthrough, and a passing `just check`.
The artifact may be produced by humans, `/code-review`, `/simplify`, Codex, or a
future Instructor-backed generator; this script only validates the result.

Usage:
    python tools/q1_review_gate.py --schema
    python tools/q1_review_gate.py --check .harness/r-cl-q1-review.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError

REQUIRED_PACKAGES: tuple[
    Literal[
        "harness-core",
        "harness-is",
        "harness-as",
        "harness-cp",
        "harness-od",
        "harness-cxa",
        "harness-runtime",
    ],
    ...,
] = (
    "harness-core",
    "harness-is",
    "harness-as",
    "harness-cp",
    "harness-od",
    "harness-cxa",
    "harness-runtime",
)

REQUIRED_LANES: tuple[Literal["codex", "code_review", "simplify"], ...] = (
    "codex",
    "code_review",
    "simplify",
)

REQUIRED_NON_PACKAGE_SURFACES: tuple[
    Literal["tools/", "justfile", "harness.toml.example"],
    ...,
] = (
    "tools/",
    "justfile",
    "harness.toml.example",
)

PackageName = Literal[
    "harness-core",
    "harness-is",
    "harness-as",
    "harness-cp",
    "harness-od",
    "harness-cxa",
    "harness-runtime",
]
LaneName = Literal["codex", "code_review", "simplify"]
NonPackageSurfaceName = Literal["tools/", "justfile", "harness.toml.example"]
FindingSeverity = Literal["critical", "important", "minor"]
FindingStatus = Literal["open", "fixed", "risk_accepted"]
GateStatus = Literal["passed", "failed", "skipped", "blocked"]


class ReviewFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    severity: FindingSeverity
    status: FindingStatus
    path: str
    line: int | None = None
    summary: str
    recommendation: str
    evidence: str | None = None


class ReviewLane(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    lane: LaneName
    status: Literal["passed", "blocked"]
    findings: tuple[ReviewFinding, ...] = ()
    notes: str


class PackageReview(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    package: PackageName
    lanes: tuple[ReviewLane, ...]


class NonPackageSurfaceReview(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    surface: NonPackageSurfaceName
    lanes: tuple[ReviewLane, ...]


class CleanCheckoutWalkthrough(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["passed", "failed"]
    commands: tuple[str, ...]
    notes: str


class VerificationCommand(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    command: str
    status: GateStatus
    notes: str


class Q1ReviewReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    phase: Literal["R-CL-Q1"]
    generated_at: str
    packages: tuple[PackageReview, ...]
    non_package_surfaces: tuple[NonPackageSurfaceReview, ...]
    clean_checkout_walkthrough: CleanCheckoutWalkthrough
    verification_commands: tuple[VerificationCommand, ...]


def _join(values: Iterable[str]) -> str:
    return ", ".join(sorted(values))


def _validate_lanes(scope: str, lanes: tuple[ReviewLane, ...]) -> list[str]:
    violations: list[str] = []
    lane_reviews: dict[str, ReviewLane] = {}
    duplicate_lanes: set[str] = set()
    for lane_review in lanes:
        if lane_review.lane in lane_reviews:
            duplicate_lanes.add(lane_review.lane)
        lane_reviews[lane_review.lane] = lane_review

    if duplicate_lanes:
        violations.append(f"{scope}: duplicate lanes: {_join(duplicate_lanes)}")

    missing_lanes = set(REQUIRED_LANES) - set(lane_reviews)
    if missing_lanes:
        violations.append(f"{scope}: missing lanes: {_join(missing_lanes)}")

    for lane_review in lanes:
        if lane_review.status != "passed":
            violations.append(f"{scope}/{lane_review.lane} lane is {lane_review.status}")

        for finding in lane_review.findings:
            prefix = f"{scope}/{lane_review.lane}/{finding.id}"
            if finding.status == "open":
                violations.append(f"{prefix} remains open")
            elif finding.status == "risk_accepted":
                violations.append(f"{prefix} risk_accepted is not closed for Q1")

    return violations


def validate_report(report: Q1ReviewReport) -> list[str]:
    """Return semantic violations for a structurally valid Q1 review artifact."""
    violations: list[str] = []

    package_reviews: dict[str, PackageReview] = {}
    duplicate_packages: set[str] = set()
    for package_review in report.packages:
        if package_review.package in package_reviews:
            duplicate_packages.add(package_review.package)
        package_reviews[package_review.package] = package_review

    if duplicate_packages:
        violations.append(f"duplicate packages: {_join(duplicate_packages)}")

    missing_packages = set(REQUIRED_PACKAGES) - set(package_reviews)
    if missing_packages:
        violations.append(f"missing packages: {_join(missing_packages)}")

    for package in REQUIRED_PACKAGES:
        package_review = package_reviews.get(package)
        if package_review is None:
            continue

        violations.extend(_validate_lanes(package, package_review.lanes))

    surface_reviews: dict[str, NonPackageSurfaceReview] = {}
    duplicate_surfaces: set[str] = set()
    for surface_review in report.non_package_surfaces:
        if surface_review.surface in surface_reviews:
            duplicate_surfaces.add(surface_review.surface)
        surface_reviews[surface_review.surface] = surface_review

    if duplicate_surfaces:
        violations.append(f"duplicate non-package surfaces: {_join(duplicate_surfaces)}")

    missing_surfaces = set(REQUIRED_NON_PACKAGE_SURFACES) - set(surface_reviews)
    if missing_surfaces:
        violations.append(f"missing non-package surfaces: {_join(missing_surfaces)}")

    for surface in REQUIRED_NON_PACKAGE_SURFACES:
        surface_review = surface_reviews.get(surface)
        if surface_review is None:
            continue

        violations.extend(_validate_lanes(surface, surface_review.lanes))

    if report.clean_checkout_walkthrough.status != "passed":
        status = report.clean_checkout_walkthrough.status
        violations.append(f"clean checkout walkthrough is {status}")
    if not report.clean_checkout_walkthrough.commands:
        violations.append("clean checkout walkthrough has no commands")

    non_passing = [
        f"{command.command} ({command.status})"
        for command in report.verification_commands
        if command.status != "passed"
    ]
    if non_passing:
        violations.append(f"non-passing verification commands: {', '.join(non_passing)}")

    has_just_check = any(
        command.command.strip() == "just check" and command.status == "passed"
        for command in report.verification_commands
    )
    if not has_just_check:
        violations.append("missing passing `just check` verification command")

    return violations


def load_report(path: Path) -> Q1ReviewReport:
    return Q1ReviewReport.model_validate_json(path.read_text(encoding="utf-8"))


def check_report(path: Path) -> int:
    try:
        report = load_report(path)
    except (OSError, ValidationError) as exc:
        print(f"Q1 REVIEW GATE INVALID: {exc}", file=sys.stderr)
        return 1

    violations = validate_report(report)
    if violations:
        print("Q1 REVIEW GATE FAILED:", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        return 1

    print(
        "Q1 review gate OK — "
        f"{len(report.packages)} packages, "
        f"{len(report.non_package_surfaces)} non-package surfaces, "
        f"{len(REQUIRED_LANES)} required lanes, "
        "no open findings"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an R-CL-Q1 structured review artifact.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--schema", action="store_true", help="print the JSON schema")
    action.add_argument("--check", type=Path, metavar="PATH", help="validate a report artifact")
    args = parser.parse_args(argv)

    if args.schema:
        print(json.dumps(Q1ReviewReport.model_json_schema(), indent=2, sort_keys=True))
        return 0

    return check_report(args.check)


if __name__ == "__main__":
    raise SystemExit(main())

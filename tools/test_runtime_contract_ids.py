"""Regression tests for runtime spec contract identifier hygiene."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SPEC = ROOT / "design-substrate" / "Spec_Harness_Runtime_v1.md"

CONTRACT_HEADING_RE = re.compile(
    r"^##\s+§(?P<section>\d+(?:\.\d+)*)\b.*?\b(?P<contract>C-RT-\d+)\b(?P<title>.*)$"
)
AMENDMENT_ONLY_MARKERS = (
    "field table",
    "NEW row",
)


def _top_level_runtime_contract_headings() -> dict[str, list[str]]:
    by_contract: dict[str, list[str]] = defaultdict(list)
    for line_no, line in enumerate(RUNTIME_SPEC.read_text().splitlines(), start=1):
        match = CONTRACT_HEADING_RE.match(line)
        if match is None:
            continue
        if any(marker in line for marker in AMENDMENT_ONLY_MARKERS):
            continue
        by_contract[match.group("contract")].append(
            f"line {line_no}: §{match.group('section')} {match.group('title').strip()}"
        )
    return by_contract


def test_runtime_contract_ids_are_unique_for_top_level_surfaces() -> None:
    """A C-RT identifier must name exactly one top-level runtime contract surface."""

    duplicates = {
        contract: locations
        for contract, locations in _top_level_runtime_contract_headings().items()
        if len(locations) > 1
    }

    assert duplicates == {}, "\n".join(
        f"{contract} is assigned to: {', '.join(locations)}"
        for contract, locations in sorted(duplicates.items())
    )

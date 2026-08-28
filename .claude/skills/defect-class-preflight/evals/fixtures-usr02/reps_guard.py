"""Launch-admission guard for the reviewer wrapper.

Enforces the round budget and validates the launch arguments before any reviewer
call is spent. The governing contract excerpt is in `contract_excerpt.md`
alongside this file.
"""

from __future__ import annotations

import argparse
import os


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="review-launch")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument(
        "--round",
        type=int,
    )
    ap.add_argument("--lane-id", type=str)
    return ap


def validate(args: argparse.Namespace) -> str | None:
    """Return a refusal reason, or None when the launch is admissible."""
    if not 1 <= args.reps <= 99:
        return "reps out of range"
    if args.round is not None and args.round > 25:
        return "BUDGET_EXHAUSTED"
    if args.lane_id is not None and len(args.lane_id) > 128:
        return "lane id too long"
    return None


def admit(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    reason = validate(args)
    if reason is not None:
        return 1
    if args.reps > 1 and os.environ.get("REVIEWER_PROBE") != "1":
        return 1
    return 0

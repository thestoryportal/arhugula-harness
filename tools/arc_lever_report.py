"""Cohort report: skill-lever treated arcs vs the untreated baseline (B-211/B-212).

Reads the committed arc-metrics ledger and, PER ARC TYPE (mixing inventing and
applying arcs compares arcs that were never comparable — codex r1 on this
tool), splits rows into a TREATED cohort (rows declaring at least one target
lever id in ``levers_active``) and the BASELINE cohort (rows declaring the
empty lever set — a claim in itself, per B-170: it says no lever was live).
Rows declaring only *other* levers belong to neither cohort and are reported
as excluded, never silently dropped.

Two further exclusions, both loud (B-170: a lever must never be evaluated
against a row that was not fully measured):
- ``review_rounds`` null — an honest could-not-look, not a measured zero;
- ``round_completeness`` != "complete" — a partial suffix is a lower bound
  whose unknown P1 count would otherwise read as a measured zero.

Per-skill attribution: separability is judged on the rows' intersections with
the TARGET lever set only — a stray extra lever id on an otherwise-identical
treated row is not separation (codex r1). While every treated arc intersects
the targets identically, the report says the skills are not separable.
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = REPO / ".harness" / "arc-metrics.jsonl"
DEFAULT_LEVERS = ("B-211", "B-212")

_BUCKETS = ("treated", "baseline", "other_levers", "unmapped", "partial")


def load_rows(ledger: Path) -> list[dict[str, Any]]:
    """Parse the ledger, refusing silently-skipped rows (no-silent-failure)."""
    if not ledger.is_file():
        raise SystemExit(f"arc-lever-report: ledger not found: {ledger}")
    rows: list[dict[str, Any]] = []
    for n, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"arc-lever-report: {ledger}:{n} is not JSON: {exc}") from exc
    return rows


def split_cohorts(
    rows: list[dict[str, Any]], levers: tuple[str, ...]
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Pure per-arc-type cohort split: {arc_type: {bucket: rows}}."""
    out: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for r in rows:
        arc_type = r.get("arc_type") or "unclassified"
        buckets = out.setdefault(arc_type, {b: [] for b in _BUCKETS})
        declared = r.get("levers_active") or []
        bucket = (
            "treated"
            if any(lv in declared for lv in levers)
            else ("baseline" if declared == [] else "other_levers")
        )
        if r.get("review_rounds") is None:
            buckets["unmapped"].append(r)
        elif r.get("round_completeness") != "complete":
            # A partial suffix carries review_rounds as a LOWER BOUND and an
            # unknown P1 count; letting it into a median converts "unknown"
            # into a score (codex r1 on this tool).
            buckets["partial"].append(r)
        else:
            buckets[bucket].append(r)
    return out


def _metrics(r: dict[str, Any], levers: tuple[str, ...]) -> dict[str, Any]:
    span = r.get("arc_span_s")
    declared = r.get("levers_active") or []
    return {
        "arc_id": r.get("arc_id"),
        "review_rounds": r["review_rounds"],
        "p1_rounds": len(r.get("p1_rounds") or []),
        "arc_span_h": round(span / 3600, 1) if isinstance(span, (int, float)) else None,
        "levers": declared,
        "target_levers_declared": sorted(lv for lv in declared if lv in levers),
    }


def _median(values: list[float]) -> float | None:
    return round(statistics.median(values), 1) if values else None


def summarize_type(
    buckets: dict[str, list[dict[str, Any]]], levers: tuple[str, ...]
) -> dict[str, Any]:
    """Pure summary for one arc type — one JSON-able value."""
    treated = [_metrics(r, levers) for r in buckets["treated"]]
    baseline = [_metrics(r, levers) for r in buckets["baseline"]]
    base_median = {
        "review_rounds": _median([m["review_rounds"] for m in baseline]),
        "p1_rounds": _median([m["p1_rounds"] for m in baseline]),
        "arc_span_h": _median([m["arc_span_h"] for m in baseline if m["arc_span_h"] is not None]),
    }
    for m in treated:
        m["delta_rounds_vs_baseline_median"] = (
            round(m["review_rounds"] - base_median["review_rounds"], 1)
            if base_median["review_rounds"] is not None
            else None
        )
    # Separability judged ONLY on how treated rows intersect the target set:
    # an extra unrelated lever must not fake a per-skill split (codex r1).
    target_patterns = {tuple(m["target_levers_declared"]) for m in treated}
    return {
        "cohort_sizes": {k: len(v) for k, v in buckets.items()},
        "baseline_median": base_median,
        "treated_arcs": treated,
        "treated_median_rounds": _median([m["review_rounds"] for m in treated]),
        "per_skill_separable": len(target_patterns) > 1,
        "excluded_unmapped": [r.get("arc_id") for r in buckets["unmapped"]],
        "excluded_partial": [r.get("arc_id") for r in buckets["partial"]],
        "excluded_other_levers": [r.get("arc_id") for r in buckets["other_levers"]],
    }


def summarize(
    cohorts_by_type: dict[str, dict[str, list[dict[str, Any]]]], levers: tuple[str, ...]
) -> dict[str, Any]:
    return {
        "target_levers": list(levers),
        "arc_types": {t: summarize_type(b, levers) for t, b in sorted(cohorts_by_type.items())},
    }


def render(summary: dict[str, Any]) -> str:
    """Human view of the summary — the JSON is the authority, this a projection."""
    lines = [f"arc-lever-report — levers {', '.join(summary['target_levers'])} (per arc type)"]
    for arc_type, s in summary["arc_types"].items():
        sizes = s["cohort_sizes"]
        bm = s["baseline_median"]
        lines.append(
            f"[{arc_type}] {sizes['treated']} treated / {sizes['baseline']} baseline — "
            f"baseline median: rounds={bm['review_rounds']} p1={bm['p1_rounds']} "
            f"span_h={bm['arc_span_h']}"
        )
        if not s["treated_arcs"]:
            lines.append("  no treated arcs — declare the lever ids at arc-metrics queue time")
        for m in s["treated_arcs"]:
            lines.append(
                f"  {m['arc_id']} rounds={m['review_rounds']} p1={m['p1_rounds']} "
                f"span_h={m['arc_span_h']} "
                f"delta_rounds_vs_baseline={m['delta_rounds_vs_baseline_median']}"
            )
        lines.append(
            f"  treated median rounds: {s['treated_median_rounds']}"
            f" | per-skill separation: "
            + (
                "available (target-lever patterns diverge)"
                if s["per_skill_separable"]
                else "NOT separable — every treated arc declares the same target levers"
            )
        )
        for key, label in (
            ("excluded_unmapped", "unmapped rounds, B-170 — never evaluated"),
            ("excluded_partial", "partial round data — lower bounds, never evaluated"),
            ("excluded_other_levers", "other lever sets"),
        ):
            if s[key]:
                lines.append(f"  excluded ({label}): " + ", ".join(str(a) for a in s[key]))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument(
        "--levers",
        default=",".join(DEFAULT_LEVERS),
        help="comma-separated lever ids defining the treated cohort",
    )
    ap.add_argument(
        "--arc-type",
        choices=("inventing", "applying"),
        default=None,
        help="restrict the report to one arc type (the default reports each type separately)",
    )
    ap.add_argument("--json", action="store_true", help="emit the summary as JSON")
    args = ap.parse_args(argv)
    levers = tuple(t for t in (s.strip() for s in args.levers.split(",")) if t)
    if not levers:
        raise SystemExit("arc-lever-report: --levers must name at least one lever id")
    cohorts = split_cohorts(load_rows(args.ledger), levers)
    if args.arc_type is not None:
        cohorts = {t: b for t, b in cohorts.items() if t == args.arc_type}
    summary = summarize(cohorts, levers)
    print(json.dumps(summary, indent=2) if args.json else render(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

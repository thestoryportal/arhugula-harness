"""Cohort report: skill-lever treated arcs vs the untreated baseline (B-211/B-212).

Reads the committed arc-metrics ledger and splits rows into a TREATED cohort
(rows declaring at least one target lever id in ``levers_active``) and the
BASELINE cohort (rows declaring the empty lever set — a claim in itself, per
B-170: it says no lever was live). Rows declaring only *other* levers belong to
neither cohort and are reported as excluded, never silently dropped.

Rows whose round data is absent (``review_rounds`` null — an honest "could not
look", not a measured zero) are excluded from every median and listed loudly:
the B-170 rule is that a lever must never be evaluated against an unmapped row.

Per-skill attribution: while every treated arc declares the same lever set,
the cohorts cannot separate B-211 (defect-class-preflight) from B-212
(register-pr-prose) — the report says so instead of implying a split.
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
    rows: list[dict[str, Any]], levers: tuple[str, ...], arc_type: str | None
) -> dict[str, list[dict[str, Any]]]:
    """Pure cohort split. Keys: treated / baseline / other_levers / unmapped."""
    out: dict[str, list[dict[str, Any]]] = {
        "treated": [],
        "baseline": [],
        "other_levers": [],
        "unmapped": [],
    }
    for r in rows:
        if arc_type is not None and r.get("arc_type") != arc_type:
            continue
        declared = r.get("levers_active") or []
        bucket = (
            "treated"
            if any(lv in declared for lv in levers)
            else ("baseline" if declared == [] else "other_levers")
        )
        # Unmapped rounds disqualify a row from medians in ANY bucket (B-170):
        # an honest null is not a measurement, and evaluating a lever against it
        # would read "could not look" as a score.
        if r.get("review_rounds") is None:
            out["unmapped"].append(r)
        else:
            out[bucket].append(r)
    return out


def _metrics(r: dict[str, Any]) -> dict[str, Any]:
    span = r.get("arc_span_s")
    return {
        "arc_id": r.get("arc_id"),
        "arc_type": r.get("arc_type"),
        "review_rounds": r["review_rounds"],
        "p1_rounds": len(r.get("p1_rounds") or []),
        "arc_span_h": round(span / 3600, 1) if isinstance(span, (int, float)) else None,
        "levers": r.get("levers_active") or [],
    }


def _median(values: list[float]) -> float | None:
    return round(statistics.median(values), 1) if values else None


def summarize(cohorts: dict[str, list[dict[str, Any]]], levers: tuple[str, ...]) -> dict[str, Any]:
    """Pure summary over the split — the whole report as one JSON-able value."""
    treated = [_metrics(r) for r in cohorts["treated"]]
    baseline = [_metrics(r) for r in cohorts["baseline"]]
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
    treated_lever_sets = {tuple(sorted(m["levers"])) for m in treated}
    return {
        "target_levers": list(levers),
        "cohort_sizes": {k: len(v) for k, v in cohorts.items()},
        "baseline_median": base_median,
        "treated_arcs": treated,
        "treated_median_rounds": _median([m["review_rounds"] for m in treated]),
        "per_skill_separable": len(treated_lever_sets) > 1,
        "excluded_unmapped": [r.get("arc_id") for r in cohorts["unmapped"]],
        "excluded_other_levers": [r.get("arc_id") for r in cohorts["other_levers"]],
    }


def render(summary: dict[str, Any]) -> str:
    """Human view of the summary — the JSON is the authority, this a projection."""
    lines: list[str] = []
    sizes = summary["cohort_sizes"]
    lines.append(
        f"arc-lever-report — levers {', '.join(summary['target_levers'])}: "
        f"{sizes['treated']} treated / {sizes['baseline']} baseline"
    )
    bm = summary["baseline_median"]
    lines.append(
        f"baseline median: rounds={bm['review_rounds']} p1={bm['p1_rounds']} "
        f"span_h={bm['arc_span_h']}"
    )
    if not summary["treated_arcs"]:
        lines.append("no treated arcs yet — declare the lever ids at arc-metrics queue time")
    for m in summary["treated_arcs"]:
        lines.append(
            f"  {m['arc_id']} [{m['arc_type']}] rounds={m['review_rounds']} "
            f"p1={m['p1_rounds']} span_h={m['arc_span_h']} "
            f"delta_rounds_vs_baseline={m['delta_rounds_vs_baseline_median']}"
        )
    lines.append(
        f"treated median rounds: {summary['treated_median_rounds']}"
        f" | per-skill separation: "
        + (
            "available (lever sets diverge)"
            if summary["per_skill_separable"]
            else "NOT separable — every treated arc declares the same lever set"
        )
    )
    if summary["excluded_unmapped"]:
        lines.append(
            "excluded (unmapped rounds, B-170 — never evaluated): "
            + ", ".join(str(a) for a in summary["excluded_unmapped"])
        )
    if summary["excluded_other_levers"]:
        lines.append(
            "excluded (other lever sets): "
            + ", ".join(str(a) for a in summary["excluded_other_levers"])
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument(
        "--levers",
        default=",".join(DEFAULT_LEVERS),
        help="comma-separated lever ids defining the treated cohort",
    )
    ap.add_argument("--arc-type", choices=("inventing", "applying"), default=None)
    ap.add_argument("--json", action="store_true", help="emit the summary as JSON")
    args = ap.parse_args(argv)
    levers = tuple(t for t in (s.strip() for s in args.levers.split(",")) if t)
    if not levers:
        raise SystemExit("arc-lever-report: --levers must name at least one lever id")
    summary = summarize(split_cohorts(load_rows(args.ledger), levers, args.arc_type), levers)
    print(json.dumps(summary, indent=2) if args.json else render(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

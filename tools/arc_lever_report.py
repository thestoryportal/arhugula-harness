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

Per-skill attribution: separability requires a single-lever contrast on the
FULL declared lever sets — two evaluable rows whose complete declarations
differ in exactly one target lever (codex r1-r7). A stray non-target lever
changing simultaneously confounds the pair; while no such contrast exists,
the report says the skills are not separable.
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

REPO = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = REPO / ".harness" / "arc-metrics.jsonl"
DEFAULT_LEVERS = ("B-211", "B-212")

_BUCKETS = ("treated", "baseline", "other_levers", "unmapped", "partial", "undeclared")


class LedgerRow(BaseModel):
    """Typed boundary for the arc-metrics ledger (parse-don't-validate, codex r12).

    Defaults encode the producer's legacy semantics (`ArcRow` at
    tools/arc_metrics.py): a field ABSENT on a pre-C-HE-25 row is legal legacy
    shape — ``round_completeness`` absent means complete, ``levers_active``
    absent means no claim — while an EXPLICIT null keeps its own downstream
    meaning, so the absent-vs-null distinction lives in the type, not in
    presence checks. Extra fields are additive C-HE-25 evolution this report
    never reads; any other illegal shape (missing ``arc_id``, a non-arc
    ``record_kind``, a mistyped field) is refused ONCE, here, instead of
    flowing anonymously into a cohort median.

    Strict mode, not lax (codex r13): a coerced ``review_rounds="3"`` or
    ``p1_rounds=["1"]`` would enter a median as a genuine measurement the
    producer never took, and a negative round/span count is no measurement at
    all — the producer only writes real non-negative numbers, so the type
    says exactly that. The one lossless coercion kept is int→float for
    ``arc_span_s`` (pydantic's strict float admits ints by design).
    """

    model_config = ConfigDict(extra="ignore", strict=True)

    arc_id: str
    record_kind: Literal["arc"] = "arc"
    arc_type: str | None = None
    arc_type_declared_at: str | None = None
    levers_active: list[str] | None = None
    review_rounds: int | None = Field(default=None, ge=0)
    round_completeness: str | None = "complete"
    p1_rounds: list[Annotated[int, Field(ge=0)]] | None = None
    arc_span_s: float | None = Field(default=None, ge=0)
    # C-HE-25 v1.6 X6e: requestId-deduplicated transcript cost (absent = never measured)
    cost_main_iet: float | None = Field(default=None, ge=0)
    cost_subagent_iet: float | None = Field(default=None, ge=0)


def load_rows(ledger: Path) -> list[LedgerRow]:
    """Parse the ledger, refusing silently-skipped rows (no-silent-failure)."""
    if not ledger.is_file():
        raise SystemExit(f"arc-lever-report: ledger not found: {ledger}")
    rows: list[LedgerRow] = []
    for n, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"arc-lever-report: {ledger}:{n} is not JSON: {exc}") from exc
        try:
            rows.append(LedgerRow.model_validate(obj))
        except ValidationError as exc:
            raise SystemExit(f"arc-lever-report: {ledger}:{n} illegal row shape: {exc}") from exc
    return rows


def _non_evaluable_reason(arc_type: str, contaminated: bool) -> str | None:
    """The C-HE-26 reason a group cannot support the lever decision, as DATA.

    Computed once, where the discriminators are known, and carried on the
    group — the human render must never re-derive the cause from the key
    string (codex r6) and must never misname it: an open-declared unknown
    type is neither close-declared nor untyped (codex r12).
    """
    if contaminated:
        return "close-declared (outcome-contaminated, C-HE-26)"
    if arc_type == "unclassified":
        return "untyped (no arc_type declared)"
    if arc_type not in ("inventing", "applying"):
        # C-HE-26 admits exactly two open-declared labels — an unknown
        # label ("research") is no more evaluable than none (codex r10).
        return f"unknown open-declared arc type {arc_type!r} (C-HE-26 admits inventing|applying)"
    return None


def split_cohorts(rows: list[LedgerRow], levers: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    """Pure per-arc-type split: {arc_type: {evaluable, reason, buckets: {bucket: rows}}}."""
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        arc_type = r.arc_type or "unclassified"
        # C-HE-26: a close-time arc-type label is outcome-contaminated and cannot
        # support arc-type discrimination (codex r3). Close-declared rows group
        # under an explicitly contaminated key, never beside open-declared ones —
        # and the group CARRIES the contamination as data, so evaluation logic
        # never re-derives it from the key string (codex r6).
        contaminated = arc_type != "unclassified" and r.arc_type_declared_at != "open"
        reason = _non_evaluable_reason(arc_type, contaminated)
        if contaminated:
            arc_type = f"{arc_type} (close-declared — outcome-contaminated, C-HE-26)"
        # C-HE-26 requires an UNCONTAMINATED OPEN-TIME inventing/applying label for
        # the lever decision — an untyped group fails that just as a close-declared
        # one does (codex r9); both stay descriptively visible, neither evaluable.
        group = out.setdefault(
            arc_type,
            {
                "evaluable": reason is None,
                "reason": reason,
                "buckets": {b: [] for b in _BUCKETS},
            },
        )
        buckets = group["buckets"]
        declared = r.levers_active
        # [] is an explicit claim ("no lever was live"); an ABSENT or null field is
        # no claim at all — collapsing them would let structurally incomplete rows
        # contaminate the baseline (codex r4). Undeclared rows are excluded loudly.
        if declared is None:
            buckets["undeclared"].append(r)
            continue
        # The queue CLI accepts repeated --levers values; [B-211] and
        # [B-211,B-211] are one declaration, not two cohorts (codex r11).
        declared = sorted(set(declared))
        r = r.model_copy(update={"levers_active": declared})
        bucket = (
            "treated"
            if any(lv in declared for lv in levers)
            else ("baseline" if declared == [] else "other_levers")
        )
        if r.review_rounds is None:
            buckets["unmapped"].append(r)
        elif r.round_completeness != "complete":
            # The LedgerRow boundary types the legacy rule: an ABSENT field
            # defaults to "complete"; an EXPLICIT null survives as None, an
            # unknown that fails closed with every other non-complete value
            # (codex r9 + r10).
            # A partial suffix carries review_rounds as a LOWER BOUND and an
            # unknown P1 count; letting it into a median converts "unknown"
            # into a score (codex r1 on this tool).
            buckets["partial"].append(r)
        else:
            buckets[bucket].append(r)
    return out


def _metrics(r: LedgerRow, levers: tuple[str, ...]) -> dict[str, Any]:
    span = r.arc_span_s
    declared = r.levers_active
    p1 = r.p1_rounds
    assert declared is not None  # undeclared rows are bucketed before metrics
    return {
        "arc_id": r.arc_id,
        "review_rounds": r.review_rounds,
        # A null p1_rounds is unmapped provenance, not a clean arc — len(None or [])
        # would award the best possible P1 score to an unmeasured value (codex r2).
        "p1_rounds": len(p1) if p1 is not None else None,
        "arc_span_h": round(span / 3600, 1) if span is not None else None,
        # Main + subagent IET in millions. Null main is unmeasured even when a
        # subagent figure exists — a partial sum would read as a cheaper arc.
        "cost_miet": (
            round((r.cost_main_iet + (r.cost_subagent_iet or 0)) / 1e6, 2)
            if r.cost_main_iet is not None
            else None
        ),
        "levers": declared,
        "target_levers_declared": sorted(lv for lv in declared if lv in levers),
    }


def _median(values: list[float]) -> float | None:
    return round(statistics.median(values), 1) if values else None


def summarize_type(group: dict[str, Any], levers: tuple[str, ...]) -> dict[str, Any]:
    """Pure summary for one arc type — one JSON-able value."""
    buckets = group["buckets"]
    treated = [_metrics(r, levers) for r in buckets["treated"]]
    baseline = [_metrics(r, levers) for r in buckets["baseline"]]
    other = [_metrics(r, levers) for r in buckets["other_levers"]]
    base_p1 = [m["p1_rounds"] for m in baseline if m["p1_rounds"] is not None]
    base_span = [m["arc_span_h"] for m in baseline if m["arc_span_h"] is not None]
    base_median = {
        "review_rounds": _median([m["review_rounds"] for m in baseline]),
        "p1_rounds": _median(base_p1),
        "arc_span_h": _median(base_span),
        # A P1 median over fewer rows than the cohort must say so, or the n>=5
        # bar can look satisfied by rows the P1 metric never measured (codex r3).
        "measured_n": {
            "review_rounds": len(baseline),
            "p1_rounds": len(base_p1),
            "arc_span_h": len(base_span),
        },
    }
    for m in treated:
        m["delta_rounds_vs_baseline_median"] = (
            round(m["review_rounds"] - base_median["review_rounds"], 1)
            if base_median["review_rounds"] is not None
            else None
        )
    # Per-skill attribution needs a CONTRAST on the FULL lever sets (codex r1-r3):
    # lever L is separable iff two evaluable rows' complete declarations differ in
    # exactly {L}. {} vs {211,212} separates nothing; {} vs {211,999} is confounded
    # by the non-target lever; only {} vs {211} (or {211} vs {211,212}) isolates.
    # Evaluable other-lever rows contribute their PATTERNS (a matched contrast
    # like {999} vs {211,999} isolates B-211 — codex r5) while staying excluded
    # from every cohort median.
    patterns = {tuple(sorted(m["levers"])) for m in treated + other}
    patterns |= {()} if baseline else set()
    # A contrast built from non-evaluable (contaminated/untyped) data must not
    # be advertised as available separation (codex r10).
    separable = (
        sorted(
            {
                lv
                for a in patterns
                for b in patterns
                if len(set(a) ^ set(b)) == 1
                for lv in set(a) ^ set(b)
                if lv in levers
            }
        )
        if group["evaluable"]
        else []
    )
    # An excluded row keeps its treatment identity: "no evaluable treated arcs"
    # and "no treated arcs declared" are different states (codex r2, P3).
    excluded_treated = sum(
        1
        for b in ("unmapped", "partial")
        for r in buckets[b]
        if any(lv in (r.levers_active or []) for lv in levers)
    )
    # The evaluable unit is the EXACT lever pattern (codex r6/r7): pooled
    # treated aggregates are gone — 5x B-211-only + 5x B-212-only rows pooled
    # to one median would evaluate neither lever. Every evaluable row's
    # pattern is summarized, INCLUDING other-lever control patterns, so any
    # separability claim ships the metrics of both sides of its contrast.
    by_pattern: dict[str, list[dict[str, Any]]] = {}
    for m in treated + baseline + other:
        key = "+".join(sorted(m["levers"])) or "(none)"
        by_pattern.setdefault(key, []).append(m)
    pattern_metrics = {
        k: {
            "n": len(ms),
            "median_rounds": _median([m["review_rounds"] for m in ms]),
            "median_p1": _median([m["p1_rounds"] for m in ms if m["p1_rounds"] is not None]),
            "p1_measured_n": sum(1 for m in ms if m["p1_rounds"] is not None),
        }
        for k, ms in by_pattern.items()
    }
    return {
        # C-HE-26: only an uncontaminated, typed group supports the n>=5 lever
        # decision — the numbers stay visible but others say NON-EVALUABLE,
        # carrying the split-time reason so the render never re-derives it.
        "evaluable_for_lever_decision": group["evaluable"],
        "non_evaluable_reason": group["reason"],
        "pattern_metrics": pattern_metrics,
        "cohort_sizes": {k: len(v) for k, v in buckets.items()},
        "baseline_median": base_median,
        "treated_arcs": treated,
        "p1_unmapped": sorted(m["arc_id"] for m in treated + baseline if m["p1_rounds"] is None),
        "separable_levers": separable,
        "per_skill_separable": bool(separable),
        "excluded_treated_count": excluded_treated,
        "excluded_unmapped": [r.arc_id for r in buckets["unmapped"]],
        "excluded_undeclared": [r.arc_id for r in buckets["undeclared"]],
        "excluded_partial": [r.arc_id for r in buckets["partial"]],
        "excluded_other_levers": [r.arc_id for r in buckets["other_levers"]],
    }


def summarize(
    cohorts_by_type: dict[str, dict[str, Any]], levers: tuple[str, ...]
) -> dict[str, Any]:
    return {
        "target_levers": list(levers),
        "arc_types": {t: summarize_type(g, levers) for t, g in sorted(cohorts_by_type.items())},
    }


def render(summary: dict[str, Any]) -> str:
    """Human view of the summary — the JSON is the authority, this a projection."""
    lines = [f"arc-lever-report — levers {', '.join(summary['target_levers'])} (per arc type)"]
    for arc_type, s in summary["arc_types"].items():
        sizes = s["cohort_sizes"]
        bm = s["baseline_median"]
        lines.append(
            f"[{arc_type}] {sizes['treated']} treated / {sizes['baseline']} baseline — "
            f"baseline median: rounds={bm['review_rounds']} "
            f"(n={bm['measured_n']['review_rounds']}) "
            f"p1={bm['p1_rounds']} (n={bm['measured_n']['p1_rounds']}) "
            f"span_h>={bm['arc_span_h']} (n={bm['measured_n']['arc_span_h']}; span is a "
            f"lower bound: derived excludes first-round duration)"
        )
        if not s["evaluable_for_lever_decision"]:
            lines.append(
                "  NON-EVALUABLE for the n>=5 lever decision: "
                f"{s['non_evaluable_reason']} — numbers are descriptive only"
            )
        for pat, ps in sorted(s["pattern_metrics"].items()):
            lines.append(
                f"  pattern[{pat}]: n={ps['n']} median_rounds={ps['median_rounds']} "
                f"median_p1={ps['median_p1']} (p1 n={ps['p1_measured_n']})"
            )
        if s["p1_unmapped"]:
            lines.append(
                "  p1-unmapped rows (in cohorts, excluded from P1 medians only): "
                + ", ".join(str(a) for a in s["p1_unmapped"])
            )
        if not s["treated_arcs"]:
            # "declare the levers" would be a false repair when treated rows exist
            # but none is evaluable (codex r2, P3) — the states are different.
            lines.append(
                f"  no evaluable treated arcs ({s['excluded_treated_count']} treated "
                "row(s) excluded as unmapped/partial)"
                if s["excluded_treated_count"]
                else "  no treated arcs — declare the lever ids at arc-metrics queue time"
            )
        for m in s["treated_arcs"]:
            p1 = m["p1_rounds"] if m["p1_rounds"] is not None else "unmapped"
            cost = f" cost={m['cost_miet']}M IET" if m["cost_miet"] is not None else ""
            lines.append(
                f"  {m['arc_id']} rounds={m['review_rounds']} p1={p1} "
                f"span_h>={m['arc_span_h']} "
                f"delta_rounds_vs_baseline={m['delta_rounds_vs_baseline_median']}{cost}"
            )
        lines.append(
            "  per-skill separation: "
            + (
                f"available for {', '.join(s['separable_levers'])} (single-lever contrast exists)"
                if s["per_skill_separable"]
                else "NOT separable — no two evaluable patterns differ in exactly one target lever"
            )
        )
        for key, label in (
            ("excluded_unmapped", "unmapped rounds, B-170 — never evaluated"),
            ("excluded_partial", "partial round data — lower bounds, never evaluated"),
            ("excluded_other_levers", "other lever sets"),
            ("excluded_undeclared", "levers_active absent/null — no claim, not a baseline"),
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
        # Close-declared groups carry an annotation suffix on the bare type key —
        # the filter must match those too, or the recommended invocation returns
        # an empty report on today's all-close-declared ledger (codex r4).
        cohorts = {
            t: b
            for t, b in cohorts.items()
            if t == args.arc_type or t.startswith(f"{args.arc_type} (")
        }
    summary = summarize(cohorts, levers)
    print(json.dumps(summary, indent=2) if args.json else render(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

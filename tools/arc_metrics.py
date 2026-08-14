#!/usr/bin/env python3
"""Arc-metrics ledger (B-170) -- per-arc wall-clock capture for efficacy tracking.

One row per arc, appended at merge time. The load-bearing field is
``levers_active``: each arc records which wall-clock levers were live when it
ran, so efficacy becomes a cohort comparison rather than an assertion.

Provenance discipline
---------------------
Fields fall into three classes, and the class is recorded per row so a
consumer can never mistake one for another:

``derived``    computed from git / gh / round-log mtimes at run time
``declared``   supplied by the operator (arc type, decision count, levers) --
               these are judgements, not measurements, and are never guessed
``unmapped``   the input for this field does not exist (e.g. no round logs
               survive for that PR). Recorded as null with a reason, never
               imputed and never silently zeroed.

Fail-closed
-----------
Any external call that exits non-zero, returns empty, or parses to an
unexpected shape aborts with a named cause. A row is never emitted with
silently-zeroed fields -- an absent measurement must be distinguishable from
a measured zero.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import shutil
import statistics
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / ".harness" / "arc-metrics.jsonl"

# The codex CLI prints every finding TWICE -- once inline in its narrative
# turn, once in the structured "Review comment:" block. Verified byte-for-byte
# on a real transcript during the 2026-08-14 audit. Raw grep counts are
# therefore halved to get true finding counts.
CODEX_DUPLICATE_FACTOR = 2


class AbortError(RuntimeError):
    """A named, fail-closed abort. Never swallowed, never defaulted."""


@dataclass
class ArcRow:
    arc_id: str
    pr: int | None = None
    # -- derived from gh --
    additions: int | None = None
    deletions: int | None = None
    files: int | None = None
    commits: int | None = None
    created_at: str | None = None
    merged_at: str | None = None
    total_arc_wall_s: float | None = None
    merge_sha: str | None = None
    # -- derived from round logs --
    review_rounds: int | None = None
    round_wall_s: list[float] = field(default_factory=list)
    p1_rounds: list[int] = field(default_factory=list)
    round_log_source: str | None = None
    # Absolute round bounds. Without these the ledger cannot reconstruct the
    # real arc window (first review activity -> merge): gap durations alone
    # cannot say WHERE the loop sat relative to the PR, and this workspace has
    # run both review-then-open and open-then-review workflows.
    first_round_at: str | None = None
    last_round_at: str | None = None
    arc_span_s: float | None = None
    # -- derived from gh run --
    ci_runs: int | None = None
    ci_wall_s: list[float] = field(default_factory=list)
    # -- declared by operator (judgements, never inferred) --
    arc_type: str | None = None
    decision_count: int | None = None
    levers_active: list[str] = field(default_factory=list)
    # -- bookkeeping --
    provenance: dict[str, str] = field(default_factory=dict)
    captured_at: str = ""
    notes: str = ""


def run(cmd: list[str], *, what: str) -> str:
    """Run a command, validating exit status and non-empty output."""
    if shutil.which(cmd[0]) is None:
        raise AbortError(f"{what}: '{cmd[0]}' not on PATH")
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    if proc.returncode != 0:
        raise AbortError(
            f"{what}: exit {proc.returncode} from {' '.join(cmd[:4])}...\n"
            f"  stderr: {proc.stderr.strip()[:300]}"
        )
    if not proc.stdout.strip():
        raise AbortError(f"{what}: empty output from {' '.join(cmd[:4])}...")
    return proc.stdout


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def gh_pr(pr: int) -> dict:
    fields = "additions,deletions,changedFiles,commits,createdAt,mergedAt,mergeCommit,title"
    raw = run(["gh", "pr", "view", str(pr), "--json", fields], what=f"gh pr view #{pr}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AbortError(f"gh pr view #{pr}: output is not JSON: {exc}") from exc
    for key in ("additions", "changedFiles", "createdAt"):
        if data.get(key) is None:
            raise AbortError(f"gh pr view #{pr}: missing expected field '{key}'")
    return data


def round_metrics(globs: list[str]) -> tuple[list[Path], list[float], list[int]]:
    """Derive per-round wall clock from log mtimes, and P1 arrival by round."""
    logs: list[Path] = []
    for g in globs:
        p = Path(g).expanduser()
        matched = sorted(p.parent.glob(p.name)) if p.name else []
        logs.extend(m for m in matched if m.is_file())
    if not logs:
        raise AbortError(
            f"round logs: zero files matched {globs} -- refusing to record "
            "'0 rounds' for what may be an unlooked path"
        )

    logs.sort(key=lambda f: f.stat().st_mtime)
    mtimes = [f.stat().st_mtime for f in logs]
    gaps = [round(b - a, 1) for a, b in itertools.pairwise(mtimes)]

    p1_rounds: list[int] = []
    for idx, f in enumerate(logs, start=1):
        try:
            text = f.read_text(errors="replace")
        except OSError as exc:
            raise AbortError(f"round logs: cannot read {f}: {exc}") from exc
        if count_p1(text) >= 1:
            p1_rounds.append(idx)
    return logs, gaps, p1_rounds


def count_p1(text: str) -> int:
    """True P1 count, across BOTH round-log dialects.

    Codex transcripts tag findings ``[P1]`` and print each finding twice (once
    inline, once in the structured block) -- so the bracketed count is halved.
    Absorption commit messages write a bare ``P1 <CLAIM>`` at line start and are
    NOT duplicated. Counting only one dialect silently reports zero for the
    other, which is the 'empty vs unlooked' failure this ledger exists to avoid.
    """
    bracketed = text.count("[P1]") // CODEX_DUPLICATE_FACTOR
    bare = len(re.findall(r"^P1\s+\S", text, flags=re.MULTILINE))
    return bracketed + bare


def ci_metrics(sha: str) -> tuple[int, list[float]]:
    raw = run(
        [
            "gh",
            "run",
            "list",
            "--limit",
            "40",
            "--json",
            "headSha,createdAt,updatedAt,conclusion,event",
        ],
        what=f"gh run list for {sha[:8]}",
    )
    runs = json.loads(raw)
    hit = [r for r in runs if str(r.get("headSha", "")).startswith(sha[:12])]
    durations = []
    for r in hit:
        # A cancelled run is NOT a fast green -- exclude it from timing, or the
        # ~65s cancellation signature poisons the baseline (2026-08-14).
        if r.get("conclusion") != "success":
            continue
        durations.append(
            round((parse_iso(r["updatedAt"]) - parse_iso(r["createdAt"])).total_seconds(), 1)
        )
    return len(hit), durations


def extract(args: argparse.Namespace) -> ArcRow:
    prov: dict[str, str] = {}
    row = ArcRow(arc_id=args.arc_id or f"pr-{args.pr}", pr=args.pr)

    data = gh_pr(args.pr)
    row.additions = data["additions"]
    row.deletions = data.get("deletions")
    row.files = data["changedFiles"]
    row.commits = len(data.get("commits") or [])
    row.created_at = data["createdAt"]
    row.merged_at = data.get("mergedAt")
    row.merge_sha = (data.get("mergeCommit") or {}).get("oid")
    if row.merged_at:
        row.total_arc_wall_s = round(
            (parse_iso(row.merged_at) - parse_iso(row.created_at)).total_seconds(), 1
        )
        prov["total_arc_wall_s"] = "derived"
    else:
        prov["total_arc_wall_s"] = "unmapped:not-merged"
    prov["gh_fields"] = "derived"

    if args.round_logs:
        logs, gaps, p1 = round_metrics(args.round_logs)
        row.review_rounds = len(logs)
        row.round_wall_s = gaps
        row.p1_rounds = p1
        row.round_log_source = str(Path(args.round_logs[0]).parent)
        first = datetime.fromtimestamp(logs[0].stat().st_mtime, tz=UTC)
        last = datetime.fromtimestamp(logs[-1].stat().st_mtime, tz=UTC)
        row.first_round_at = first.isoformat()
        row.last_round_at = last.isoformat()
        if row.merged_at:
            # The real arc window: first review activity through merge. This is
            # the metric the ~5h/arc claim should be measured against -- NOT
            # createdAt->mergedAt, which misses every round run before the PR
            # opened (measured at up to 56x the PR window).
            row.arc_span_s = round((parse_iso(row.merged_at) - first).total_seconds(), 1)
        prov["round_fields"] = "derived"
    else:
        prov["round_fields"] = "unmapped:no-round-logs-supplied"

    if row.merge_sha:
        try:
            n, durs = ci_metrics(row.merge_sha)
            row.ci_runs, row.ci_wall_s = n, durs
            prov["ci_fields"] = "derived"
        except AbortError as exc:
            prov["ci_fields"] = f"unmapped:{exc}"
    else:
        prov["ci_fields"] = "unmapped:no-merge-sha"

    row.arc_type = args.arc_type
    row.decision_count = args.decisions
    row.levers_active = args.levers or []
    prov["arc_type"] = "declared" if args.arc_type else "unmapped:unclassified"
    prov["decision_count"] = "declared" if args.decisions is not None else "unmapped:unclassified"
    prov["levers_active"] = "declared"

    row.provenance = prov
    row.captured_at = datetime.now(tz=UTC).isoformat()
    row.notes = args.notes or ""
    return row


def append(row: ArcRow) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    existing = read_ledger()
    if any(r.get("arc_id") == row.arc_id for r in existing):
        raise AbortError(
            f"arc_id '{row.arc_id}' already in ledger -- refusing to append a "
            "duplicate (use a distinct --arc-id or remove the prior row)"
        )
    with LEDGER.open("a") as fh:
        fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def read_ledger() -> list[dict]:
    if not LEDGER.exists():
        return []
    rows = []
    for n, line in enumerate(LEDGER.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AbortError(f"ledger line {n} is not valid JSON: {exc}") from exc
    return rows


def fmt_span(vals: list[float], unit: float = 60.0, suffix: str = "m") -> str:
    """Median with range -- never a bare mean. Measured round variance is ~5x."""
    if not vals:
        return "--"
    v = sorted(x / unit for x in vals)
    med = statistics.median(v)
    return f"{med:.1f}{suffix} (n={len(v)}, {v[0]:.1f}-{v[-1]:.1f})"


def summary(_args: argparse.Namespace) -> int:
    rows = read_ledger()
    if not rows:
        raise AbortError(f"ledger is empty or absent: {LEDGER}")

    baseline = [r for r in rows if not r.get("levers_active")]
    treated = [r for r in rows if r.get("levers_active")]

    print(f"arc-metrics ledger: {len(rows)} rows  ({LEDGER})")
    print(f"  baseline (no levers): {len(baseline)}   treated: {len(treated)}\n")

    for label, cohort in (("BASELINE", baseline), ("TREATED", treated)):
        if not cohort:
            continue
        print(f"-- {label} (n={len(cohort)}) " + "-" * (46 - len(label)))
        arcs = [r["total_arc_wall_s"] for r in cohort if r.get("total_arc_wall_s")]
        rounds = [r["review_rounds"] for r in cohort if r.get("review_rounds")]
        allgaps = [g for r in cohort for g in (r.get("round_wall_s") or [])]
        adds = [r["additions"] for r in cohort if r.get("additions") is not None]
        print(f"  arc wall clock   {fmt_span(arcs)}          [stochastic]")
        print(f"  round wall clock {fmt_span(allgaps)}          [stochastic]")
        print(
            f"  review rounds    "
            f"{statistics.median(rounds):.0f} (n={len(rounds)}, "
            f"{min(rounds)}-{max(rounds)})"
            if rounds
            else "  review rounds    --"
        )
        print(f"  additions        {fmt_span(adds, 1.0, '')}")
        unmapped = sum(
            1
            for r in cohort
            if str(r.get("provenance", {}).get("round_fields", "")).startswith("unmapped")
        )
        if unmapped:
            print(f"  {unmapped}/{len(cohort)} rows have NO round data (unmapped, not zero)")
        print()

    allgaps = [g for r in rows for g in (r.get("round_wall_s") or [])]
    if allgaps:
        lo, hi = min(allgaps) / 60, max(allgaps) / 60
        spread = f"{lo:.1f}-{hi:.1f} min/round, {hi / max(lo, 0.1):.0f}x"
    else:
        spread = "not yet measurable"
    print(
        f"NOTE  Metrics marked [stochastic] carry wide measured variance "
        f"({spread}).\n      A ~2% effect is NOT detectable at this sample size. "
        "Deterministic metrics\n      (CI job seconds, arc count, rounds consumed "
        "by mechanised classes) are\n      countable and need no statistics -- "
        "prefer those for efficacy claims."
    )
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    row = extract(args)
    if args.dry_run:
        print(json.dumps(asdict(row), indent=2, sort_keys=True))
        return 0
    append(row)
    print(f"appended {row.arc_id} -> {LEDGER}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="arc_metrics", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    ex = sub.add_parser("extract", help="capture one arc row")
    ex.add_argument("--pr", type=int, required=True)
    ex.add_argument("--arc-id")
    ex.add_argument("--arc-type", choices=["inventing", "applying"])
    ex.add_argument("--decisions", type=int, help="independent decision count")
    ex.add_argument("--round-logs", nargs="*", help="glob(s) for this arc's round logs")
    ex.add_argument("--levers", nargs="*", help="levers live during this arc")
    ex.add_argument("--notes", default="")
    ex.add_argument("--dry-run", action="store_true")
    ex.set_defaults(func=cmd_extract)

    sm = sub.add_parser("summary", help="per-cohort medians with range")
    sm.set_defaults(func=summary)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except AbortError as exc:
        print(f"ABORT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

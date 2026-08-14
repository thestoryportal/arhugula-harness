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
import os
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

#: Pending captures, deliberately OUTSIDE the repo. A topic worktree is
#: disposed at loop completion, so anything queued inside one is lost with it --
#: and a dirty tracked file there blocks that disposal outright. See
#: ``queue_capture``.
QUEUE = Path(
    os.environ.get(
        "ARC_METRICS_QUEUE",
        Path.home() / ".gstack" / "projects" / "arhugula-v2" / "arc-metrics-queue.jsonl",
    )
)

# The codex CLI prints every finding TWICE -- once inline in its narrative
# turn, once in the structured block below this marker. Verified byte-for-byte
# on a real transcript during the 2026-08-14 audit. Findings are counted as
# DISTINCT line-anchored matches rather than halved: a halving constant is
# wrong the moment a transcript carries an odd number of contextual mentions,
# and it cannot tell a quoted past finding from a live one.
FINAL_REVIEW_MARKER = "Full review comments:"

#: `gh run list --commit` matches on the full object name only.
FULL_SHA_LEN = 40


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

    Counts only findings, never prose that happens to mention a severity tag.
    A whole-transcript ``text.count("[P1]")`` is wrong twice over: the reviewed
    diff can quote a PAST review ("R1 -- two real [P1]s advisor missed") and a
    skill doc can carry a literal format example, both of which then classify a
    clean round as carrying a P1. Measured on the B-40 round-1 log, where both
    bracketed hits were exactly that.

    So: findings are anchored to line start (``- [P1] ...``, codex's own
    emission shape) and counted as DISTINCT lines. Distinctness -- not a
    halving constant -- is what absorbs codex printing every finding twice
    (once inline, once in the structured block): two identical emissions of one
    finding collapse, while two genuinely different findings do not. When the
    structured block is present, only the LAST one is read, so an earlier
    round quoted inside the transcript cannot leak in.

    Absorption commit messages write a bare ``P1 <CLAIM>`` at line start and are
    NOT duplicated. Counting only one dialect silently reports zero for the
    other, which is the 'empty vs unlooked' failure this ledger exists to avoid.
    """
    payload = text
    if FINAL_REVIEW_MARKER in text:
        payload = text.rsplit(FINAL_REVIEW_MARKER, 1)[1]
    bracketed = {
        line.strip() for line in re.findall(r"^\s*-?\s*\[P1\].*$", payload, flags=re.MULTILINE)
    }
    bare = {line.strip() for line in re.findall(r"^P1\s+\S.*$", payload, flags=re.MULTILINE)}
    return len(bracketed) + len(bare)


def ci_metrics(sha: str) -> tuple[int, list[float]]:
    """CI runs for THIS commit, asked for by commit.

    Scanning the latest N runs and filtering client-side cannot distinguish
    "this commit had no runs" from "this commit is older than the window", and
    the second one silently becomes a measured zero -- the exact absent-vs-zero
    violation this ledger exists to prevent. Measured: 12 of the 16 backfilled
    baseline rows recorded `derived` CI fields with zero runs under the old
    windowed query. ``--commit`` makes an empty result mean what it says -- but
    ONLY for a full 40-char SHA. Measured 2026-08-14: ``gh run list --commit
    <abbrev>`` returns ``[]`` for a commit whose runs plainly exist, so an
    abbreviated SHA would reintroduce the silent zero through the very query
    meant to remove it.
    """
    if len(sha) != FULL_SHA_LEN:
        raise AbortError(
            f"ci runs: need a full {FULL_SHA_LEN}-char SHA, got {len(sha)} chars "
            f"({sha!r}) -- gh returns an empty set for an abbreviated commit, "
            "which would be recorded as a measured zero"
        )
    raw = run(
        [
            "gh",
            "run",
            "list",
            "--commit",
            sha,
            "--limit",
            "100",
            "--json",
            "headSha,createdAt,updatedAt,conclusion,event",
        ],
        what=f"gh run list --commit {sha[:8]}",
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
    # An arc is not an arc until it merged. Appending a pre-merge row would
    # persist null merge fields AND burn the arc_id, so the duplicate guard
    # below would then reject the correct post-merge capture -- turning a
    # mistyped PR number into manual ledger surgery. Refuse instead; --dry-run
    # stays available for inspecting a row before merge.
    if not row.merged_at or not row.merge_sha:
        raise AbortError(
            f"{row.arc_id}: refusing to append an unmerged arc "
            f"(merged_at={row.merged_at!r}, merge_sha={row.merge_sha!r}) -- "
            "capture after merge, or use --dry-run to inspect"
        )
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    existing = read_ledger()
    if any(r.get("arc_id") == row.arc_id for r in existing):
        raise AbortError(
            f"arc_id '{row.arc_id}' already in ledger -- refusing to append a "
            "duplicate (use a distinct --arc-id or remove the prior row)"
        )
    with LEDGER.open("a") as fh:
        fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def queue_capture(args: argparse.Namespace) -> int:
    """Record an arc's capture inputs OUTSIDE the repo, for a later drain.

    Capture runs at arc closure, when the merge SHA finally exists -- but that
    is the worst moment to write into the tracked ledger. In an autonomous arc
    the closure step runs inside the topic worktree, and a dirty tracked file
    there both strands the row when the worktree is disposed and blocks the
    disposal itself (worktree GC skips a merged worktree carrying local state,
    while loop completion requires that worktree to be unregistered).

    Committing straight to `main` is no better: before the terminating refresh
    the drift guard hard-fails the push, and after it the next local preflight
    hard-fails instead, demanding yet another refresh.

    So closure writes nothing to the repo. It queues the arc's inputs -- above
    all the DECLARED judgements (arc type, decision count, active levers) that
    only the session which ran the arc can supply -- to a durable path outside
    any worktree. The next arc drains the queue and commits the rows inside its
    own PR, which is an ordinary content commit with none of the above problems.
    """
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "pr": args.pr,
        "arc_id": args.arc_id,
        "arc_type": args.arc_type,
        "decisions": args.decisions,
        "round_logs": args.round_logs or [],
        "levers": args.levers or [],
        "notes": args.notes or "",
        "queued_at": datetime.now(tz=UTC).isoformat(),
    }
    with QUEUE.open("a") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    print(f"queued arc capture for #{args.pr} -> {QUEUE}")
    return 0


def read_queue() -> list[dict]:
    if not QUEUE.exists():
        return []
    out = []
    for n, line in enumerate(QUEUE.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AbortError(f"queue line {n} is not valid JSON: {exc}") from exc
    return out


def drain(_args: argparse.Namespace) -> int:
    """Fold every queued arc into the tracked ledger.

    Entries that are already in the ledger are dropped rather than re-appended;
    an entry whose capture still fails is KEPT queued, so a transient gh outage
    costs a retry rather than the row.
    """
    pending = read_queue()
    if not pending:
        print("arc-metrics queue is empty -- nothing to drain")
        return 0

    known = {r.get("arc_id") for r in read_ledger()}
    kept: list[dict] = []
    added = 0
    for entry in pending:
        arc_id = entry.get("arc_id") or f"pr-{entry['pr']}"
        if arc_id in known:
            print(f"  {arc_id}: already in ledger, dropping from queue")
            continue
        args = argparse.Namespace(
            pr=entry["pr"],
            arc_id=entry.get("arc_id"),
            arc_type=entry.get("arc_type"),
            decisions=entry.get("decisions"),
            round_logs=entry.get("round_logs") or None,
            levers=entry.get("levers"),
            notes=entry.get("notes", ""),
        )
        try:
            append(extract(args))
        except AbortError as exc:
            print(f"  {arc_id}: KEPT QUEUED -- {exc}", file=sys.stderr)
            kept.append(entry)
            continue
        print(f"  {arc_id}: appended")
        added += 1

    QUEUE.write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in kept))
    print(f"drained {added} arc(s); {len(kept)} still queued")
    return 0


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


def arc_duration(row: dict) -> float | None:
    """The arc: first review activity -> merge, falling back to the PR window.

    NOT ``createdAt -> mergedAt``. The review loop largely runs on the branch
    BEFORE the PR opens, so the PR window can understate an arc by 44x (#1337:
    6.1m open vs 269.2m real) or 58x (#1115: 2.8m vs 161.4m). It also runs the
    other way when a merged PR simply sat open (#1060: 548.2m open vs 44.4m of
    actual arc). Reporting the PR window as "arc wall clock" would have made
    the baseline cohort -- the whole point of this ledger -- meaningless.

    ``arc_span_s`` needs round data. Where none survives, the PR window stands
    in and ``summary`` prints how many rows are on that weaker footing.
    """
    return row.get("arc_span_s") or row.get("total_arc_wall_s")


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
        arcs = [d for d in (arc_duration(r) for r in cohort) if d]
        pr_window_only = sum(
            1 for r in cohort if not r.get("arc_span_s") and r.get("total_arc_wall_s")
        )
        rounds = [r["review_rounds"] for r in cohort if r.get("review_rounds")]
        allgaps = [g for r in cohort for g in (r.get("round_wall_s") or [])]
        adds = [r["additions"] for r in cohort if r.get("additions") is not None]
        print(f"  arc wall clock   {fmt_span(arcs)}          [stochastic]")
        if pr_window_only:
            print(
                f"     ^ {pr_window_only}/{len(cohort)} of these are the PR window only "
                "(no round data); the PR window is not the arc"
            )
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

    q = sub.add_parser("queue", help="record capture inputs out-of-repo (arc closure)")
    q.add_argument("--pr", type=int, required=True)
    q.add_argument("--arc-id")
    q.add_argument("--arc-type", choices=["inventing", "applying"])
    q.add_argument("--decisions", type=int, help="independent decision count")
    q.add_argument("--round-logs", nargs="*", help="glob(s) for this arc's round logs")
    q.add_argument("--levers", nargs="*", help="levers live during this arc")
    q.add_argument("--notes", default="")
    q.set_defaults(func=queue_capture)

    dr = sub.add_parser("drain", help="fold queued arcs into the ledger (next arc's PR)")
    dr.set_defaults(func=drain)

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

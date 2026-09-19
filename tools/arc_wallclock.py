#!/usr/bin/env python3
"""Per-arc wall-clock, the tracked outcome of spec v1.9 (C-HE-28 §2, X9h).

The goal the spec records: an arc lands in a mean of at most 60 minutes, in one lane or
in parallel lanes. X9h replaces C-HE-28 §2's correlation with this measure, correlated
against `concurrent_lanes_at_open`. It reads the stores the loop already writes:

- the reservation (C-HE-03), through `reservations.current`: reserved_at, PR, merge sha
  and the `concurrent_lanes_at_open` sensor, read as lanes by `arc_metrics.lanes_at_open`;
- the reservation's `phases.verify.start` span (C-HE-27 §5): when review round 1 began;
- the gate log (C-HE-24): the last review row for the arc;
- git: when the merge commit landed on main;
- the merge door (C-HE-06): the `released.<token>` record, whose mtime `_move_lease`
  stamps immediately before the rename that releases the lease.

Phases, in minutes:

    build     reserved      -> review start (the verify span's round-1 admission)
    review    review start  -> last review row
    to_merge  last review   -> merge commit   (CI wait, gate rows, the door's merge step)
    door      merge commit  -> lease release  (post-merge CI, refresh or lit step)
    total     reserved      -> lease release

A phase whose endpoint the stores never recorded is None and is left out of that phase's
statistics; `total` is never computed from a substitute endpoint. The summary is reported
over all arcs and per lanes-at-open cohort (`unknown` where the sensor recorded nothing).

The merge instant comes from the reservation's merge_sha; when an older reservation
lacks one, it is resolved from the squash commit on main whose subject ends `(#<pr>)`,
and the JSON row says so (`merged_source`). A merged arc whose merge instant cannot be
resolved is listed as unmeasured with the reason.

Usage:
    uv run python tools/arc_wallclock.py [--last N] [--json]

Exit codes: 0 report printed; 2 a store could not be read.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arc_metrics  # [LAW:one-source-of-truth] lanes_at_open is the one cohort-key conversion
import merge_door  # [LAW:one-source-of-truth] DOOR is the door's own path
import reservations  # [LAW:one-source-of-truth] the fenced reader of the reservation store

REPO = Path(__file__).resolve().parents[1]
GATE_LOG = REPO / ".harness" / "merge-gate-log.jsonl"
#: Producers whose rows are review activity (codex/gemini rounds and the merge-gate lenses).
REVIEW_PRODUCER_PREFIXES = ("codex_review_wrapper", "gemini_review_wrapper", "merge-gate-")
PHASES = ("build", "review", "to_merge", "door", "total")
#: The spec v1.9 goal (C-HE-28 §2 as amended by X9h).
GOAL_MEAN_MINUTES = 60.0


class StoreError(Exception):
    """A store the report depends on could not be read."""


@dataclass(frozen=True)
class Timeline:
    """One merged arc's instants. `None` means the store holds no record of that instant."""

    arc_id: str
    pr: int | None
    reserved: datetime
    #: round-1 admission: the reservation's `phases.verify.start` span edge, which
    #: review-with-failover-logged writes before the reviewer runs (C-HE-27 §5)
    review_start: datetime | None
    last_review: datetime | None
    merged: datetime
    released: datetime | None
    #: the C-HE-28 cohort key in LANES (`arc_metrics.lanes_at_open`: stored siblings + 1,
    #: 1 for a reservation older than the sensor); None when the sensor recorded nothing
    lanes: int | None
    #: where `merged` came from: the reservation's merge_sha, or the squash commit on
    #: main whose subject names the PR (landings older than the door's merge_sha record)
    merged_source: str = "reservation"


@dataclass(frozen=True)
class Unmeasured:
    arc_id: str
    reserved: datetime
    reason: str


# ── pure core ────────────────────────────────────────────────────────────────


def _minutes(start: datetime | None, end: datetime | None) -> float | None:
    return None if start is None or end is None else (end - start).total_seconds() / 60.0


def phases(t: Timeline) -> dict[str, float | None]:
    """Phase durations in minutes; a phase whose endpoint was never recorded is None."""
    # [LAW:dataflow-not-control-flow] every phase is computed every time; absence flows
    # through as None rather than branching the set of phases
    return {
        "build": _minutes(t.reserved, t.review_start),
        "review": _minutes(t.review_start, t.last_review),
        "to_merge": _minutes(t.last_review, t.merged),
        "door": _minutes(t.merged, t.released),
        "total": _minutes(t.reserved, t.released),
    }


def summarize(timelines: list[Timeline]) -> dict[str, dict[str, float | int | None]]:
    """Mean, median and count per phase over the arcs that recorded that phase."""
    out: dict[str, dict[str, float | int | None]] = {}
    for name in PHASES:
        vals = [v for t in timelines if (v := phases(t)[name]) is not None]
        out[name] = {
            "n": len(vals),
            "mean": statistics.fmean(vals) if vals else None,
            "median": statistics.median(vals) if vals else None,
        }
    return out


def by_cohort(timelines: list[Timeline]) -> dict[int | None, dict[str, float | int | None]]:
    """The total-phase summary per lanes-at-open cohort (C-HE-28 §2, X9h), ascending by
    lanes, with the unknown cohort (None) last."""
    keys = sorted({t.lanes for t in timelines}, key=lambda k: (k is None, k or 0))
    return {k: summarize([t for t in timelines if t.lanes == k])["total"] for k in keys}


def cohort_label(lanes: int | None) -> str:
    return "unknown" if lanes is None else str(lanes)


def latest(
    timelines: list[Timeline], unmeasured: list[Unmeasured], n: int
) -> tuple[list[Timeline], list[Unmeasured]]:
    """The n most recently reserved merged arcs, measured or not -- `reserved` is the one
    instant every merged arc has; n >= 1 is guaranteed by `_positive_int` at the CLI."""
    cut = sorted([t.reserved for t in timelines] + [u.reserved for u in unmeasured])[-n:][0]
    return (
        sorted((t for t in timelines if t.reserved >= cut), key=lambda t: t.reserved),
        [u for u in unmeasured if u.reserved >= cut],
    )


def goal_verdict(mean_total: float | None) -> str:
    if mean_total is None:
        return "no arcs with a recorded release"
    return "MET" if mean_total <= GOAL_MEAN_MINUTES else "NOT MET"


# ── effectful edge: read the stores ──────────────────────────────────────────


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _last_review(rows: list[dict]) -> dict[str, datetime]:
    """The last review row per arc: rows are minted when a reviewer RETURNS, so the last
    one ends the review phase (the first one marks round 1's end, not the start)."""
    last: dict[str, datetime] = {}
    for r in rows:
        if not str(r.get("producer", "")).startswith(REVIEW_PRODUCER_PREFIXES):
            continue
        at = _ts(r["ts"])
        last[r["arc_id"]] = max(last.get(r["arc_id"], at), at)
    return last


def _verify_start(head: dict) -> datetime | None:
    """Round-1 admission from the reservation's span record; None for an arc before the
    span existed (U-HE-50), never a substitute instant."""
    start = (head.get("phases") or {}).get("verify", {}).get("start")
    return _ts(start) if start else None


def _releases(door_dir: Path) -> dict[str, datetime]:
    """Release instant per reservation: the mtime `_move_lease` stamps on `released.<T>`."""
    out: dict[str, datetime] = {}
    if door_dir.is_symlink():
        raise StoreError(f"merge-door directory {door_dir} is a symlink -- refused")
    for released in door_dir.glob("released.*"):
        if released.is_symlink():
            # the door refuses symlinked history (merge_door.py gc); a planted link would
            # inject a forged release instant into the measure
            raise StoreError(f"release record {released} is a symlink -- refused")
        try:
            at = datetime.fromtimestamp(released.stat().st_mtime, UTC)
            arc = json.loads(released.read_text())["reservation_id"]
        except FileNotFoundError:
            # the door's 30-day gc (merge_door.gc) removed it mid-walk: the release is
            # unrecorded, so the arc's door and total phases stay None
            continue
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            raise StoreError(f"unreadable release record {released}: {exc!r}") from exc
        out[arc] = max(out.get(arc, at), at)
    return out


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def _squash_commits(repo: Path) -> dict[int, str] | str:
    """PR number -> squash commit on origin/main, from subjects ending `(#<pr>)`; or the
    reason origin/main is unreadable, which only the arcs lacking a merge_sha inherit."""
    proc = _git(repo, "log", "--first-parent", "--format=%H %s", "origin/main")
    if proc.returncode != 0:
        return f"no merge_sha and git cannot read origin/main: {proc.stderr.strip()}"
    out: dict[int, str] = {}
    for line in proc.stdout.splitlines():
        sha, _, subject = line.partition(" ")
        tail = subject.rsplit("(#", 1)[-1]
        if subject.endswith(")") and tail[:-1].isdigit():
            out.setdefault(int(tail[:-1]), sha)
    return out


def _commit_time(repo: Path, sha: str) -> datetime | str:
    """The commit instant, or the reason git could not resolve it (one arc, not the run)."""
    proc = _git(repo, "show", "-s", "--format=%cI", sha)
    if proc.returncode != 0:
        return f"git cannot resolve merge commit {sha}: {proc.stderr.strip()}"
    return _ts(proc.stdout.strip())


def _merge_instant(
    repo: Path, head: dict, squash: dict[int, str] | str
) -> tuple[datetime, str] | str:
    """(merge instant, its source) for one arc, or the reason it cannot be resolved."""
    if head.get("merge_sha"):
        sha, source = head["merge_sha"], "reservation"
    elif isinstance(squash, str):
        return squash
    else:
        sha, source = squash.get(head.get("pr")), "git-subject"
    if not sha:
        return "merged with no merge_sha and no squash commit naming its PR"
    at = _commit_time(repo, sha)
    return at if isinstance(at, str) else (at, source)


def _merged_heads() -> list[tuple[str, dict]]:
    """(arc_id, head) for every merged reservation, through the canonical reader."""
    try:
        root = reservations.reservations_root()
        if not root.is_dir():
            raise StoreError(f"reservation store not found at {root}")
        arcs = sorted(p.name for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))
        heads = [(arc, reservations.current(arc)) for arc in arcs]
    except (reservations.ReservationError, OSError, json.JSONDecodeError) as exc:
        raise StoreError(f"reservation store unreadable: {exc!r}") from exc
    return [(arc, h[1]) for arc, h in heads if h is not None and h[1].get("state") == "merged"]


def load(gate_log: Path, repo: Path, door_dir: Path) -> tuple[list[Timeline], list[Unmeasured]]:
    """Every merged reservation as a Timeline, or as Unmeasured with the reason."""
    heads = _merged_heads()
    try:
        rows = [json.loads(line) for line in gate_log.read_text().splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        raise StoreError(f"gate log unreadable at {gate_log}: {exc}") from exc
    last_review = _last_review(rows)
    releases = _releases(door_dir)
    squash = _squash_commits(repo)
    timelines: list[Timeline] = []
    unmeasured: list[Unmeasured] = []
    for arc, head in heads:
        resolved = _merge_instant(repo, head, squash)
        if isinstance(resolved, str):
            unmeasured.append(Unmeasured(arc, _ts(head["reserved_at"]), resolved))
            continue
        merged, source = resolved
        timelines.append(
            Timeline(
                arc_id=arc,
                pr=head.get("pr"),
                reserved=_ts(head["reserved_at"]),
                review_start=_verify_start(head),
                last_review=last_review.get(arc),
                merged=merged,
                released=releases.get(arc),
                lanes=arc_metrics.lanes_at_open(head),
                merged_source=source,
            )
        )
    return timelines, unmeasured


# ── CLI ──────────────────────────────────────────────────────────────────────


def _fmt(v: float | int | None) -> str:
    return "-" if v is None else f"{v:.0f}"


def render(timelines: list[Timeline], unmeasured: list[Unmeasured]) -> str:
    lines = [f"{'arc':<40} {'pr':>5} {'lanes':>7} " + " ".join(f"{p:>8}" for p in PHASES)]
    for t in timelines:
        ph = phases(t)
        lines.append(
            f"{t.arc_id:<40} {t.pr or '-':>5} {cohort_label(t.lanes):>7} "
            + " ".join(f"{_fmt(ph[p]):>8}" for p in PHASES)
        )
    s = summarize(timelines)
    lines.append("")
    lines.append("minutes      " + " ".join(f"{p:>8}" for p in PHASES))
    for stat in ("mean", "median", "n"):
        lines.append(f"{stat:<12} " + " ".join(f"{_fmt(s[p][stat]):>8}" for p in PHASES))
    lines.append("")
    lines.append("total by lanes at open    n     mean   median")
    for key, c in by_cohort(timelines).items():
        stats = f"{_fmt(c['n']):>4} {_fmt(c['mean']):>8} {_fmt(c['median']):>8}"
        lines.append(f"  {cohort_label(key):<20} {stats}")
    lines.append(
        f"goal: mean total <= {GOAL_MEAN_MINUTES:.0f} min -> {goal_verdict(s['total']['mean'])}"
    )
    lines.extend(f"unmeasured: {u.arc_id} ({u.reason})" for u in unmeasured)
    return "\n".join(lines)


def _positive_int(value: str) -> int:
    n = int(value)
    if n < 1:
        raise argparse.ArgumentTypeError(f"must be >= 1, got {n}")
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--last",
        type=_positive_int,
        default=30,
        help="report the N most recently reserved merged arcs",
    )
    ap.add_argument("--json", action="store_true", help="emit the phases and summary as JSON")
    args = ap.parse_args(argv)
    try:
        timelines, unmeasured = load(GATE_LOG, REPO, merge_door.DOOR)
    except StoreError as exc:
        print(f"arc_wallclock: {exc}", file=sys.stderr)
        return 2
    window, unmeasured = latest(timelines, unmeasured, args.last)
    if args.json:
        print(
            json.dumps(
                {
                    "arcs": [
                        {
                            "arc_id": t.arc_id,
                            "pr": t.pr,
                            "lanes": t.lanes,
                            "merged_source": t.merged_source,
                            **phases(t),
                        }
                        for t in window
                    ],
                    "summary": summarize(window),
                    "by_lanes": {cohort_label(k): v for k, v in by_cohort(window).items()},
                    "goal": goal_verdict(summarize(window)["total"]["mean"]),
                    "unmeasured": [{"arc_id": u.arc_id, "reason": u.reason} for u in unmeasured],
                },
                indent=2,
            )
        )
    else:
        print(render(window, unmeasured))
    return 0


if __name__ == "__main__":
    sys.exit(main())

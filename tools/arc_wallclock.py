#!/usr/bin/env python3
"""Per-arc wall-clock, the tracked outcome of spec v1.9 (C-HE-28 §2, X9h).

The goal the spec records: an arc lands in a mean of at most 60 minutes, in one lane or
in parallel lanes. X9h replaces C-HE-28 §2's correlation with this measure, correlated
against `concurrent_lanes_at_open`. It reads the stores the loop already writes:

- the reservation (C-HE-03), through `reservations.current`: reserved_at, PR, merge sha
  and the `concurrent_lanes_at_open` cohort key;
- the gate log (C-HE-24): the first and last review row for the arc;
- git: when the merge commit landed on main;
- the merge door (C-HE-06): the `released.<token>` record, whose mtime `_move_lease`
  stamps immediately before the rename that releases the lease.

Phases, in minutes:

    build     reserved      -> first review row
    review    first review  -> last review row
    to_merge  last review   -> merge commit   (CI wait, gate rows, the door's merge step)
    door      merge commit  -> lease release  (post-merge CI, refresh or lit step)
    total     reserved      -> lease release

A phase whose endpoint the stores never recorded is None and is left out of that phase's
statistics; `total` is never computed from a substitute endpoint. The summary is reported
over all arcs and per `concurrent_lanes_at_open` cohort (`unrecorded` for reservations
older than the sensor).

The merge instant comes from the reservation's merge_sha; when an older reservation
lacks one, it is resolved from the squash commit on main whose subject ends `(#<pr>)`,
and the row says so (`merged_source`). A merged arc whose merge instant cannot be
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
    first_review: datetime | None
    last_review: datetime | None
    merged: datetime
    released: datetime | None
    #: the C-HE-28 cohort key; None for reservations older than the sensor
    concurrent_lanes_at_open: int | None
    #: where `merged` came from: the reservation's merge_sha, or the squash commit on
    #: main whose subject names the PR (landings older than the door's merge_sha record)
    merged_source: str = "reservation"


@dataclass(frozen=True)
class Unmeasured:
    arc_id: str
    reason: str


# ── pure core ────────────────────────────────────────────────────────────────


def _minutes(start: datetime | None, end: datetime | None) -> float | None:
    return None if start is None or end is None else (end - start).total_seconds() / 60.0


def phases(t: Timeline) -> dict[str, float | None]:
    """Phase durations in minutes; a phase whose endpoint was never recorded is None."""
    # [LAW:dataflow-not-control-flow] every phase is computed every time; absence flows
    # through as None rather than branching the set of phases
    return {
        "build": _minutes(t.reserved, t.first_review),
        "review": _minutes(t.first_review, t.last_review),
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


def cohort_key(t: Timeline) -> str:
    return "unrecorded" if t.concurrent_lanes_at_open is None else str(t.concurrent_lanes_at_open)


def by_cohort(timelines: list[Timeline]) -> dict[str, dict[str, float | int | None]]:
    """The total-phase summary per `concurrent_lanes_at_open` cohort (C-HE-28 §2, X9h)."""
    keys = sorted({cohort_key(t) for t in timelines}, key=lambda k: (not k.isdigit(), k.zfill(4)))
    return {k: summarize([t for t in timelines if cohort_key(t) == k])["total"] for k in keys}


def latest(timelines: list[Timeline], n: int) -> list[Timeline]:
    """The n most recently merged; n >= 1 is guaranteed by `_positive_int` at the CLI."""
    return sorted(timelines, key=lambda t: t.merged)[-n:]


def goal_verdict(mean_total: float | None) -> str:
    if mean_total is None:
        return "no arcs with a recorded release"
    return "MET" if mean_total <= GOAL_MEAN_MINUTES else "NOT MET"


# ── effectful edge: read the stores ──────────────────────────────────────────


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _review_bounds(rows: list[dict]) -> dict[str, tuple[datetime, datetime]]:
    bounds: dict[str, tuple[datetime, datetime]] = {}
    for r in rows:
        if not str(r.get("producer", "")).startswith(REVIEW_PRODUCER_PREFIXES):
            continue
        at = _ts(r["ts"])
        lo, hi = bounds.get(r["arc_id"], (at, at))
        bounds[r["arc_id"]] = (min(lo, at), max(hi, at))
    return bounds


def _releases(door_dir: Path) -> dict[str, datetime]:
    """Release instant per reservation: the mtime `_move_lease` stamps on `released.<T>`."""
    out: dict[str, datetime] = {}
    for released in door_dir.glob("released.*"):
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


def _squash_commits(repo: Path) -> dict[int, str]:
    """PR number -> squash commit on origin/main, from subjects ending `(#<pr>)`."""
    proc = _git(repo, "log", "--first-parent", "--format=%H %s", "origin/main")
    if proc.returncode != 0:
        raise StoreError(f"git cannot read origin/main: {proc.stderr.strip()}")
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


def load(
    gate_log: Path = GATE_LOG, repo: Path = REPO, door_dir: Path = merge_door.DOOR
) -> tuple[list[Timeline], list[Unmeasured]]:
    """Every merged reservation as a Timeline, or as Unmeasured with the reason."""
    heads = _merged_heads()
    try:
        rows = [json.loads(line) for line in gate_log.read_text().splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        raise StoreError(f"gate log unreadable at {gate_log}: {exc}") from exc
    review = _review_bounds(rows)
    releases = _releases(door_dir)
    squash = _squash_commits(repo)
    timelines: list[Timeline] = []
    unmeasured: list[Unmeasured] = []
    for arc, head in heads:
        sha, source = head.get("merge_sha"), "reservation"
        if not sha:
            sha, source = squash.get(head.get("pr")), "git-subject"
        merged = (
            _commit_time(repo, sha)
            if sha
            else "merged with no merge_sha and no squash commit naming its PR"
        )
        if isinstance(merged, str):
            unmeasured.append(Unmeasured(arc, merged))
            continue
        first_last = review.get(arc)
        timelines.append(
            Timeline(
                arc_id=arc,
                pr=head.get("pr"),
                reserved=_ts(head["reserved_at"]),
                first_review=first_last[0] if first_last else None,
                last_review=first_last[1] if first_last else None,
                merged=merged,
                released=releases.get(arc),
                concurrent_lanes_at_open=head.get("concurrent_lanes_at_open"),
                merged_source=source,
            )
        )
    return timelines, unmeasured


# ── CLI ──────────────────────────────────────────────────────────────────────


def _fmt(v: float | int | None) -> str:
    return "-" if v is None else f"{v:.0f}"


def render(timelines: list[Timeline], unmeasured: list[Unmeasured]) -> str:
    lines = [f"{'arc':<40} {'pr':>5} {'lanes':>5} " + " ".join(f"{p:>8}" for p in PHASES)]
    for t in timelines:
        ph = phases(t)
        lines.append(
            f"{t.arc_id:<40} {t.pr or '-':>5} {cohort_key(t)[:5]:>5} "
            + " ".join(f"{_fmt(ph[p]):>8}" for p in PHASES)
        )
    s = summarize(timelines)
    lines.append("")
    lines.append("minutes      " + " ".join(f"{p:>8}" for p in PHASES))
    for stat in ("mean", "median", "n"):
        lines.append(f"{stat:<12} " + " ".join(f"{_fmt(s[p][stat]):>8}" for p in PHASES))
    lines.append("")
    lines.append("total by concurrent_lanes_at_open    n     mean   median")
    for key, c in by_cohort(timelines).items():
        lines.append(f"  {key:<32} {_fmt(c['n']):>4} {_fmt(c['mean']):>8} {_fmt(c['median']):>8}")
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
        "--last", type=_positive_int, default=30, help="report the N most recently merged arcs"
    )
    ap.add_argument("--json", action="store_true", help="emit the phases and summary as JSON")
    args = ap.parse_args(argv)
    try:
        timelines, unmeasured = load()
    except StoreError as exc:
        print(f"arc_wallclock: {exc}", file=sys.stderr)
        return 2
    window = latest(timelines, args.last)
    if args.json:
        print(
            json.dumps(
                {
                    "arcs": [
                        {
                            "arc_id": t.arc_id,
                            "pr": t.pr,
                            "concurrent_lanes_at_open": t.concurrent_lanes_at_open,
                            **phases(t),
                        }
                        for t in window
                    ],
                    "summary": summarize(window),
                    "by_cohort": by_cohort(window),
                    "goal": goal_verdict(summarize(window)["total"]["mean"]),
                    "unmeasured": [u.__dict__ for u in unmeasured],
                },
                indent=2,
            )
        )
    else:
        print(render(window, unmeasured))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Per-arc wall-clock, the tracked outcome of spec v1.9 (C-HE-28 §2, X9h).

The goal the spec records: an arc lands in a mean of at most 60 minutes, in one lane or
in parallel lanes. This tool measures it from the stores the loop already writes:

- the reservation (C-HE-03): when the arc was reserved, its PR and merge sha;
- the gate log (C-HE-24): the first and last review row for the arc;
- git: when the merge commit landed on main;
- the merge door (C-HE-06): when the lease holding the landing was released.

Phases, in minutes:

    build     reserved      -> first review row
    review    first review  -> last review row
    to_merge  last review   -> merge commit   (CI wait, gate rows, the door's merge step)
    door      merge commit  -> lease release  (post-merge CI, refresh or lit step)
    total     reserved      -> lease release, or -> merge commit when no release is recorded

The merge instant comes from the reservation's merge_sha; when an older reservation
lacks one, it is resolved from the squash commit on main whose subject ends `(#<pr>)`,
and the row says so (`merged_source`). An arc with neither is reported as unmeasured
with that reason, never dropped silently.

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
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_metrics import QUEUE_DIR  # [LAW:one-source-of-truth] the one QUEUE_DIR resolver

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
        "total": _minutes(t.reserved, t.released or t.merged),
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


def latest(timelines: list[Timeline], n: int) -> list[Timeline]:
    """The n most recently merged; n >= 1 is guaranteed by `_positive_int` at the CLI."""
    return sorted(timelines, key=lambda t: t.merged)[-n:]


# ── effectful edge: read the stores ──────────────────────────────────────────


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _read_json(path: Path) -> dict:
    """One record from a store. A vanished file stays FileNotFoundError (the door's gc may
    remove a marker mid-walk); any other unreadable record is a StoreError (exit 2)."""
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        raise
    except (OSError, json.JSONDecodeError) as exc:
        raise StoreError(f"unreadable record {path}: {exc}") from exc


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
    """Release instant per reservation: the transition marker of each released lease."""
    out: dict[str, datetime] = {}
    for released in door_dir.glob("released.*"):
        token = released.name.split(".", 1)[1]
        try:
            arc = _read_json(released)["reservation_id"]
            at = _ts(_read_json(door_dir / f"transition.{token}")["created_at"])
        except FileNotFoundError:
            # the door's 30-day gc (merge_door.py) removed the pair: the release is
            # unrecorded, so the arc's door phase stays None rather than guessed
            continue
        out[arc] = max(out.get(arc, at), at)
    return out


def _commit_time(repo: Path, sha: str) -> datetime:
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", "-s", "--format=%cI", sha],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise StoreError(f"git cannot read merge commit {sha}: {proc.stderr.strip()}")
    return _ts(proc.stdout.strip())


def _squash_commit(repo: Path, pr: int) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo), "log", "--first-parent", "--format=%H %s", "origin/main"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise StoreError(f"git cannot read origin/main: {proc.stderr.strip()}")
    suffix = f"(#{pr})"
    return next(
        (line.split(" ", 1)[0] for line in proc.stdout.splitlines() if line.endswith(suffix)), None
    )


def load(
    queue_dir: Path = QUEUE_DIR, gate_log: Path = GATE_LOG, repo: Path = REPO
) -> tuple[list[Timeline], list[Unmeasured]]:
    """Every merged reservation as a Timeline; bypassed or unreadable arcs as Unmeasured."""
    res_dir = queue_dir / "reservations"
    if not res_dir.is_dir():
        raise StoreError(f"reservation store not found at {res_dir}")
    try:
        rows = [json.loads(line) for line in gate_log.read_text().splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        raise StoreError(f"gate log unreadable at {gate_log}: {exc}") from exc
    review = _review_bounds(rows)
    releases = _releases(queue_dir / "merge-door")
    timelines: list[Timeline] = []
    unmeasured: list[Unmeasured] = []
    for arc_dir in sorted(
        p for p in res_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
    ):
        gens = sorted(arc_dir.glob("*.json"), key=lambda p: int(p.stem))
        if not gens:
            continue
        head = _read_json(gens[-1])
        if head.get("state") != "merged":
            continue
        sha, source = head.get("merge_sha"), "reservation"
        if not sha and head.get("pr"):
            sha, source = _squash_commit(repo, head["pr"]), "git-subject"
        if not sha:
            unmeasured.append(
                Unmeasured(
                    arc_dir.name, "merged with no merge_sha and no squash commit naming its PR"
                )
            )
            continue
        first_last = review.get(arc_dir.name)
        timelines.append(
            Timeline(
                arc_id=arc_dir.name,
                pr=head.get("pr"),
                reserved=_ts(head["reserved_at"]),
                first_review=first_last[0] if first_last else None,
                last_review=first_last[1] if first_last else None,
                merged=_commit_time(repo, sha),
                released=releases.get(arc_dir.name),
                merged_source=source,
            )
        )
    return timelines, unmeasured


# ── CLI ──────────────────────────────────────────────────────────────────────


def _fmt(v: float | int | None) -> str:
    return "-" if v is None else f"{v:.0f}"


def render(timelines: list[Timeline], unmeasured: list[Unmeasured]) -> str:
    lines = [f"{'arc':<40} {'pr':>5} " + " ".join(f"{p:>8}" for p in PHASES)]
    for t in timelines:
        ph = phases(t)
        lines.append(
            f"{t.arc_id:<40} {t.pr or '-':>5} " + " ".join(f"{_fmt(ph[p]):>8}" for p in PHASES)
        )
    s = summarize(timelines)
    lines.append("")
    lines.append("minutes      " + " ".join(f"{p:>8}" for p in PHASES))
    for stat in ("mean", "median", "n"):
        lines.append(f"{stat:<12} " + " ".join(f"{_fmt(s[p][stat]):>8}" for p in PHASES))
    mean_total = s["total"]["mean"]
    verdict = (
        "no arcs"
        if mean_total is None
        else ("MET" if mean_total <= GOAL_MEAN_MINUTES else "NOT MET")
    )
    lines.append(f"goal: mean total <= {GOAL_MEAN_MINUTES:.0f} min -> {verdict}")
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
                    "arcs": [{"arc_id": t.arc_id, "pr": t.pr, **phases(t)} for t in window],
                    "summary": summarize(window),
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

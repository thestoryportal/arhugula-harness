"""Per-arc transcript cost extractor (U-HE-48, C-HE-25 v1.6 X6e).

Derives an arc's API cost from its session transcript per the [B] audit method
(`.harness/session-audit-2026-08-26-u-he-35-workflow-efficiency.md` "Evidence
and method"): usage is deduplicated by `requestId` -- a transcript stores one
assistant record per content block (thinking, text, tool_use), each carrying a
copy of the SAME usage block, so naive sums double-count by ~1.9x -- and ranked
by the IET index (input + 1.25*cache-write + 0.1*cache-read + 5*output).
Subagent transcripts under `<transcript-dir>/<stem>/subagents/` are included.
Stage windows are cut at transcript event timestamps supplied via `--cut`.

Usage:  just arc-cost <transcript> [--cut ISO ...] [--json]

Exit codes: 0 success / 2 bad input (missing file, no usage records, bad cut).
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

# [LAW:one-source-of-truth] the IET price ratios live here and nowhere else
IET_CACHE_WRITE = 1.25
IET_CACHE_READ = 0.1
IET_OUTPUT = 5.0


class CostError(ValueError):
    """Bad input: the transcript cannot yield a truthful cost figure."""


@dataclass(frozen=True)
class Call:
    """One deduplicated API call: the single usage block behind a requestId."""

    ts: datetime
    input: int
    cache_write: int
    cache_read: int
    output: int


@dataclass(frozen=True)
class Totals:
    calls: int = 0
    input: int = 0
    cache_write: int = 0
    cache_read: int = 0
    output: int = 0

    @property
    def iet(self) -> float:
        return (
            self.input
            + IET_CACHE_WRITE * self.cache_write
            + IET_CACHE_READ * self.cache_read
            + IET_OUTPUT * self.output
        )

    def as_dict(self) -> dict:
        return {
            "calls": self.calls,
            "input": self.input,
            "cache_write": self.cache_write,
            "cache_read": self.cache_read,
            "output": self.output,
            "iet": round(self.iet, 2),
        }


def parse_ts(s: str, *, what: str) -> datetime:
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CostError(f"{what}: not an ISO timestamp: {s!r}") from exc
    # a naive timestamp means UTC here: transcripts stamp Z everywhere
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def dedupe_calls(records: list[dict], *, source: str) -> list[Call]:
    """One Call per requestId, first occurrence wins (all copies are identical)."""
    calls: dict[str, Call] = {}
    for i, r in enumerate(records):
        if r.get("type") != "assistant":
            continue
        usage = (r.get("message") or {}).get("usage")
        if not usage:
            continue
        rid = r.get("requestId")
        # [LAW:no-silent-failure] a usage block with no requestId cannot be
        # deduplicated; a fallback key would silently change the count's meaning
        if not rid:
            raise CostError(f"{source}: assistant record {i} carries usage but no requestId")
        ts = r.get("timestamp")
        if not ts:
            raise CostError(f"{source}: assistant record {i} ({rid}) has no timestamp")
        if rid not in calls:
            calls[rid] = Call(
                ts=parse_ts(ts, what=f"{source} record {i}"),
                input=usage.get("input_tokens", 0),
                cache_write=usage.get("cache_creation_input_tokens", 0),
                cache_read=usage.get("cache_read_input_tokens", 0),
                output=usage.get("output_tokens", 0),
            )
    return sorted(calls.values(), key=lambda c: c.ts)


def totals(calls: list[Call]) -> Totals:
    return Totals(
        calls=len(calls),
        input=sum(c.input for c in calls),
        cache_write=sum(c.cache_write for c in calls),
        cache_read=sum(c.cache_read for c in calls),
        output=sum(c.output for c in calls),
    )


def windows(main: list[Call], subs: list[Call], cuts: list[datetime]) -> list[dict]:
    """Partition both call sets at the cut timestamps: [start,c1), [c1,c2), ..."""
    if cuts != sorted(cuts):
        raise CostError("--cut timestamps must be in ascending order")

    def in_window(c: Call, lo: datetime | None, hi: datetime | None) -> bool:
        return (lo is None or c.ts >= lo) and (hi is None or c.ts < hi)

    bounds: list[datetime | None] = [None, *cuts, None]
    return [
        {
            "start": lo.isoformat() if lo else None,
            "end": hi.isoformat() if hi else None,
            "main": totals([c for c in main if in_window(c, lo, hi)]).as_dict(),
            "subagents": totals([c for c in subs if in_window(c, lo, hi)]).as_dict(),
        }
        for lo, hi in itertools.pairwise(bounds)
    ]


# -- edges: file IO and rendering ------------------------------------------


def read_records(path: Path) -> list[dict]:
    try:
        lines = path.read_text().splitlines()
    except OSError as exc:
        raise CostError(f"cannot read transcript: {exc}") from exc
    records = []
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise CostError(f"{path.name}:{n}: not JSON: {exc}") from exc
    return records


def subagent_files(transcript: Path) -> list[Path]:
    # sibling directory named by the transcript stem, per the [B] layout
    return sorted((transcript.parent / transcript.stem / "subagents").glob("agent-*.jsonl"))


def cost_report(transcript: Path, cuts: list[datetime]) -> dict:
    main = dedupe_calls(read_records(transcript), source=transcript.name)
    if not main:
        # [LAW:no-silent-failure] zero usage records is a wrong input (not this
        # harness's transcript shape), never a measured zero-cost arc
        raise CostError(f"{transcript}: no assistant usage records -- not a session transcript?")
    sub_paths = subagent_files(transcript)
    subs = [c for p in sub_paths for c in dedupe_calls(read_records(p), source=p.name)]
    report = {
        "transcript": str(transcript),
        "main": totals(main).as_dict(),
        "subagents": {"files": len(sub_paths), **totals(subs).as_dict()},
        "total_iet": round(totals(main).iet + totals(subs).iet, 2),
    }
    if cuts:
        report["windows"] = windows(main, sorted(subs, key=lambda c: c.ts), cuts)
    return report


def render(report: dict) -> str:
    def line(name: str, t: dict) -> str:
        return (
            f"{name:<10} {t['calls']:>5} calls  {t['input']:>8} in  "
            f"{t['cache_write']:>11,} cw  {t['cache_read']:>13,} cr  "
            f"{t['output']:>9,} out  {t['iet'] / 1e6:>7.2f}M IET"
        )

    out = [f"transcript {report['transcript']}"]
    out.append(line("main", report["main"]))
    out.append(line(f"subagents({report['subagents']['files']})", report["subagents"]))
    out.append(f"{'total':<10} {report['total_iet'] / 1e6:.2f}M IET")
    for i, w in enumerate(report.get("windows", [])):
        span = f"[{w['start'] or 'start'} .. {w['end'] or 'end'})"
        out.append(f"window {i} {span}")
        out.append("  " + line("main", w["main"]))
        out.append("  " + line("subagents", w["subagents"]))
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="arc_cost", description=__doc__)
    p.add_argument("transcript", type=Path, help="session transcript .jsonl")
    p.add_argument(
        "--cut",
        action="append",
        default=[],
        metavar="ISO",
        help="stage-window boundary (repeatable, ascending; transcript event timestamps)",
    )
    p.add_argument("--json", action="store_true", help="machine-readable output")
    args = p.parse_args(argv)
    try:
        cuts = [parse_ts(c, what="--cut") for c in args.cut]
        report = cost_report(args.transcript, cuts)
    except CostError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.json else render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())

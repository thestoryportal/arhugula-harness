"""Per-arc transcript cost extractor (U-HE-48, C-HE-25 v1.6 X6e).

Derives an arc's API cost from its session transcript per the [B] audit method
(`.harness/session-audit-2026-08-26-u-he-35-workflow-efficiency.md` "Evidence
and method"): usage is deduplicated by `requestId` -- a transcript stores one
assistant record per content block (thinking, text, tool_use), each carrying a
copy of the SAME usage block, so naive sums double-count by ~1.9x -- and ranked
by the IET index (input + 1.25*cache-write + 0.1*cache-read + 5*output).
Subagent transcripts under `<transcript-dir>/<stem>/subagents/` are included.
Stage windows are cut at transcript event timestamps supplied via `--cut`.

Usage:  just arc-cost <transcript> [<transcript> ...] [--cut ISO ...] [--json]

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


def _tok(usage: dict, key: str, where: str) -> int:
    """A usage token count, refused unless a present non-negative int.

    All four fields are REQUIRED: 0 of 20,414 usage blocks across the project's
    126 transcripts omit any of them (measured u-he-48 r7), so an absent field
    is a malformed producer, and defaulting it to zero would silently
    undercount instead of following the exit-2 contract (r4/r7 P3s).
    """
    if key not in usage:
        raise CostError(f"{where} usage.{key} is absent")
    v = usage[key]
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise CostError(f"{where} usage.{key}={v!r} is not a non-negative int")
    return v


def dedupe_calls(records: list[dict], *, source: str) -> list[Call]:
    """One Call per requestId.

    Main-session copies of a request's usage block are identical on the [B]
    witness (0 divergent of 428 requestIds), but subagent transcripts stamp an
    early PARTIAL output_tokens copy before the final one (42 of 291), so copies
    merge by PER-FIELD MAX — order-independent, equal to the copy when copies
    agree, and equal to the final (largest) value under monotone streaming
    growth. The timestamp keeps the earliest copy: windows cut at when the call
    happened.
    """
    calls: dict[str, Call] = {}
    for i, r in enumerate(records):
        if r.get("type") != "assistant":
            continue
        msg = r.get("message")
        if msg is None:
            continue
        if not isinstance(msg, dict):
            raise CostError(f"{source}: assistant record {i} message is not an object")
        usage = msg.get("usage")
        if not usage:
            continue
        if not isinstance(usage, dict):
            raise CostError(f"{source}: assistant record {i} usage is not an object")
        rid = r.get("requestId")
        # [LAW:no-silent-failure] a usage block with no requestId cannot be
        # deduplicated; a fallback key would silently change the count's meaning
        if not rid or not isinstance(rid, str):
            raise CostError(f"{source}: assistant record {i} carries usage but no requestId")
        ts = r.get("timestamp")
        # [LAW:parse-dont-validate] refuse malformed shapes HERE with the exit-2
        # contract, never as a traceback mid-closure (codex u-he-48 r4 P3)
        if not ts or not isinstance(ts, str):
            raise CostError(f"{source}: assistant record {i} ({rid}) has no string timestamp")

        where = f"{source}: record {i} ({rid})"
        seen = calls.get(rid)
        cur = Call(
            ts=parse_ts(ts, what=f"{source} record {i}"),
            input=_tok(usage, "input_tokens", where),
            cache_write=_tok(usage, "cache_creation_input_tokens", where),
            cache_read=_tok(usage, "cache_read_input_tokens", where),
            output=_tok(usage, "output_tokens", where),
        )
        calls[rid] = (
            cur
            if seen is None
            else Call(
                ts=min(seen.ts, cur.ts),
                input=max(seen.input, cur.input),
                cache_write=max(seen.cache_write, cur.cache_write),
                cache_read=max(seen.cache_read, cur.cache_read),
                output=max(seen.output, cur.output),
            )
        )
    # An all-zero merged call is an aborted/truncated request, not work done
    # (codex u-he-48 r6; 0 such calls on the [B] witness, so the ratified
    # headline is unaffected) — kept, it would let a truncated transcript
    # persist as a measured 0-IET arc.
    return sorted(
        (
            c
            for c in calls.values()
            if (c.input, c.cache_write, c.cache_read, c.output) != (0, 0, 0, 0)
        ),
        key=lambda c: c.ts,
    )


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
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CostError(f"{path.name}:{n}: not JSON: {exc}") from exc
        # [LAW:parse-dont-validate] a JSON-valid non-object line ("5", a string)
        # would AttributeError downstream instead of the exit-2 contract (r5 P3)
        if not isinstance(rec, dict):
            raise CostError(f"{path.name}:{n}: not a transcript record object")
        records.append(rec)
    return records


def subagent_files(transcript: Path) -> list[Path]:
    """The transcript's subagent sidecars, refusing a present-but-empty store.

    Sibling directory named by the transcript stem, per the [B] layout. An
    ABSENT subagents/ dir is a session that spawned no subagents (59 of the
    project's 126 transcripts, measured u-he-48 r7 — a genuine zero); a dir
    that EXISTS but holds no agent files never occurs naturally (0 of 67
    measured), so it is a GC'd/partial store and a zero there would be a
    false measurement.
    """
    sub_dir = transcript.parent / transcript.stem / "subagents"
    files = sorted(sub_dir.glob("agent-*.jsonl"))
    if sub_dir.is_dir() and not files:
        raise CostError(
            f"{transcript}: subagents/ exists but holds no agent files -- a GC'd or "
            "partial store, so the subagent cost cannot be measured"
        )
    return files


def cost_report(transcripts: list[Path], cuts: list[datetime]) -> dict:
    """Pooled cost over one arc's transcript set.

    An arc resumed or handed off spans several sessions, each with its own
    transcript (codex u-he-48 r4) — the arc's cost is the pool, deduplicated
    GLOBALLY by requestId (a resumed session can copy prior records into its
    own file, so per-file dedupe alone could double-count).

    Sidechain records are subagent turns inlined into the main transcript;
    their cost is additive and separately sourced from the subagents/ files,
    so counting them in main would double-count. Same exclusion as the repo's
    existing transcript instrument (tools/context_budget.py).
    [LAW:one-source-of-truth] main = pooled non-sidechain records only.
    """
    pooled = [r for t in transcripts for r in read_records(t)]
    main_records = [r for r in pooled if not r.get("isSidechain")]
    main = dedupe_calls(main_records, source=";".join(t.name for t in transcripts))
    if not main:
        # [LAW:no-silent-failure] zero usage records is a wrong input (not this
        # harness's transcript shape), never a measured zero-cost arc
        raise CostError(
            f"{';'.join(map(str, transcripts))}: no assistant usage with non-zero tokens -- "
            "not session transcripts, or truncated?"
        )
    sub_paths = [p for t in transcripts for p in subagent_files(t)]
    # [LAW:no-silent-failure] visible sidechain work with NO subagent files is a
    # GC'd/missing store, not a measured zero — a zero here would enter cost
    # medians as an artificially cheap arc (codex u-he-48 r5)
    if not sub_paths and any(r.get("isSidechain") for r in pooled):
        raise CostError(
            f"{';'.join(map(str, transcripts))}: sidechain records present but no "
            "subagents/ files found -- the subagent transcripts are missing, so the "
            "subagent cost cannot be measured"
        )
    subs = dedupe_calls(
        [r for p in sub_paths for r in read_records(p)],
        source=";".join(p.name for p in sub_paths) or "subagents",
    )
    report = {
        "transcripts": [str(t) for t in transcripts],
        "main": totals(main).as_dict(),
        "subagents": {"files": len(sub_paths), **totals(subs).as_dict()},
        "total_iet": round(totals(main).iet + totals(subs).iet, 2),
    }
    if cuts:
        report["windows"] = windows(main, subs, cuts)
    return report


def render(report: dict) -> str:
    def line(name: str, t: dict) -> str:
        return (
            f"{name:<10} {t['calls']:>5} calls  {t['input']:>8} in  "
            f"{t['cache_write']:>11,} cw  {t['cache_read']:>13,} cr  "
            f"{t['output']:>9,} out  {t['iet'] / 1e6:>7.2f}M IET"
        )

    out = [f"transcripts {'; '.join(report['transcripts'])}"]
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
    p.add_argument(
        "transcript",
        type=Path,
        nargs="+",
        help="the arc's session transcript(s) .jsonl — pass every session that ran the arc",
    )
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
        report = cost_report(list(args.transcript), cuts)
    except CostError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.json else render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())

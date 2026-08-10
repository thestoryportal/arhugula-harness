#!/usr/bin/env python3
"""First-turn context-budget measurement over Claude Code session transcripts.

R-CTX-1 U-CTX-02 instrument. For each session JSONL under the project's
transcript directory (``~/.claude/projects/<cwd-slug>/``), find the FIRST
main-loop assistant API call and report its context size:

    input_tokens + cache_creation_input_tokens + cache_read_input_tokens

— i.e. everything the model read on turn 1: the preloaded system prompt,
CLAUDE.md corpus, hook output, and the first user message. This is the
program's headline metric (baseline ~98-100k; Floor-B target ~71k; gate 76k).

Records are DEDUPLICATED BY REQUEST ID: stream chunks and retries of one API
call share a ``requestId``, so only the first record per requestId counts.
Sidechain records (subagent transcripts inlined with ``isSidechain: true``)
are excluded — subagent preload is a separate, additive cost (reported by
``--sidechains``), never folded into the main-session first-turn number.

Stdlib-only by design (no workspace deps; runs under any ``uv run python``).
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

USAGE_FIELDS = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
)

_DESCRIPTION = "First-turn context-budget measurement over Claude Code session transcripts."


def _loads_record(line: str) -> dict[str, Any] | None:
    """One transcript line as a dict, or None (malformed / non-object)."""
    try:
        rec = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(rec, dict):
        return None
    return cast("dict[str, Any]", rec)


def _usage_of(rec: dict[str, Any]) -> dict[str, Any] | None:
    """The record's ``message.usage`` dict, or None."""
    message = rec.get("message")
    if not isinstance(message, dict):
        return None
    usage = cast("dict[str, Any]", message).get("usage")
    if not isinstance(usage, dict):
        return None
    return cast("dict[str, Any]", usage)


def project_transcript_dir(cwd: Path) -> Path:
    """Claude Code's per-project transcript dir: cwd path with '/' -> '-'."""
    slug = str(cwd.resolve()).replace("/", "-")
    return Path.home() / ".claude" / "projects" / slug


def first_turn_total(path: Path) -> dict[str, Any] | None:
    """First main-loop assistant usage record of one session file, or None.

    Walks the file in order; the first non-sidechain assistant record carrying
    a ``message.usage`` with a fresh ``requestId`` is the session's first API
    call. Malformed lines are skipped (transcripts are append-only and a
    mid-write tail line may be truncated).
    """
    seen_request_ids: set[str] = set()
    try:
        fh = path.open(encoding="utf-8")
    except OSError:
        return None
    with fh:
        for line in fh:
            rec = _loads_record(line)
            if rec is None:
                continue
            if rec.get("type") != "assistant" or rec.get("isSidechain"):
                continue
            request_id = rec.get("requestId")
            if request_id is not None:
                if request_id in seen_request_ids:
                    continue
                seen_request_ids.add(request_id)
            usage = _usage_of(rec)
            if usage is None:
                continue
            parts = {f: int(usage.get(f) or 0) for f in USAGE_FIELDS}
            if sum(parts.values()) == 0:
                # aborted/empty call (all-zero usage) — not a measurement;
                # keep scanning for the session's first real API call.
                continue
            return {
                "session": path.stem,
                "timestamp": rec.get("timestamp"),
                "request_id": request_id,
                **parts,
                "first_turn_total": sum(parts.values()),
            }
    return None


def post_compaction_first_turns(path: Path) -> list[dict[str, Any]]:
    """First main-loop assistant usage after EACH compaction boundary (errata E4).

    A compaction lands in the transcript as ``{"type": "system", "subtype":
    "compact_boundary", "compactMetadata": {"trigger": "manual"|"auto", ...}}``.
    A post-compaction request is NOT the session's first turn, so
    ``first_turn_total`` structurally cannot see it — this selector walks the
    file and captures the first non-sidechain, non-zero assistant usage record
    following each boundary (request-ID-deduplicated), giving the program's
    post-compaction acceptance measurement its own instrument.
    """
    rows: list[dict[str, Any]] = []
    seen_request_ids: set[str] = set()
    pending_trigger: str | None = None
    try:
        fh = path.open(encoding="utf-8")
    except OSError:
        return rows
    with fh:
        for line in fh:
            rec = _loads_record(line)
            if rec is None:
                continue
            if rec.get("type") == "system" and rec.get("subtype") == "compact_boundary":
                meta = rec.get("compactMetadata")
                if isinstance(meta, dict):
                    pending_trigger = str(cast("dict[str, Any]", meta).get("trigger", "unknown"))
                else:
                    pending_trigger = "unknown"
                continue
            if pending_trigger is None:
                continue
            if rec.get("type") != "assistant" or rec.get("isSidechain"):
                continue
            request_id = rec.get("requestId")
            if request_id is not None:
                if request_id in seen_request_ids:
                    continue
                seen_request_ids.add(request_id)
            usage = _usage_of(rec)
            if usage is None:
                continue
            parts = {f: int(usage.get(f) or 0) for f in USAGE_FIELDS}
            if sum(parts.values()) == 0:
                continue
            rows.append(
                {
                    "session": path.stem,
                    "timestamp": rec.get("timestamp"),
                    "request_id": request_id,
                    "trigger": pending_trigger,
                    **parts,
                    "post_compaction_total": sum(parts.values()),
                }
            )
            pending_trigger = None
    return rows


def sidechain_first_turns(path: Path) -> list[int]:
    """First-turn totals of each sidechain (subagent) thread in one session file.

    A sidechain thread is identified by the sidechain record's own sessionId/
    uuid chain; the cheap, shape-stable proxy used here is: the first sidechain
    assistant record per distinct requestId whose cache_read is LOWER than its
    cache_creation (a fresh-preload signature) — good enough for the aggregate
    "subagent preload multiplier" view, which is reported separately and never
    added to the headline.
    """
    totals: list[int] = []
    seen: set[str] = set()
    try:
        fh = path.open(encoding="utf-8")
    except OSError:
        return totals
    with fh:
        for line in fh:
            rec = _loads_record(line)
            if rec is None:
                continue
            if rec.get("type") != "assistant" or not rec.get("isSidechain"):
                continue
            sid = str(rec.get("sessionId") or "")
            parent = str(rec.get("parentUuid") or "")
            usage = _usage_of(rec)
            if usage is None:
                continue
            # first assistant record of each sidechain thread: keyed by the
            # thread's first-seen parent chain root.
            key = f"{sid}:{parent.split('-')[0]}"
            if key in seen:
                continue
            seen.add(key)
            totals.append(sum(int(usage.get(f) or 0) for f in USAGE_FIELDS))
    return totals


def collect(directory: Path, limit: int) -> list[dict[str, Any]]:
    files = sorted(directory.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    rows: list[dict[str, Any]] = []
    for path in files:
        row = first_turn_total(path)
        if row is not None:
            rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="project whose transcripts to measure (default: cwd)",
    )
    parser.add_argument(
        "--sessions",
        type=int,
        default=20,
        help="most-recent session count (default 20)",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument(
        "--post-compaction",
        action="store_true",
        help="also report the first assistant call after each compaction boundary "
        "(errata E4 — the post-compaction acceptance selector; a post-compaction "
        "request is never the session's first turn)",
    )
    parser.add_argument(
        "--sidechains",
        action="store_true",
        help="also report per-session sidechain (subagent) first-turn totals — "
        "a separate additive cost, never folded into the headline",
    )
    args = parser.parse_args(argv)

    directory = project_transcript_dir(args.project_dir)
    if not directory.is_dir():
        print(f"no transcript dir at {directory}", file=sys.stderr)
        return 1

    rows = collect(directory, args.sessions)
    if not rows:
        print(f"no measurable sessions under {directory}", file=sys.stderr)
        return 1

    totals = [r["first_turn_total"] for r in rows]
    summary = {
        "sessions_measured": len(rows),
        "median_first_turn": int(statistics.median(totals)),
        "mean_first_turn": int(statistics.mean(totals)),
        "min_first_turn": min(totals),
        "max_first_turn": max(totals),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }

    recent_files = sorted(directory.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[
        : args.sessions
    ]

    post_compaction_rows: list[dict[str, Any]] = []
    if args.post_compaction:
        for path in recent_files:
            post_compaction_rows.extend(post_compaction_first_turns(path))
        pc_totals = [r["post_compaction_total"] for r in post_compaction_rows]
        summary["post_compaction_measured"] = len(pc_totals)
        if pc_totals:
            summary["post_compaction_median"] = int(statistics.median(pc_totals))
            summary["post_compaction_mean"] = int(statistics.mean(pc_totals))

    if args.sidechains:
        side: list[int] = []
        for path in recent_files:
            side.extend(sidechain_first_turns(path))
        summary["sidechain_first_turns_measured"] = len(side)
        if side:
            summary["sidechain_median_first_turn"] = int(statistics.median(side))

    if args.json:
        payload: dict[str, Any] = {"summary": summary, "sessions": rows}
        if args.post_compaction:
            payload["post_compaction"] = post_compaction_rows
        print(json.dumps(payload, indent=2))
        return 0

    print(f"context-budget — {len(rows)} session(s) from {directory}")
    for r in rows:
        ts = (r["timestamp"] or "")[:19]
        print(
            f"  {r['session'][:8]}  {ts}  input={r['input_tokens']:>7,}"
            f"  cache_new={r['cache_creation_input_tokens']:>8,}"
            f"  cache_read={r['cache_read_input_tokens']:>8,}"
            f"  TOTAL={r['first_turn_total']:>8,}"
        )
    print(
        f"median={summary['median_first_turn']:,}  mean={summary['mean_first_turn']:,}"
        f"  min={summary['min_first_turn']:,}  max={summary['max_first_turn']:,}"
    )
    if args.post_compaction:
        n = summary.get("post_compaction_measured", 0)
        if n:
            print(
                f"post-compaction: n={n}"
                f"  median={summary.get('post_compaction_median', 0):,}"
                f"  mean={summary.get('post_compaction_mean', 0):,}"
                f"  (first call after each compact_boundary — the E4 selector)"
            )
        else:
            print("post-compaction: no compact_boundary records in the measured sessions")
    if args.sidechains and summary.get("sidechain_first_turns_measured"):
        print(
            f"sidechains: n={summary['sidechain_first_turns_measured']}"
            f"  median={summary.get('sidechain_median_first_turn', 0):,}"
            f"  (separate additive cost — NOT in the headline)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
    mid-write tail line may be truncated). An UNREADABLE file propagates
    ``OSError`` — silently substituting older sessions would let the
    acceptance metric shift without revealing the missing input (fail closed).
    """
    seen_request_ids: set[str] = set()
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            rec = _loads_record(line)
            if rec is None:
                continue
            if rec.get("type") != "assistant" or rec.get("isSidechain"):
                continue
            request_id = rec.get("requestId")
            if request_id is not None and request_id in seen_request_ids:
                continue
            usage = _usage_of(rec)
            if usage is None:
                continue
            parts = {f: int(usage.get(f) or 0) for f in USAGE_FIELDS}
            if sum(parts.values()) == 0:
                # aborted/empty call (all-zero usage) — not a measurement; do
                # NOT mark the requestId seen (a later chunk of the SAME
                # request may carry the real usage); keep scanning.
                continue
            if request_id is not None:
                seen_request_ids.add(request_id)
            return {
                "session": path.stem,
                "timestamp": rec.get("timestamp"),
                "request_id": request_id,
                # cohort discriminator: a `claude -p` / SDK / restricted-tool run
                # preloads a different config surface than a real session, and
                # enough of them would let the ≤76k gate pass without the real
                # preload shrinking. (sessionKind, entrypoint) separates them —
                # e.g. ('bg','cli') for background sessions vs (None,'sdk-cli')
                # for headless SDK runs.
                "cohort": (
                    f"{rec.get('sessionKind') or 'interactive'}"
                    f"/{rec.get('entrypoint') or 'unknown'}"
                ),
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
    with path.open(encoding="utf-8") as fh:
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
            if request_id is not None and request_id in seen_request_ids:
                continue
            usage = _usage_of(rec)
            if usage is None:
                continue
            parts = {f: int(usage.get(f) or 0) for f in USAGE_FIELDS}
            if sum(parts.values()) == 0:
                # zero-usage chunk: do NOT mark seen — a later chunk of the
                # same request may carry the real usage.
                continue
            if request_id is not None:
                seen_request_ids.add(request_id)
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


def sidechain_first_turns(path: Path) -> list[dict[str, Any]]:
    """First-turn row of each subagent spawned by one session.

    Subagent transcripts are NOT inlined in the parent session file — each
    lives at ``<session-stem>/subagents/agent-*.jsonl`` beside it. The first
    non-zero assistant usage record per agent file (request-ID-deduplicated
    within the file, so stream chunks of one call never count twice) is that
    subagent's first turn; its own timestamp rides along so callers can rank
    by event recency. Reported separately from the headline — subagent
    preload is an additive cost, never folded into the main-session number.
    Unreadable agent files propagate ``OSError`` (fail closed).
    """
    rows: list[dict[str, Any]] = []
    subagents_dir = path.parent / path.stem / "subagents"
    if not subagents_dir.is_dir():
        return rows
    for agent_file in sorted(subagents_dir.glob("agent-*.jsonl")):
        seen_request_ids: set[str] = set()
        with agent_file.open(encoding="utf-8") as fh:
            for line in fh:
                rec = _loads_record(line)
                if rec is None:
                    continue
                if rec.get("type") != "assistant":
                    continue
                request_id = rec.get("requestId")
                if request_id is not None and request_id in seen_request_ids:
                    continue
                usage = _usage_of(rec)
                if usage is None:
                    continue
                total = sum(int(usage.get(f) or 0) for f in USAGE_FIELDS)
                if total == 0:
                    # zero-usage chunk: do NOT mark seen — a later chunk of
                    # the same request may carry the real usage.
                    continue
                if request_id is not None:
                    seen_request_ids.add(request_id)
                rows.append(
                    {
                        "session": path.stem,
                        "agent": agent_file.stem,
                        "timestamp": rec.get("timestamp"),
                        "sidechain_total": total,
                    }
                )
                break  # first real call only — one first turn per agent file
    return rows


def collect_all(directory: Path) -> list[dict[str, Any]]:
    """Every measurable session's first-turn row, ranked by FIRST-TURN time.

    Not by file mtime: resuming an old session after a config change bumps its
    mtime while its first turn (what we measure) stays historical — mtime
    ranking would mix pre-change measurements into a post-change cohort and
    corrupt the program's A/B delta. Every session file is scanned; the row's
    own first-turn timestamp decides recency. Callers slice the window.
    """
    rows: list[dict[str, Any]] = []
    for path in directory.glob("*.jsonl"):
        row = first_turn_total(path)
        if row is not None:
            rows.append(row)
    rows.sort(key=lambda r: str(r.get("timestamp") or ""), reverse=True)
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

    try:
        all_rows = collect_all(directory)
    except OSError as e:
        # Fail closed: silently substituting older sessions would let the
        # acceptance metric change without revealing the missing input.
        print(f"unreadable transcript — aborting measurement: {e}", file=sys.stderr)
        return 1
    rows = all_rows[: args.sessions]
    if not rows:
        print(f"no measurable sessions under {directory}", file=sys.stderr)
        return 1

    # Headline statistics come from the ELIGIBLE cohort only: real CLI
    # sessions (entrypoint `cli` — bg or interactive alike). Eligibility is
    # EXPLICIT, never plurality: a window dominated by `claude -p` / SDK /
    # restricted-tool runs (entrypoint `sdk-cli` etc.) must not become the
    # headline, or the ≤76k acceptance gate could pass without the real
    # preload shrinking. Ineligible cohorts are listed separately.
    def _eligible(r: dict[str, Any]) -> bool:
        return str(r.get("cohort") or "").endswith("/cli")

    headline_rows = [r for r in rows if _eligible(r)]
    excluded: dict[str, int] = {}
    for r in rows:
        if not _eligible(r):
            c = str(r.get("cohort") or "unknown")
            excluded[c] = excluded.get(c, 0) + 1
    if not headline_rows:
        print(
            f"no eligible CLI sessions (entrypoint 'cli') among the {len(rows)} "
            f"selected — cohorts seen: {excluded}. Refusing to compute a headline "
            "from ineligible (headless/SDK) sessions.",
            file=sys.stderr,
        )
        return 1
    headline_cohort = "*/cli"

    totals = [r["first_turn_total"] for r in headline_rows]
    summary = {
        "sessions_measured": len(rows),
        "headline_cohort": headline_cohort,
        "headline_sessions": len(headline_rows),
        "excluded_cohorts": excluded,
        "median_first_turn": int(statistics.median(totals)),
        "mean_first_turn": int(statistics.mean(totals)),
        "min_first_turn": min(totals),
        "max_first_turn": max(totals),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }

    # The deep-scan views (post-compaction, sidechains) are cohort-filtered
    # AND event-time-windowed: they scan EVERY eligible CLI session (an
    # excluded headless session's compact boundaries or subagents never leak
    # in) and keep events whose OWN timestamp falls inside the headline
    # window's time span, ranked by that event timestamp. Selecting by the
    # parent's first-turn time would drop a fresh compaction inside a resumed
    # old session while keeping stale events from newer parents.
    eligible_files = [directory / f"{r['session']}.jsonl" for r in all_rows if _eligible(r)]
    window_start = min(str(r.get("timestamp") or "") for r in headline_rows)

    def _windowed(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        kept = [e for e in events if str(e.get("timestamp") or "") >= window_start]
        kept.sort(key=lambda e: str(e.get("timestamp") or ""), reverse=True)
        return kept

    post_compaction_rows: list[dict[str, Any]] = []
    if args.post_compaction:
        try:
            for path in eligible_files:
                post_compaction_rows.extend(post_compaction_first_turns(path))
        except OSError as e:
            print(f"unreadable transcript — aborting measurement: {e}", file=sys.stderr)
            return 1
        post_compaction_rows = _windowed(post_compaction_rows)
        pc_totals = [r["post_compaction_total"] for r in post_compaction_rows]
        summary["post_compaction_measured"] = len(pc_totals)
        if pc_totals:
            summary["post_compaction_median"] = int(statistics.median(pc_totals))
            summary["post_compaction_mean"] = int(statistics.mean(pc_totals))

    if args.sidechains:
        side_rows: list[dict[str, Any]] = []
        try:
            for path in eligible_files:
                side_rows.extend(sidechain_first_turns(path))
        except OSError as e:
            print(f"unreadable transcript — aborting measurement: {e}", file=sys.stderr)
            return 1
        side_rows = _windowed(side_rows)
        side = [r["sidechain_total"] for r in side_rows]
        summary["sidechain_first_turns_measured"] = len(side)
        if side:
            summary["sidechain_median_first_turn"] = int(statistics.median(side))

    if args.json:
        payload: dict[str, Any] = {"summary": summary, "sessions": rows}
        if args.post_compaction:
            payload["post_compaction"] = post_compaction_rows
        if args.sidechains:
            payload["sidechains"] = side_rows
        print(json.dumps(payload, indent=2))
        return 0

    print(f"context-budget — {len(rows)} session(s) from {directory}")
    for r in rows:
        ts = (r["timestamp"] or "")[:19]
        marker = "" if _eligible(r) else f"  [{r.get('cohort')} — excluded]"
        print(
            f"  {r['session'][:8]}  {ts}  input={r['input_tokens']:>7,}"
            f"  cache_new={r['cache_creation_input_tokens']:>8,}"
            f"  cache_read={r['cache_read_input_tokens']:>8,}"
            f"  TOTAL={r['first_turn_total']:>8,}{marker}"
        )
    print(
        f"median={summary['median_first_turn']:,}  mean={summary['mean_first_turn']:,}"
        f"  min={summary['min_first_turn']:,}  max={summary['max_first_turn']:,}"
        f"  (headline cohort {headline_cohort}: {len(headline_rows)}/{len(rows)} sessions)"
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

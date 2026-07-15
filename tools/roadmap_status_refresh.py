#!/usr/bin/env python3
"""Deterministic mechanical-skeleton refresh for `.harness/roadmap_status.md`.

This does NOT regenerate the whole file. The `## Next action` prose and the
`Recently completed` Notes cells are agent-authored narrative — not machine-
derivable — and a full-template regen would destroy curated history. What IS
mechanical, and therefore owned here instead of hand-edited, is:

  * the `## Workspace state anchor` table (git_head / workspace_state_hash /
    last_refreshed / latest_retirement_batch / open_fork_doc_count)
  * the `## In-flight (open PRs)` table (derived straight from `gh pr list`)
  * the CAP on `## Recently completed (last 5)` (prepend + truncate to 5,
    dedup by PR/R-NNN ref)
  * the CAP on `## Drift detection log` (prepend + truncate to 10, overflow
    moved — not deleted — into `.harness/roadmap_drift_log_archive.md`)

The hash recipe is byte-parity-critical: `tools/hooks/lib.sh`'s
`hook_state_hash` (consumed by the SessionStart + PostToolUse hooks) computes
the SAME sha256(head|prs|forks|batch)[:12] independently in bash. A silent
mismatch here means every future session falsely reports `[ROADMAP DRIFT]`.
To make that impossible instead of merely tested-against, `compute_state()`
shells out to the EXACT command strings `tools/roadmap-audit/session-start.sh`
runs (not a Python reimplementation) — one source of truth, two callers.
`tools/test_roadmap_status_refresh.py::test_hash_parity_with_bash_hook` pins
`hash12()` against `hook_state_hash` directly as a regression guard.

Usage:
    python tools/roadmap_status_refresh.py --state              # JSON state dump
    python tools/roadmap_status_refresh.py --check               # CI gate
    python tools/roadmap_status_refresh.py --trim-drift-log       # cap+archive only
    python tools/roadmap_status_refresh.py --refresh \\
        --pr "PR #1234" --date 2026-07-16 \\
        --notes "One-line agent-authored summary of what shipped." \\
        [--drift-source "..." --drift-resolution "..."] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS = ROOT / ".harness" / "roadmap_status.md"
DEFAULT_ARCHIVE = ROOT / ".harness" / "roadmap_drift_log_archive.md"

RECENTLY_COMPLETED_HEADING = "Recently completed (last 5)"
IN_FLIGHT_HEADING = "In-flight (open PRs)"
DRIFT_LOG_HEADING = "Drift detection log"
ANCHOR_HEADING = "Workspace state anchor"

RECENTLY_COMPLETED_CAP = 5
DRIFT_LOG_CAP = 10


class RoadmapStatusError(ValueError):
    """A structural problem with roadmap_status.md (fails --check)."""


# --- Workspace state (the hash-parity-critical half) -------------------------


@dataclass(frozen=True)
class WorkspaceState:
    head8: str
    prs_csv: str
    fork_count: str
    batch_path: str

    @property
    def open_pr_count(self) -> int:
        return 0 if not self.prs_csv else len(self.prs_csv.split(","))

    def hash12(self) -> str:
        return hash12(self.head8, self.prs_csv, self.fork_count, self.batch_path)

    def as_dict(self) -> dict[str, object]:
        return {
            "head8": self.head8,
            "prs_csv": self.prs_csv,
            "open_pr_count": self.open_pr_count,
            "fork_count": self.fork_count,
            "batch_path": self.batch_path,
            "workspace_state_hash": self.hash12(),
        }


def hash12(head8: str, prs_csv: str, fork_count: str, batch_path: str) -> str:
    """sha256(head|prs|forks|batch)[:12] — MUST match tools/hooks/lib.sh hook_state_hash."""
    s = f"{head8}|{prs_csv}|{fork_count}|{batch_path}"
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]


def _sh(cmd: str, cwd: Path) -> str:
    """Run a bash snippet, return stripped stdout. Never raises (matches the
    hooks' always-degrade-not-crash posture — e.g. `gh` absent/offline)."""
    try:
        out = subprocess.run(
            ["bash", "-c", cmd], cwd=cwd, capture_output=True, text=True, timeout=15
        )
        return out.stdout.strip()
    except Exception:
        return ""


def compute_state(project_dir: Path = ROOT) -> WorkspaceState:
    """Shell out to the literal command strings session-start.sh runs — not a
    reimplementation — so this can never drift from the bash hash recipe."""
    head8 = _sh("git rev-parse HEAD 2>/dev/null | head -c 8", project_dir)
    prs_csv = _sh(
        "gh pr list --state open --json number,headRefName "
        '--jq \'. | sort_by(.number) | map("\\(.number):\\(.headRefName)") | join(",")\' '
        "2>/dev/null || echo ''",
        project_dir,
    )
    fork_count = _sh(
        "ls .harness/class_1_fork_*.md .harness/class_2_fork_*.md 2>/dev/null | wc -l | tr -d ' '",
        project_dir,
    )
    batch_path = _sh(
        "ls .harness/phase-7d-retirement-events-batch-*.md 2>/dev/null | sort -V | tail -1",
        project_dir,
    )
    return WorkspaceState(
        head8=head8, prs_csv=prs_csv, fork_count=fork_count or "0", batch_path=batch_path
    )


# --- Markdown section/table plumbing ------------------------------------------


def _section_span(text: str, heading: str) -> tuple[int, int]:
    """Span of `## {heading}` through (not including) the next `^## ` or EOF."""
    m = re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE)
    if not m:
        raise RoadmapStatusError(f"section not found: {heading!r}")
    start = m.start()
    nxt = re.compile(r"^## ", re.MULTILINE).search(text, m.end())
    end = nxt.start() if nxt else len(text)
    return start, end


def _table_block_span(section: str) -> tuple[int, int]:
    """Span of the contiguous `|`-prefixed line block (the table) within a section."""
    lines = section.splitlines(keepends=True)
    offsets: list[int] = []
    pos = 0
    for line in lines:
        offsets.append(pos)
        pos += len(line)
    starts = [i for i, line in enumerate(lines) if line.startswith("|")]
    if not starts:
        raise RoadmapStatusError("no table found in section")
    first, last = starts[0], starts[-1]
    # extend `last` through any immediately-following contiguous `|` lines
    while last + 1 < len(lines) and lines[last + 1].startswith("|"):
        last += 1
    start = offsets[first]
    end = offsets[last] + len(lines[last])
    return start, end


def _table_rows(table_text: str) -> list[str]:
    return [line for line in table_text.splitlines() if line.startswith("|")]


def _replace_table_data_rows(text: str, heading: str, new_data_rows: list[str]) -> str:
    """Keep a section's header+separator row, replace the data rows."""
    sec_start, sec_end = _section_span(text, heading)
    section = text[sec_start:sec_end]
    tbl_start, tbl_end = _table_block_span(section)
    rows = _table_rows(section[tbl_start:tbl_end])
    if len(rows) < 2:
        raise RoadmapStatusError(f"{heading!r}: table missing header/separator")
    header, sep = rows[0], rows[1]
    new_table = "\n".join([header, sep, *new_data_rows]) + "\n"
    new_section = section[:tbl_start] + new_table + section[tbl_end:]
    return text[:sec_start] + new_section + text[sec_end:]


def _get_table_data_rows(text: str, heading: str) -> list[str]:
    sec_start, sec_end = _section_span(text, heading)
    section = text[sec_start:sec_end]
    tbl_start, tbl_end = _table_block_span(section)
    rows = _table_rows(section[tbl_start:tbl_end])
    return rows[2:] if len(rows) > 2 else []


# --- Anchor table --------------------------------------------------------------


def refresh_anchor(
    text: str, state: WorkspaceState, git_head_note: str, last_refreshed: str
) -> str:
    sec_start, sec_end = _section_span(text, ANCHOR_HEADING)
    section = text[sec_start:sec_end]
    tbl_start, tbl_end = _table_block_span(section)
    rows = _table_rows(section[tbl_start:tbl_end])
    header, sep = rows[0], rows[1]
    new_rows = [
        f"| `workspace_state_hash` | `{state.hash12()}` |",
        f"| `last_refreshed` | {last_refreshed} |",
        f"| `git_head` | `{state.head8}` — {git_head_note} |",
        f"| `latest_retirement_batch` | `{state.batch_path}` |",
        f"| `open_fork_doc_count` | {state.fork_count} |",
    ]
    new_table = "\n".join([header, sep, *new_rows]) + "\n"
    new_section = section[:tbl_start] + new_table + section[tbl_end:]
    return text[:sec_start] + new_section + text[sec_end:]


# --- In-flight PR table (fully mechanical — derived straight from gh) --------


def refresh_in_flight(text: str, state: WorkspaceState) -> str:
    rows: list[str]
    if not state.prs_csv:
        rows = ["| *(none)* | — | — | No open PRs at refresh time. |"]
    else:
        rows = []
        for pair in state.prs_csv.split(","):
            num, _, branch = pair.partition(":")
            rows.append(f"| #{num} | `{branch}` | — | — |")
    return _replace_table_data_rows(text, IN_FLIGHT_HEADING, rows)


# --- Recently completed (capped, idempotent prepend) --------------------------


def prepend_recently_completed(
    text: str, pr_ref: str, closed_at: str, notes: str, cap: int = RECENTLY_COMPLETED_CAP
) -> str:
    existing = _get_table_data_rows(text, RECENTLY_COMPLETED_HEADING)
    key_prefix = f"| {pr_ref} |"
    deduped = [r for r in existing if not r.startswith(key_prefix)]
    new_row = f"| {pr_ref} | {closed_at} | {notes} |"
    rows = [new_row, *deduped][:cap]
    return _replace_table_data_rows(text, RECENTLY_COMPLETED_HEADING, rows)


# --- Drift detection log (capped, idempotent prepend + archive overflow) -----


def _row_key(row: str) -> str:
    """A stable dedup key: the row's raw text (archive move must never
    double-move or double-prepend a row already present)."""
    return row.strip()


def prepend_drift_log(text: str, date: str, source: str, resolution: str) -> str:
    existing = _get_table_data_rows(text, DRIFT_LOG_HEADING)
    new_row = f"| {date} | {source} | {resolution} |"
    if existing and _row_key(existing[0]) == _row_key(new_row):
        return text  # already-applied no-op
    rows = [new_row, *existing]
    return _replace_table_data_rows(text, DRIFT_LOG_HEADING, rows)


def trim_drift_log(
    text: str, archive_path: Path = DEFAULT_ARCHIVE, cap: int = DRIFT_LOG_CAP
) -> tuple[str, str | None, int]:
    """Cap the live drift log to `cap` most-recent rows; move overflow into the
    archive file (never delete). Idempotent: a row already present in the
    archive (by exact text) is never re-appended; if nothing exceeds the cap
    this is a byte-identical no-op. PURE — writes nothing to disk; returns
    (new_status_text, new_archive_text_or_None, moved_count). `new_archive_text`
    is None iff nothing needed to move (callers must not write in that case)."""
    rows = _get_table_data_rows(text, DRIFT_LOG_HEADING)
    if len(rows) <= cap:
        return text, None, 0
    keep, overflow = rows[:cap], rows[cap:]

    archive_text = (
        archive_path.read_text()
        if archive_path.exists()
        else (
            "# Roadmap drift-detection log — full archive\n\n"
            "Full §12.3 drift/reconciliation audit history. The live dashboard "
            f"(`.harness/roadmap_status.md` → {DRIFT_LOG_HEADING}) shows only the "
            "most recent events; this file preserves the complete record.\n\n"
            "| Date | Source | Resolution |\n|---|---|---|\n"
        )
    )
    archive_existing_keys = {
        _row_key(line) for line in archive_text.splitlines() if line.startswith("|")
    }
    to_append = [r for r in overflow if _row_key(r) not in archive_existing_keys]
    new_archive_text = None
    if to_append:
        if not archive_text.endswith("\n"):
            archive_text += "\n"
        new_archive_text = archive_text + "\n".join(to_append) + "\n"

    new_text = _replace_table_data_rows(text, DRIFT_LOG_HEADING, keep)
    return new_text, new_archive_text, len(to_append)


# --- Validation (--check) -----------------------------------------------------


def validate(text: str, status_path: Path = DEFAULT_STATUS) -> list[str]:
    violations: list[str] = []

    try:
        recently = _get_table_data_rows(text, RECENTLY_COMPLETED_HEADING)
        if len(recently) > RECENTLY_COMPLETED_CAP:
            violations.append(
                f"{RECENTLY_COMPLETED_HEADING}: {len(recently)} rows exceeds cap "
                f"{RECENTLY_COMPLETED_CAP}"
            )
        seen: set[str] = set()
        for row in recently:
            key = row.split("|")[1].strip() if row.count("|") >= 2 else row
            if key in seen:
                violations.append(f"{RECENTLY_COMPLETED_HEADING}: duplicate ref {key!r}")
            seen.add(key)
    except RoadmapStatusError as e:
        violations.append(str(e))

    try:
        drift = _get_table_data_rows(text, DRIFT_LOG_HEADING)
        if len(drift) > DRIFT_LOG_CAP:
            violations.append(
                f"{DRIFT_LOG_HEADING}: {len(drift)} rows exceeds cap {DRIFT_LOG_CAP} "
                f"(run --trim-drift-log)"
            )
    except RoadmapStatusError as e:
        violations.append(str(e))

    m = re.search(r"`workspace_state_hash`\s*\|\s*`([a-f0-9]{12})`", text)
    stored_hash = m.group(1) if m else None
    if stored_hash is None:
        violations.append("no workspace_state_hash found in anchor table")
    else:
        state = compute_state(status_path.resolve().parents[1])
        computed = state.hash12()
        if state.head8 and computed != stored_hash:
            # Not fatal on its own — the §12.1 step-6 fixed-point carve-out means a
            # one-commit lag is expected right after a terminating refresh. Report
            # as informational rather than a hard violation; the SessionStart hook
            # is the authoritative halt-or-proceed gate for this.
            violations.append(
                f"workspace_state_hash stored={stored_hash} computed={computed} "
                "(informational — verify against §12.1 fixed-point carve-out "
                "before treating as drift)"
            )

    return violations


# --- CLI ------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic roadmap_status.md skeleton refresh.")
    ap.add_argument("--status", type=Path, default=DEFAULT_STATUS)
    ap.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    ap.add_argument("--state", action="store_true", help="print computed WorkspaceState as JSON")
    ap.add_argument("--check", action="store_true", help="validate; exit 1 on any violation")
    ap.add_argument("--trim-drift-log", action="store_true", help="cap+archive drift log only")
    ap.add_argument(
        "--refresh",
        action="store_true",
        help="mechanical refresh (anchor + in-flight + recently-completed)",
    )
    ap.add_argument("--pr", help="PR ref for the recently-completed row, e.g. 'PR #1234'")
    ap.add_argument("--date", help="ISO date for the recently-completed row")
    ap.add_argument("--notes", help="agent-authored notes cell for the recently-completed row")
    ap.add_argument("--last-refreshed", help="ISO 8601 timestamp; default: --date at 00:00:00Z")
    ap.add_argument(
        "--git-head-note", default="", help="free-text note appended after the git_head hash"
    )
    ap.add_argument("--drift-source", help="optional: also prepend a drift-log row")
    ap.add_argument("--drift-resolution", help="resolution text for --drift-source")
    ap.add_argument("--dry-run", action="store_true", help="print the diff instead of writing")
    args = ap.parse_args(argv)

    if args.state:
        print(json.dumps(compute_state().as_dict(), indent=2))
        return 0

    text = args.status.read_text()

    if args.check:
        violations = validate(text, args.status)
        hard = [v for v in violations if "informational" not in v]
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        if hard:
            print("ROADMAP STATUS CHECK FAILED:", file=sys.stderr)
            return 1
        print("roadmap_status.md OK")
        return 0

    if args.trim_drift_log:
        new_text, new_archive_text, moved = trim_drift_log(text, args.archive)
        if args.dry_run:
            print(f"would move {moved} row(s) to {args.archive}")
            return 0
        if new_archive_text is not None:
            args.archive.write_text(new_archive_text)
        if new_text != text:
            args.status.write_text(new_text)
        print(f"moved {moved} row(s) to {args.archive}")
        return 0

    if args.refresh:
        if not (args.pr and args.date and args.notes is not None):
            ap.error("--refresh requires --pr --date --notes")
        state = compute_state(args.status.resolve().parents[1])
        last_refreshed = args.last_refreshed or f"{args.date}T00:00:00Z"
        new_text = refresh_anchor(text, state, args.git_head_note, last_refreshed)
        new_text = refresh_in_flight(new_text, state)
        new_text = prepend_recently_completed(new_text, args.pr, args.date, args.notes)
        if args.drift_source:
            new_text = prepend_drift_log(
                new_text, args.date, args.drift_source, args.drift_resolution or ""
            )
        new_text, new_archive_text, moved = trim_drift_log(new_text, args.archive)
        if args.dry_run:
            import difflib

            diff = difflib.unified_diff(
                text.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=str(args.status),
                tofile=str(args.status) + " (refreshed)",
            )
            sys.stdout.writelines(diff)
            return 0
        if new_archive_text is not None:
            args.archive.write_text(new_archive_text)
        args.status.write_text(new_text)
        print(
            f"refreshed {args.status}: hash={state.hash12()} in_flight={state.open_pr_count} "
            f"drift_log_moved={moved}"
        )
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

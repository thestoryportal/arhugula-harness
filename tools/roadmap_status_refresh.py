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
import contextlib
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS = ROOT / ".harness" / "roadmap_status.md"
DEFAULT_ARCHIVE = ROOT / ".harness" / "roadmap_drift_log_archive.md"
# U-CTX-03: the "## Next action" section's round-by-round history (every
# `Prior next action (post-#NNN)` / `Round N` paragraph) lives here, verbatim,
# once superseded by a newer round. Never written by an ordinary --refresh —
# it is populated by hand at each next-action update, mirroring the existing
# DEFAULT_ARCHIVE convention for the drift log.
NEXT_ACTION_ARCHIVE = ROOT / ".harness" / "roadmap-next-action-archive.md"
# U-HE-28 codex r2 P2: the merge door's fixed wrapper string cannot carry an authored
# `--next-action`, but §12.2 requires the pointer re-derived at the refresh. ship-pr
# writes this gitignored draft (first line `post-pr: <N>`, pointer body below) BEFORE
# invoking safe-merge; the emit mode consumes it when N matches its own POST_PR and
# leaves (with a stderr warning) any mismatched/stale draft. An explicit --next-action
# flag always wins over the draft.
NEXT_ACTION_DRAFT = ROOT / ".harness" / ".next-action-draft"

RECENTLY_COMPLETED_HEADING = "Recently completed (last 5)"
IN_FLIGHT_HEADING = "In-flight (open PRs)"
DRIFT_LOG_HEADING = "Drift detection log"
ANCHOR_HEADING = "Workspace state anchor"
NEXT_ACTION_HEADING = "Next action"

RECENTLY_COMPLETED_CAP = 5
# U-CTX-03 AC #3: the whole-file byte budget the truncated `roadmap_status.md`
# must stay under (was 316,894 B pre-truncation; the "## Next action" body
# alone was 292,031 B of that).
HEAD_BYTE_BUDGET = 25_600
# Paragraph shapes that belong in NEXT_ACTION_ARCHIVE, never inline in the
# live "## Next action" section — re-accumulating them here is exactly the
# regression the archive split (U-CTX-03) exists to prevent.
_ARCHIVED_PARAGRAPH_RE = re.compile(r"^\*\*(Prior next action|Round \d+)", re.MULTILINE)
#: The live pointer paragraph `--rotate-next-action` demotes and replaces. The
#: `(post-#NNN)` label is part of the shape `validate()` counts, so the tool
#: composes it rather than trusting caller-supplied prose to carry it.
_CURRENT_PARAGRAPH_RE = re.compile(
    r"^\*\*Current next action \(post-#[^)]*\)\.\*\*.*?(?=\n\n|\Z)", re.MULTILINE | re.DOTALL
)
#: Insertion point in NEXT_ACTION_ARCHIVE: immediately after the header block's
#: `---` rule, so demoted rounds stay most-recent-first (the archive's own
#: documented ordering).
_ARCHIVE_INSERT_RE = re.compile(r"\n---\n\n")
DRIFT_LOG_CAP = 10
#: Byte budget for the `## Drift detection log` table's DATA rows. The row cap
#: above bounds the row COUNT but not row SIZE, and the rows are agent-authored
#: multi-KB narratives — at the 2026-08-13 saturation the ten capped rows were
#: 9,620 B, 38% of a 25,536 B file with 64 B of headroom left. Overflow moves
#: (never deletes) into DEFAULT_ARCHIVE exactly as count overflow does; the
#: newest row is always kept regardless of size so the table is never empty.
DRIFT_LOG_BYTE_BUDGET = 3_000
#: structural soft-severity marker (codex round-8): ONLY messages the validator
#: itself prefixes with this are non-hard — substring matching on "informational"
#: would let interpolated filenames/titles containing the word soften a real
#: violation.
INFORMATIONAL_PREFIX = "[informational] "


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


def _drift_keep_count(rows: list[str], cap: int, byte_budget: int) -> int:
    """How many most-recent drift rows survive BOTH the row cap and the byte
    budget. The newest row always survives (`max(1, …)`) — an empty data-row
    block would leave the table header dangling and make the section
    unparseable by `_table_block_span`, so a single oversized row is kept and
    reported rather than trimmed away."""
    kept = 0
    used = 0
    for row in rows[:cap]:
        size = len(row.encode("utf-8")) + 1  # +1 for the row's newline
        if kept and used + size > byte_budget:
            break
        used += size
        kept += 1
    return max(1, kept)


def trim_drift_log(
    text: str,
    archive_path: Path = DEFAULT_ARCHIVE,
    cap: int = DRIFT_LOG_CAP,
    byte_budget: int = DRIFT_LOG_BYTE_BUDGET,
) -> tuple[str, str | None, int]:
    """Cap the live drift log to the most-recent rows that fit BOTH `cap` rows
    and `byte_budget` bytes; move overflow into the archive file (never
    delete). Idempotent: a row already present in the archive (by exact text)
    is never re-appended; if nothing exceeds either bound this is a
    byte-identical no-op. PURE — writes nothing to disk; returns
    (new_status_text, new_archive_text_or_None, moved_count). `new_archive_text`
    is None iff nothing needed to move (callers must not write in that case)."""
    rows = _get_table_data_rows(text, DRIFT_LOG_HEADING)
    keep_n = _drift_keep_count(rows, cap, byte_budget)
    if len(rows) <= keep_n:
        return text, None, 0
    keep, overflow = rows[:keep_n], rows[keep_n:]

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


# --- Next-action rotation (the relief valve `--refresh` structurally cannot be) --


def _current_round_label(text: str) -> str | None:
    m = _CURRENT_PARAGRAPH_RE.search(text)
    if m is None:
        return None
    label = re.search(r"\(post-#([^)]*)\)", m.group(0))
    return label.group(1) if label else None


def find_superseded_round(status_path: Path, project_dir: Path) -> tuple[str, str] | None:
    """The most recent next-action round that is NO LONGER the live one, read
    from the live head's own git history.

    This is the archive's OWN documented convention, verbatim: *archiving happens
    in the NEXT content PR after a round is superseded, and the superseded text is
    taken from git history of the live head.* Archiving the round that is still
    CURRENT (an earlier draft of this tool did exactly that) breaks the archive's
    prior-only invariant — the trilemma recorded at `B-168`, resolved by exit
    (iii): archive round N-1, so all three constraints hold UNCHANGED and the
    write may ride an ordinary content PR.

    Returns (label, paragraph) or None when nothing is superseded yet.
    """
    rel = str(status_path.resolve().relative_to(project_dir.resolve()))
    live = _current_round_label(status_path.read_text())
    # FAIL CLOSED on unusable history. `_sh` degrades to "" on any git failure,
    # and a shallow clone yields a truncated log — either would make this return
    # None, the CLI report "nothing to archive", and the owed round go
    # permanently unarchived while later runs move on to newer ones (codex round
    # 14 [P2]). "No superseded round" and "cannot see the history" are different
    # answers and must not share an exit path.
    revs = _sh(f"git log --format=%H -- {rel}", project_dir).split()
    if not revs:
        raise RoadmapStatusError(
            f"git log returned no history for {rel} — refusing to report 'nothing to "
            "archive' when the history is simply unreadable"
        )
    for rev in revs:
        blob = _sh(f"git show {rev}:{rel}", project_dir)
        if not blob:
            continue
        label = _current_round_label(blob)
        if label and label != live:
            m = _CURRENT_PARAGRAPH_RE.search(blob)
            if m:
                return label, m.group(0)
    # Nothing differing found. In a SHALLOW clone that is ambiguous — genuinely
    # nothing superseded, or simply beyond the graft point — and reporting
    # "nothing to archive" would let the owed round go permanently unarchived
    # while later runs move on to newer ones. Shallowness only matters HERE, on
    # the not-found path: this workspace is normally shallow, so refusing up
    # front would break the documented workflow outright.
    if _sh("git rev-parse --is-shallow-repository", project_dir).strip() == "true":
        raise RoadmapStatusError(
            f"no superseded round found within a SHALLOW clone's {len(revs)} available "
            f"revision(s) of {rel} — cannot distinguish 'none' from 'beyond the graft "
            "point'. Re-run with full history (git fetch --unshallow)."
        )
    return None


def archive_superseded_round(paragraph: str, archive_text: str) -> str | None:
    """Append an already-SUPERSEDED round to the archive, relabelled `Prior`.
    Archive-only write; idempotent. Returns None if already present."""
    demoted = paragraph.replace("**Current next action", "**Prior next action", 1)
    if demoted.strip() in archive_text:
        return None
    ins = _ARCHIVE_INSERT_RE.search(archive_text)
    if ins is None:
        raise RoadmapStatusError(
            f"{NEXT_ACTION_ARCHIVE.name}: no `---` header rule found — cannot "
            "determine the most-recent-first insertion point"
        )
    at = ins.end()
    return archive_text[:at] + demoted.strip() + "\n\n" + archive_text[at:]


def archive_current_next_action(text: str, archive_text: str) -> str | None:
    """Append the live `**Current next action**` paragraph to the archive,
    relabelled `Prior`, WITHOUT touching the status file. Returns the new archive
    text, or None if it is already archived (idempotent).

    This split is what makes the workflow PR-compatible (codex round 11 [P1]).
    A rotation that wrote BOTH files could never transit a PR: bundled with the
    refresh, the PR's base..head diff includes the archive, so the §12.2.1 shape
    gate rejects a refresh-prefixed title; titled otherwise, the squash merge is
    non-terminating and reds `main`. Split, both steps are individually clean —
    this one touches only the archive (so `_owed_lag` applies), and the
    terminating refresh touches only `roadmap_status.md` (so `_lag_expected`
    applies).
    """
    m = _CURRENT_PARAGRAPH_RE.search(text)
    if m is None:
        raise RoadmapStatusError(
            f"{NEXT_ACTION_HEADING}: no `**Current next action (post-#NNN).**` paragraph to archive"
        )
    demoted = m.group(0).replace("**Current next action", "**Prior next action", 1)
    if demoted.strip() in archive_text:
        return None
    ins = _ARCHIVE_INSERT_RE.search(archive_text)
    if ins is None:
        raise RoadmapStatusError(
            f"{NEXT_ACTION_ARCHIVE.name}: no `---` header rule found — cannot "
            "determine the most-recent-first insertion point"
        )
    at = ins.end()
    return archive_text[:at] + demoted.strip() + "\n\n" + archive_text[at:]


def install_next_action(text: str, pr_ref: str, body: str) -> str:
    """Replace the live pointer paragraph. STATUS FILE ONLY — safe inside the
    single-file terminating refresh.

    Deliberately does NOT require the outgoing round to be archived first. Under
    the `B-168` exit (iii) resolution the archive lags by exactly one arc BY
    DESIGN — the next content PR archives this round via `--archive-superseded`,
    and the live head's git history is the lossless record meanwhile. An earlier
    draft enforced archive-before-replace, which silently encoded a DIFFERENT
    exit (relaxing the archive's prior-only invariant) and made the refresh
    unrunnable at the one moment it is needed.
    """
    m = _CURRENT_PARAGRAPH_RE.search(text)
    if m is None:
        raise RoadmapStatusError(
            f"{NEXT_ACTION_HEADING}: no `**Current next action (post-#NNN).**` paragraph to replace"
        )
    digits = re.fullmatch(r"(?:PR\s*)?#?\s*(\d+)", pr_ref.strip(), re.IGNORECASE)
    if not digits:
        raise RoadmapStatusError(
            f"--pr {pr_ref!r} is not a PR number — expected `1234`, `#1234` or `PR #1234`"
        )
    if "\n\n" in body.strip():
        raise RoadmapStatusError(
            "--next-action body must be a SINGLE paragraph (no blank lines) — the "
            "live pointer is one paragraph, and only the first would ever be archived"
        )
    if not body.strip():
        raise RoadmapStatusError(
            "--next-action requires a non-empty body — refusing to install an empty "
            "next-action pointer (an empty frontier passes --check silently)"
        )
    new_paragraph = f"**Current next action (post-#{digits.group(1)}).** {body.strip()}"
    return text[: m.start()] + new_paragraph + text[m.end() :]


def rotate_next_action(
    text: str, archive_text: str, pr_ref: str, body: str
) -> tuple[str, str | None]:
    """Demote the live `**Current next action (post-#A)**` paragraph into the
    next-action archive (relabelled `Prior`, body verbatim) and install a new
    Current paragraph in its place. PURE — writes nothing; returns
    (new_status_text, new_archive_text_or_None); `new_archive_text` is None iff
    the demoted round was already archived (idempotent re-run).

    This is deliberately NOT part of `--refresh`. §12.2.1 requires a
    terminating refresh commit to touch EXACTLY `.harness/roadmap_status.md`,
    so a mode that also writes the archive can never be the terminating commit
    — which is precisely why the relief valve was unreachable from inside a
    refresh and the head saturated instead. Run this as its OWN content commit
    (unprefixed title, per §12.2.1 "bundled changes drop the prefix") BEFORE
    the terminating refresh."""
    m = _CURRENT_PARAGRAPH_RE.search(text)
    if m is None:
        raise RoadmapStatusError(
            f"{NEXT_ACTION_HEADING}: no `**Current next action (post-#NNN).**` paragraph to rotate"
        )
    demoted = m.group(0).replace("**Current next action", "**Prior next action", 1)

    # `--pr` is documented as accepting `PR #1234`; `lstrip("#")` handled only a
    # bare `#1234` and turned the documented form into the malformed label
    # `(post-#PR #1234)`, which validate() then accepted (codex round 2 [P2]).
    # Extract the numeric shape, and refuse anything else rather than emit a
    # label the rest of the machinery keys on.
    digits = re.fullmatch(r"(?:PR\s*)?#?\s*(\d+)", pr_ref.strip(), re.IGNORECASE)
    if not digits:
        raise RoadmapStatusError(
            f"--pr {pr_ref!r} is not a PR number — expected `1234`, `#1234` or `PR #1234`"
        )
    num = digits.group(1)
    # An empty/whitespace BODY (an unset shell variable, typically) would archive
    # the live pointer and install a marker with NO actionable text — and
    # validate() only COUNTS the marker, so the empty frontier would pass --check
    # too, leaving the next session with no next action at all (codex round 3
    # [P2]). Refuse before either file is modified.
    # The live pointer is ONE paragraph by construction: _CURRENT_PARAGRAPH_RE
    # stops at the first blank line, so a multi-paragraph body writes fine but
    # only its FIRST paragraph is archived at the next rotation — the remainder
    # stays in the live section permanently, growing the head while validation
    # still passes (codex round 5 [P2]). Reject rather than silently truncate
    # the archive.
    if "\n\n" in body.strip():
        raise RoadmapStatusError(
            "--rotate-next-action body must be a SINGLE paragraph (no blank lines) — "
            "the live pointer is one paragraph, and only the first would ever be "
            "archived, leaving the rest permanently in the live section"
        )
    if not body.strip():
        raise RoadmapStatusError(
            "--rotate-next-action requires a non-empty body — refusing to install an "
            "empty next-action pointer (an empty frontier passes --check silently)"
        )
    new_paragraph = f"**Current next action (post-#{num}).** {body.strip()}"

    # Re-running the SAME rotation must be a no-op. Without this the newly
    # installed paragraph is read as the current one, demoted into the archive,
    # and left live as Current — so the archive claims a round is Prior while the
    # head still says it is Current (codex round 2 [P2]; the original idempotency
    # test missed it by re-running against the ORIGINAL text, not the output).
    if m.group(0).strip() == new_paragraph.strip():
        return text, None

    new_text = text[: m.start()] + new_paragraph + text[m.end() :]

    if demoted.strip() in archive_text:
        return new_text, None
    ins = _ARCHIVE_INSERT_RE.search(archive_text)
    if ins is None:
        raise RoadmapStatusError(
            f"{NEXT_ACTION_ARCHIVE.name}: no `---` header rule found — cannot "
            "determine the most-recent-first insertion point"
        )
    at = ins.end()
    new_archive_text = archive_text[:at] + demoted.strip() + "\n\n" + archive_text[at:]
    return new_text, new_archive_text


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
        # Row COUNT alone never bounded this section: the rows are multi-KB
        # narratives, so ten legal rows were 38% of the whole-file budget.
        # Judge the BYTES directly, not "would a trim change the row count".
        # Those are different questions, and conflating them fails open on the
        # single-oversized-row case (out-of-family review, round 1): with one
        # 5 KB row, `_drift_keep_count` returns 1 because the newest row is
        # always retained, `len(drift) > 1` is False, and --check reported no
        # violation against a section 67% over budget.
        drift_bytes = sum(len(r.encode("utf-8")) + 1 for r in drift)
        if drift_bytes > DRIFT_LOG_BYTE_BUDGET:
            trimmable = len(drift) > _drift_keep_count(drift, DRIFT_LOG_CAP, DRIFT_LOG_BYTE_BUDGET)
            remedy = (
                f"run --trim-drift-log; overflow moves to {DEFAULT_ARCHIVE.name}, "
                "nothing is deleted"
                if trimmable
                else "the NEWEST row alone exceeds the budget and is always retained "
                "(trimming cannot help) — shorten that row's prose"
            )
            # INFORMATIONAL, not hard. The load-bearing cap is the WHOLE-FILE
            # HEAD_BYTE_BUDGET above, which stays hard. This sub-budget's job is
            # to say WHERE the bytes are and that a trim will reclaim them — the
            # 2026-08-13 saturation was a file legally under the hard cap with 64
            # B of headroom, and 38% of it sitting in this one section. Hard-
            # blocking CI on a sub-budget while the real cap is satisfied would
            # be over-enforcement, and would red `main` for every arc between the
            # budget landing and the next trim.
            violations.append(
                f"{INFORMATIONAL_PREFIX}{DRIFT_LOG_HEADING}: {drift_bytes} B of data "
                f"rows exceeds the {DRIFT_LOG_BYTE_BUDGET} B guidance budget ({remedy})"
            )
    except RoadmapStatusError as e:
        violations.append(str(e))

    # U-CTX-03 AC #3: whole-file byte budget. The pre-truncation file grew to
    # 316,894 B (292,031 B of it the "## Next action" body alone) before
    # NEXT_ACTION_ARCHIVE existed — this is the regression guard against that
    # recurring.
    status_bytes = len(text.encode("utf-8"))
    if status_bytes > HEAD_BYTE_BUDGET:
        violations.append(
            f"roadmap_status.md is {status_bytes} B, exceeds the {HEAD_BYTE_BUDGET} B "
            f"head byte budget (archive growth belongs in {NEXT_ACTION_ARCHIVE.name}, "
            "not inline)"
        )

    # U-CTX-03 AC #2: the archive is never (re-)written by an ordinary terminating
    # refresh, and the live "## Next action" section never re-accumulates the
    # archived paragraph shapes it was truncated to move out — that would defeat
    # the byte-budget truncation and silently regrow the file this arc just
    # shrank. A --refresh call's own write set is a single Path.write_text call
    # against `args.status` (plus, only on drift-log overflow, `args.archive` —
    # DEFAULT_ARCHIVE, a distinct file from NEXT_ACTION_ARCHIVE); asserting the
    # two archive constants are distinct paths keeps that separation structural,
    # and the content check below keeps the live section from silently regrowing
    # into what would have to be the next-action archive's job.
    if DEFAULT_ARCHIVE.resolve() == NEXT_ACTION_ARCHIVE.resolve():
        violations.append(
            "DEFAULT_ARCHIVE and NEXT_ACTION_ARCHIVE must be distinct files — a "
            "--refresh call's drift-log trim must never touch the next-action archive"
        )
    try:
        next_action_start, next_action_end = _section_span(text, NEXT_ACTION_HEADING)
        next_action_body = text[next_action_start:next_action_end]
        if _ARCHIVED_PARAGRAPH_RE.search(next_action_body):
            violations.append(
                f"{NEXT_ACTION_HEADING}: contains an inline `Prior next action`/"
                f"`Round N` paragraph — archive it to {NEXT_ACTION_ARCHIVE.name} "
                "instead of accumulating it inline (defeats the U-CTX-03 byte-budget "
                "truncation)"
            )
        # Exactly ONE `**Current next action (...)**` paragraph (codex round-5):
        # a second one would leave hook_roadmap_next consuming whichever comes
        # first — a potentially stale live pointer — while the inline-history
        # regex above (which matches only the demoted `Prior`/`Round N` shapes)
        # stayed silent. Zero means the live pointer is gone entirely.
        current_count = next_action_body.count("**Current next action (")
        if current_count != 1:
            violations.append(
                f"{NEXT_ACTION_HEADING}: expected exactly ONE `**Current next "
                f"action (...)**` paragraph, found {current_count} — the live "
                "pointer must be single and unambiguous (a superseded round is "
                "relabelled `Prior` and archived, never left as a second Current)"
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
                f"{INFORMATIONAL_PREFIX}workspace_state_hash stored={stored_hash} "
                f"computed={computed} (verify against §12.1 fixed-point carve-out "
                "before treating as drift)"
            )

    return violations


# --- CLI ------------------------------------------------------------------


#: mirrors codex_context_guard.TERMINATING_REFRESH_FILE_SETS (kept literal here
#: so `--check` stays import-light; the guard module drags in codex_loop).
_REFRESH_TITLE_PREFIX = "ops: roadmap status refresh "
_REFRESH_ONLY_FILE_SET = frozenset({".harness/roadmap_status.md"})


def check_head_refresh_shape(
    root: Path,
    ref: str = "HEAD",
    base: str | None = None,
    title_override: str | None = None,
) -> list[str]:
    """U-CTX-03 AC #2, git-shape half (codex round-2): if HEAD is a
    terminating-refresh-titled commit, its changed-file set must be EXACTLY
    `.harness/roadmap_status.md` — a refresh that also writes the next-action
    archive (or anything else) breaks the §12.2.1 one-file invariant that the
    fixed-point machinery keys on. Constant-distinctness alone cannot see a
    commit's actual write set. No-op (empty list) when HEAD is not
    refresh-titled or git is unavailable (e.g. a tarball checkout)."""
    # Distinguish "intentionally not a git checkout" (tarball / missing root /
    # no git binary — skip) from "git ERRORED inside a real checkout" (fail
    # CLOSED: returning [] there would report success without enforcing the
    # refresh file-set at all — codex round-4).
    checkout_marker = (root / ".git").exists()
    try:
        probe = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as e:
        if checkout_marker:
            # codex round-8: a .git marker exists, so this is a real checkout
            # whose probe ERRORED (timeout/permissions) — skipping would report
            # success without enforcing the refresh shape at all.
            return [
                f"git probe errored in a directory carrying a .git marker — "
                f"failing closed rather than skipping the refresh-shape gate: {e}"
            ]
        return []
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        if checkout_marker:
            return [
                f"git refused --is-inside-work-tree in a directory carrying a .git "
                f"marker (rc={probe.returncode}, stderr={probe.stderr.strip()!r}) — "
                f"failing closed rather than skipping the refresh-shape gate"
            ]
        return []
    try:
        # Pin the (possibly symbolic) ref to an immutable SHA ONCE — merge-gate
        # lens 1 on this arc: with `--shape-ref HEAD` a concurrent commit
        # landing between the title read and the file-set read would make the
        # gate judge commit A's title against commit B's diff (spurious hard
        # failure, or transient fail-open). Every subsequent git call uses the
        # pinned SHA.
        resolved_ref = subprocess.run(
            ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        ).stdout.strip()
        ref = resolved_ref
        if title_override is not None:
            # codex round-10: the §12.2.1 invariant binds on the PR TITLE —
            # a refresh-titled PR whose head commit carries an ordinary
            # subject must still be judged (and a content PR is governed by
            # its own title regardless of inner commit subjects).
            title = title_override
        else:
            title = subprocess.run(
                ["git", "log", "-1", "--format=%s", ref],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            ).stdout.strip()
        if not title.startswith(_REFRESH_TITLE_PREFIX):
            return []
        # Shallow-boundary guard (codex round-3): on a depth-1 CI checkout,
        # HEAD's parent is absent and `git show HEAD` lists the ENTIRE tree
        # (parentless root-commit diff) — the same documented failure shape as
        # ci.yml's codex-context-guard checkout comment. Judging the set there
        # would fail every legitimate refresh; skip instead (the arc-ledger CI
        # job now checks out full history, so the gate still enforces in CI).
        parent_ok = (
            subprocess.run(
                ["git", "rev-parse", "--verify", "-q", f"{ref}^"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            ).returncode
            == 0
        )
        if not parent_ok:
            shallow = (
                subprocess.run(
                    ["git", "rev-parse", "--is-shallow-repository"],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    timeout=10,
                ).stdout.strip()
                == "true"
            )
            if shallow:
                return []
        # Merge-wrapped refresh (codex round-9): a `git merge --no-ff`-landed
        # refresh keeps the reserved prefix on a MERGE commit, where plain
        # `git show --name-only` uses combined-diff semantics and can return
        # NO paths (the result matches a parent) — an empty set would wrongly
        # fail every such legitimate refresh. §12.2.1 recognizes merge-wrapped
        # refresh points; judge merges by their FIRST-PARENT diff instead.
        if base is not None:
            # PR context: the invariant covers the PR's WHOLE base..head diff,
            # not just the head commit (a multi-commit refresh PR must not
            # hide extra files in earlier commits).
            changed = subprocess.run(
                ["git", "diff", "--name-only", f"{base}...{ref}"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            ).stdout
            files = frozenset(line.strip() for line in changed.splitlines() if line.strip())
            if files != _REFRESH_ONLY_FILE_SET:
                return [
                    f"refresh-titled PR ({title!r}) changes {sorted(files)} across "
                    f"base...head — a terminating refresh must touch EXACTLY "
                    f"{sorted(_REFRESH_ONLY_FILE_SET)} (§12.2.1)"
                ]
            return []
        parents = subprocess.run(
            ["git", "rev-list", "--parents", "-n", "1", ref],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        ).stdout.split()[1:]
        if len(parents) >= 2:
            changed = subprocess.run(
                ["git", "diff", "--name-only", f"{ref}^1", ref],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            ).stdout
        else:
            changed = subprocess.run(
                ["git", "show", "--name-only", "--pretty=format:", ref],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            ).stdout
    except (OSError, subprocess.SubprocessError) as e:
        return [
            f"git errored inside a detected work tree while validating the "
            f"terminating-refresh shape — failing closed rather than skipping "
            f"the file-set gate: {e}"
        ]
    files = frozenset(line.strip() for line in changed.splitlines() if line.strip())
    if files != _REFRESH_ONLY_FILE_SET:
        return [
            f"HEAD is a terminating-refresh-titled commit ({title!r}) but its "
            f"changed-file set is {sorted(files)} — a terminating refresh must "
            f"touch EXACTLY {sorted(_REFRESH_ONLY_FILE_SET)} (§12.2.1; "
            f"U-CTX-03 AC #2: the next-action archive is written by content "
            f"PRs, never by the refresh commit)"
        ]
    return []


def _discard_matching_draft(post_pr: int, represented_in: str | None) -> None:
    """Retire the next-action draft iff it names post_pr AND its body is verifiably
    represented by the pushed refresh content (codex r6 P2: an operator may CORRECT a
    same-PR draft after the branch was pushed — deleting the unrepresented correction
    would silently land the older pointer). represented_in is the pushed refresh
    commit's roadmap_status.md text, or None when it could not be obtained — in every
    unverified case the draft is KEPT (fail toward retaining the operator's authoring).
    """
    try:
        if not NEXT_ACTION_DRAFT.is_file():
            return
        raw = NEXT_ACTION_DRAFT.read_text()
        first, _, rest = raw.partition("\n")
        m = re.match(r"post-pr:\s*(\d+)\s*$", first.strip())
        if not (m and int(m.group(1)) == post_pr):
            return  # another arc's authoring — always left alone
        body = rest.strip()
        # r7 P2 + r8 P2 + r11 P2: the proof is EQUALITY with the LIVE pointer body
        # AND the pointer's own post-# label naming THIS landing — a stale post-#54
        # pointer that happens to equal the draft body is not installation of the
        # post-#55 pointer.
        live = _CURRENT_PARAGRAPH_RE.search(represented_in) if represented_in else None
        live_body = None
        if live is not None:
            lm = re.match(
                r"^\*\*Current next action \(post-#(\d+)[^)]*\)\.\*\*\s*(.*)\Z",
                live.group(0),
                re.DOTALL,
            )
            if lm and int(lm.group(1)) == post_pr:
                live_body = lm.group(2).strip()
        if body and live_body == body:
            # r11 P2 best-effort recheck: another agent may have replaced the draft
            # since the read above — unlink only if the content is unchanged (the
            # read-vs-unlink instant remains an irreducible non-atomic window).
            if NEXT_ACTION_DRAFT.read_text() == raw:
                NEXT_ACTION_DRAFT.unlink()
        else:
            print(
                "emit-refresh-pr: keeping next-action draft — its body is not "
                "verified in the pushed refresh content (a correction survives "
                "for the retry / next manual refresh)",
                file=sys.stderr,
            )
    except OSError:
        pass


def _pushed_refresh_text(run, branch: str) -> str | None:
    """Best-effort read of the pushed refresh commit's roadmap_status.md (for draft
    retirement verification). None on any failure — never aborts the emit."""
    try:
        f = run(
            ["git", "fetch", "-q", "origin", branch],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if f.returncode != 0:
            return None
        s = run(
            ["git", "show", "FETCH_HEAD:.harness/roadmap_status.md"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return s.stdout if s.returncode == 0 else None
    except Exception:
        return None


def emit_refresh_pr(
    post_pr: int,
    *,
    notes: str | None = None,
    next_action: str | None = None,
    date: str | None = None,
    run=subprocess.run,
    do_refresh=None,
) -> dict:
    """C-HE-06 §4(viii), U-HE-28: create the terminating refresh PR as the merge door's
    continuation and return {pr, head_sha} for the door to merge under the same held lease.

    Any failure raises -> non-zero exit, no JSON -> the door marks step (viii) blocked.
    Never merges here (the door drives the merge).

    IDEMPOTENT by branch name (plan Codex round-4 P1): a crash between `gh pr create` and
    the door's sidecar publish must not orphan/duplicate the refresh. If the branch
    already has an open PR, return it; if the branch was pushed but no PR exists, create
    the PR on it; only otherwise create the branch. NOTE (r8): after such a crash the
    door deliberately blocks on `refresh_intent_unresolved` (U-HE-23 codex r1 P2 — a
    blind re-call could mint a second PR); this idempotency is what makes BOTH documented
    recoveries converge — `record-refresh` records the pair, and `clear-refresh-intent`
    + re-land re-enters here and resumes the existing branch/PR instead of duplicating.

    As-built correction vs the plan-time sketch (recorded in the U-HE-28 rev note): the
    fresh path branches from the JUST-MERGED `origin/main` tip (fetch first), and runs
    the mechanical refresh AFTER that checkout — never from the invoking worktree's topic
    HEAD. Both §12.2.1 halves depend on it: the refresh commit's recorded `git_head` must
    equal its OWN parent (`_is_terminating_refresh_commit`), and the PR's base...head
    diff must be roadmap-status-only (a topic-HEAD branch would drag the whole arc diff
    into the shape gate).
    """
    branch = f"roadmap-refresh-post-{post_pr}"
    title = f"ops: roadmap status refresh post-#{post_pr}"
    body = (
        "terminating refresh (CLAUDE.md §12.2.1); landed by the merge door as a "
        "continuation (C-HE-06 §4(viii))"
    )

    def sh(*args: str) -> str:
        p = run(list(args), capture_output=True, text=True, timeout=120)
        if p.returncode != 0:
            raise SystemExit(f"emit-refresh-pr: {' '.join(args)} failed: {p.stderr.strip()}")
        return p.stdout.strip()

    existing = sh(
        "gh",
        "pr",
        "list",
        "--head",
        branch,
        "--state",
        "open",
        "--json",
        "number,headRefOid,baseRefName,title,isCrossRepository",
        "--jq",
        '.[0] | select(.) | "\\(.number)\\t\\(.headRefOid)\\t\\(.baseRefName)\\t'
        '\\(.isCrossRepository)\\t\\(.title)"',
    )
    if existing:
        n, head, base_ref, cross_repo, found_title = existing.split("\t", 4)
        # r7 P2 + r10 P1: identity-gate the resumed PR — a retargeted or reused PR,
        # or a FORK PR squatting the predictable branch name (attacker-controlled
        # head the door's title/base/file gates cannot distinguish), must never be
        # persisted for the door to merge.
        if base_ref != "main" or cross_repo != "false" or found_title.strip() != title:
            raise SystemExit(
                f"emit-refresh-pr: open PR #{n} on {branch} is not this landing's "
                f"terminating refresh (base {base_ref!r}, cross-repo {cross_repo!r}, "
                f"title {found_title!r}); inspect/close it before retrying"
            )
        if notes is not None or next_action is not None or date is not None:
            # r10 P2 (supersedes the r7 warn-and-continue): a resume cannot apply
            # supplied flags — silently handing the stale PR to the door would land
            # the OLD pointer while the operator believes the correction applied.
            raise SystemExit(
                f"emit-refresh-pr: open refresh PR #{n} already exists; supplied "
                "--notes/--date/--next-action cannot be applied to it. Close the PR "
                "(or drop the flags) and re-run"
            )
        # retire a matching draft ONLY if its body is verifiably in the pushed
        # refresh commit (codex r3 P2 + r6 P2 correction-preserving rule)
        _discard_matching_draft(post_pr, _pushed_refresh_text(run, branch))
        return {"pr": int(n), "head_sha": head}
    # Remote-branch probe: `--exit-code` means exit 2 is the ONLY "no matching ref"
    # signal; auth/transport/timeout failures use other codes (codex r1 P2 — same
    # contract ship-pr's branch-hygiene step documents). Treating those as "absent"
    # would reset a previously-pushed branch onto origin/main and then fail the
    # non-fast-forward push, blocking the door instead of resuming the branch.
    probe = run(
        ["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if probe.returncode not in (0, 2):
        raise SystemExit(
            f"emit-refresh-pr: could not verify remote state of {branch} "
            f"(ls-remote exit {probe.returncode}): {probe.stderr.strip()}"
        )
    if probe.returncode == 0:
        sh("git", "fetch", "-q", "origin", branch)
        sh("git", "checkout", "-q", "-B", branch, f"origin/{branch}")
        # r7 P2 + r10 P2: this path recovers a branch whose refresh commit ALREADY
        # exists — re-running the refresh here would add a second commit whose
        # recorded git_head is the first refresh commit, breaking the §12.2.1 fixed
        # point on squash. Supplied flags therefore cannot apply: REFUSE rather than
        # warn (the r10 posture, unified with the open-PR path above).
        if notes is not None or next_action is not None or date is not None:
            raise SystemExit(
                f"emit-refresh-pr: a pushed refresh branch {branch} already exists; "
                "supplied --notes/--date/--next-action cannot be applied to its "
                "commit. Delete the remote branch (or drop the flags) and re-run"
            )
        url = sh(
            "gh",
            "pr",
            "create",
            "--base",
            "main",
            "--head",
            branch,
            "--title",
            title,
            "--body",
            body,
        )
        # the branch is checked out here, but verify against the PUSHED content the
        # same way as the sibling path (r6 P2)
        _discard_matching_draft(post_pr, _pushed_refresh_text(run, branch))
        return {
            "pr": int(url.rstrip("/").rsplit("/", 1)[-1]),
            "head_sha": sh("git", "rev-parse", "HEAD"),
        }
    # Fresh path: branch from the just-merged main tip (see docstring), then refresh.
    sh("git", "fetch", "-q", "origin", "main")
    sh("git", "checkout", "-q", "-B", branch, "origin/main")
    draft_warning = None
    draft_used = False
    if next_action is None and NEXT_ACTION_DRAFT.is_file():
        # §12.2 pointer re-derivation through the door (codex r2 P2): consume the
        # ship-pr-authored draft iff it names THIS landing; a stale draft from an
        # aborted arc must never install another arc's pointer.
        raw = NEXT_ACTION_DRAFT.read_text()
        first, _, rest = raw.partition("\n")
        m = re.match(r"post-pr:\s*(\d+)\s*$", first.strip())
        if m and int(m.group(1)) == post_pr and rest.strip():
            # READ ONLY — the draft is retired after `gh pr create` succeeds (codex
            # r3 P2): a crash between here and the push must leave the draft for the
            # retry, else the re-run silently lands a pointer-less refresh.
            next_action = rest.strip()
            draft_used = True
        else:
            # The door captures and discards this process's stderr on success (codex
            # r5 P2), so the condition is ALSO surfaced durably in the refresh PR
            # body below — the venue the operator actually reads.
            draft_warning = (
                f"WARNING: next-action draft ignored ({first.strip()!r} does not "
                f"name post-pr: {post_pr}, or empty body); pointer left as-is"
            )
            print(f"emit-refresh-pr: {draft_warning}", file=sys.stderr)
    if do_refresh is None:

        def do_refresh() -> None:
            argv = [
                "--refresh",
                "--pr",
                f"PR #{post_pr}",
                "--date",
                date or _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%d"),
                "--notes",
                notes
                if notes is not None
                else (
                    "landed through the merge door; terminating refresh as "
                    "continuation (C-HE-06 §4(viii))"
                ),
            ]
            if next_action is not None:
                argv += ["--next-action", next_action]
            rc = main(argv)
            if rc != 0:
                raise SystemExit(f"emit-refresh-pr: mechanical refresh exited {rc}")

    do_refresh()
    sh("git", "add", ".harness/roadmap_status.md")  # the ONLY file (§12.2.1)
    changed = sh("git", "diff", "--cached", "--name-only").splitlines()
    if changed != [".harness/roadmap_status.md"]:
        raise SystemExit(
            f"emit-refresh-pr: refresh must touch exactly .harness/roadmap_status.md, got {changed}"
        )
    sh("git", "commit", "-m", title)
    sh("git", "push", "-u", "origin", branch)
    pr_body = body if draft_warning is None else f"{body}\n\n{draft_warning}"
    url = sh("gh", "pr", "create", "--base", "main", "--title", title, "--body", pr_body)
    # only a draft whose body was ADOPTED into this refresh is represented by
    # construction — retire it now that the branch + PR are durable (r3 P2). An
    # overridden (explicit --next-action) or mismatched draft is unrepresented
    # authoring and is KEPT (r6 P2 rule; supersedes the r5 retire-on-override).
    if draft_used:
        # mirror exactly what install_next_action just wrote, so the helper's
        # live-paragraph proof holds by construction
        _discard_matching_draft(
            post_pr, f"**Current next action (post-#{post_pr}).** {next_action}"
        )
    return {
        "pr": int(url.rstrip("/").rsplit("/", 1)[-1]),
        "head_sha": sh("git", "rev-parse", "HEAD"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic roadmap_status.md skeleton refresh.")
    ap.add_argument("--status", type=Path, default=DEFAULT_STATUS)
    ap.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    ap.add_argument("--state", action="store_true", help="print computed WorkspaceState as JSON")
    ap.add_argument("--check", action="store_true", help="validate; exit 1 on any violation")
    ap.add_argument(
        "--shape-ref",
        default="HEAD",
        help="git ref the terminating-refresh shape gate judges (default HEAD). "
        "CI pull_request runs pass the PR HEAD sha: actions/checkout puts the "
        "SYNTHETIC merge ref at HEAD, whose 'Merge ...' subject would make the "
        "gate silently no-op pre-merge (codex round-5)",
    )
    ap.add_argument(
        "--shape-base",
        default=None,
        help="base sha for the shape gate: judge the WHOLE base...shape-ref diff "
        "(PR context) instead of the single ref commit",
    )
    ap.add_argument(
        "--shape-title-env",
        default=None,
        help="NAME of an env var holding the authoritative title for the shape "
        "gate (the PR title on pull_request events — passed via env, never "
        "shell-interpolated; codex round-10)",
    )
    ap.add_argument("--trim-drift-log", action="store_true", help="cap+archive drift log only")
    ap.add_argument(
        "--archive-superseded",
        action="store_true",
        help="append the most recent ALREADY-SUPERSEDED next-action round (read "
        "from the live head's git history) to the next-action archive as Prior. "
        "Writes ONLY the archive, so it rides an ordinary content PR. Archiving "
        "the round that is still CURRENT would break the archive's prior-only "
        "invariant — see B-168 exit (iii)",
    )
    ap.add_argument(
        "--next-action",
        metavar="BODY",
        help="with --refresh: install BODY as the new Current next-action pointer "
        "in the SAME single-file write (requires --pr)",
    )
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
    ap.add_argument(
        "--emit-refresh-pr-json",
        type=int,
        metavar="POST_PR",
        help="C-HE-06 §4(viii), U-HE-28: run the mechanical refresh for the "
        "just-landed PR POST_PR (branching from the just-merged origin/main "
        "tip), commit on roadmap-refresh-post-POST_PR, push, create the "
        "terminating refresh PR, and print {pr, head_sha} for the merge door. "
        "--notes/--next-action/--date compose when given; the door's fixed "
        "wrapper invocation passes none, so those default mechanically. "
        "Idempotent by branch name; any failure exits non-zero with no JSON",
    )
    ap.add_argument("--drift-source", help="optional: also prepend a drift-log row")
    ap.add_argument("--drift-resolution", help="resolution text for --drift-source")
    ap.add_argument("--dry-run", action="store_true", help="print the diff instead of writing")
    args = ap.parse_args(argv)

    # U-CTX-03 AC #2, runtime half: the structural constant check in validate()
    # only compares the hard-coded defaults — it cannot see a caller aliasing
    # the drift-log archive onto the PROTECTED next-action archive via
    # `--archive`, which would let a drift-log overflow rewrite the round
    # history. Reject the effective path before any write-capable mode runs.
    # Derive the TARGET checkout's root + protected archive from --status
    # (codex round-3): with `--status` pointing at another checkout, comparing
    # only this module's hard-coded constant would leave THAT checkout's own
    # next-action archive unprotected and shape-check the wrong repo. The
    # module-global constant stays in the comparison so the default-invocation
    # protection is unchanged.
    status_root = args.status.resolve().parent.parent
    target_protected_archive = status_root / ".harness" / "roadmap-next-action-archive.md"

    def _aliases_protected(candidate: Path, protected: Path) -> bool:
        # Path equality first; then FILE IDENTITY for existing files — on a
        # case-insensitive filesystem (macOS default) a case-variant spelling
        # names the same inode while resolve() preserves casing (codex
        # round-11), and samefile also covers hard/symlink aliases.
        if candidate.resolve() == protected.resolve():
            return True
        try:
            return candidate.exists() and protected.exists() and candidate.samefile(protected)
        except OSError:
            return False

    if _aliases_protected(args.archive, NEXT_ACTION_ARCHIVE) or _aliases_protected(
        args.archive, target_protected_archive
    ):
        print(
            f"--archive must not point at the protected next-action archive "
            f"({NEXT_ACTION_ARCHIVE}) — the drift-log trim would rewrite the "
            f"round history (U-CTX-03 AC #2)",
            file=sys.stderr,
        )
        return 2

    if args.emit_refresh_pr_json is not None:
        if args.dry_run:
            # r11 P2: the emitter checks out branches, commits, pushes, and creates a
            # PR — there is no side-effect-free preview. Refuse the combination.
            print(
                "--emit-refresh-pr-json is a mutating mode (checkout/commit/push/PR) "
                "and does not support --dry-run",
                file=sys.stderr,
            )
            return 2
        # STDOUT PURITY (codex r1 P1): merge_door.py json-parses this mode's ENTIRE
        # captured stdout, and the in-process `--refresh` re-invocation (plus anything
        # nested) prints progress lines. Route every nested write to stderr for the
        # whole emit; the one JSON line below is the only thing real stdout ever sees.
        real_stdout = sys.stdout
        with contextlib.redirect_stdout(sys.stderr):
            out = emit_refresh_pr(
                args.emit_refresh_pr_json,
                notes=args.notes,
                next_action=args.next_action,
                date=args.date,
            )
        print(json.dumps(out), file=real_stdout)
        return 0

    if args.state:
        print(json.dumps(compute_state().as_dict(), indent=2))
        return 0

    text = args.status.read_text()

    if args.check:
        violations = validate(text, args.status)
        shape_title = None
        if args.shape_title_env:
            shape_title = os.environ.get(args.shape_title_env)
            if not shape_title:
                # codex round-12: --shape-title-env names the AUTHORITATIVE
                # title source; a missing/empty variable silently falling back
                # to the commit subject would let a refresh-titled PR bypass
                # the base...head file-set check. Fail closed.
                print(
                    f"--shape-title-env {args.shape_title_env!r} is unset or empty — "
                    "refusing to fall back to the commit subject (the PR title is "
                    "the authoritative §12.2.1 invariant source)",
                    file=sys.stderr,
                )
                return 2
        violations.extend(
            check_head_refresh_shape(
                status_root, args.shape_ref, base=args.shape_base, title_override=shape_title
            )
        )
        # Severity is STRUCTURAL: only messages the validator itself prefixed
        # with INFORMATIONAL_PREFIX are soft (codex round-8 — a substring
        # search would let an attacker-controlled filename/title containing
        # the word "informational" silently soften a hard violation).
        hard = [v for v in violations if not v.startswith(INFORMATIONAL_PREFIX)]
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        if hard:
            print("ROADMAP STATUS CHECK FAILED:", file=sys.stderr)
            return 1
        head_bytes = len(text.encode("utf-8"))
        print(
            f"roadmap_status.md OK ({head_bytes}/{HEAD_BYTE_BUDGET} B, "
            f"headroom {HEAD_BYTE_BUDGET - head_bytes} B)"
        )
        return 0

    if args.trim_drift_log:
        # A drift event that OVERFLOWS the log deadlocked the documented
        # `--refresh --drift-source` workflow (codex round 5 [P1]): --refresh
        # prepends the row, the trim then needs an archive write, and --refresh
        # refuses — while pre-running --trim-drift-log was a no-op because the
        # row did not exist yet. So the CONTENT mode carries the new event: it
        # prepends and archives in one content commit, after which the
        # terminating --refresh is genuinely one-file.
        original = text
        if args.drift_source:
            if not args.date:
                ap.error("--trim-drift-log --drift-source requires --date")
            text = prepend_drift_log(
                text, args.date, args.drift_source, args.drift_resolution or ""
            )
        new_text, new_archive_text, moved = trim_drift_log(text, args.archive)
        # Same hard-cap refusal the rotation path applies (codex round 4): a
        # large new resolution is RETAINED by _drift_keep_count (the newest row
        # always survives), so this path could write past HEAD_BYTE_BUDGET and
        # exit 0 — a 10 KB resolution wrote 26,172 B, which validate() then
        # hard-rejects, guaranteeing the next CI check fails (codex round 9).
        trimmed_bytes = len(new_text.encode("utf-8"))
        if trimmed_bytes > HEAD_BYTE_BUDGET:
            print(
                f"--trim-drift-log would leave {args.status.name} at {trimmed_bytes} B, "
                f"over the {HEAD_BYTE_BUDGET} B hard cap (by "
                f"{trimmed_bytes - HEAD_BYTE_BUDGET} B) — refusing to write a status "
                "file --check would reject. Shorten the drift resolution text.",
                file=sys.stderr,
            )
            return 2
        if args.dry_run:
            print(f"would move {moved} row(s) to {args.archive}")
            return 0
        if new_archive_text is not None:
            args.archive.write_text(new_archive_text)
        # Compare against the ORIGINAL file, not the already-prepended text: a
        # small event that leaves the log under both limits makes trim_drift_log
        # a no-op, so `new_text != text` was False and the event was silently
        # DROPPED while the command printed "moved 0" and exited 0 (codex round
        # 6 [P2] — a regression the round-5 fix introduced).
        if new_text != original:
            args.status.write_text(new_text)
        print(f"moved {moved} row(s) to {args.archive}")
        return 0

    if args.archive_superseded:
        na_archive = status_root / ".harness" / "roadmap-next-action-archive.md"
        if not na_archive.is_file():
            print(f"next-action archive not found: {na_archive}", file=sys.stderr)
            return 2
        found = find_superseded_round(args.status, status_root)
        if found is None:
            print("no superseded next-action round found in history — nothing to archive")
            return 0
        label, paragraph = found
        new_archive = archive_superseded_round(paragraph, na_archive.read_text())
        if new_archive is None:
            print(f"superseded round post-#{label} is already archived — no change")
            return 0
        if args.dry_run:
            print(f"would archive superseded round post-#{label} to {na_archive.name}")
            return 0
        na_archive.write_text(new_archive)
        print(
            f"archived superseded round post-#{label} to {na_archive.name} "
            f"(ONE file; {args.status.name} untouched — this rides the CONTENT PR)"
        )
        return 0

    if args.refresh:
        if not (args.pr and args.date and args.notes is not None):
            ap.error("--refresh requires --pr --date --notes")
        state = compute_state(args.status.resolve().parents[1])
        last_refreshed = args.last_refreshed or f"{args.date}T00:00:00Z"
        new_text = refresh_anchor(text, state, args.git_head_note, last_refreshed)
        new_text = refresh_in_flight(new_text, state)
        new_text = prepend_recently_completed(new_text, args.pr, args.date, args.notes)
        if args.next_action is not None:
            new_text = install_next_action(new_text, args.pr, args.next_action)
        if args.drift_source:
            new_text = prepend_drift_log(
                new_text, args.date, args.drift_source, args.drift_resolution or ""
            )
        # §12.2.1, enforced instead of merely documented: a terminating refresh
        # commit must change EXACTLY `.harness/roadmap_status.md`. This mode used
        # to silently write `args.archive` too whenever the drift log overflowed,
        # producing a two-file commit that the shape gate then rejects — the
        # operator noticed only after the fact, and the workspace absorbed it as
        # "commit the trim separately" folklore. Refuse instead, and name the
        # mode that legitimately does the move.
        # Judge the refusal on the HARD requirement (the ROW CAP) ONLY. The byte
        # budget is SOFT guidance for a deliberate content-commit trim; keying the
        # refusal on it as well made EVERY terminating refresh refuse the moment
        # the live log exceeded that guidance — found by dogfooding this very
        # refresh, which the tool blocked outright. A soft budget must never gate
        # a hard path.
        trimmed_text, would_archive, would_move = trim_drift_log(
            new_text, args.archive, byte_budget=sys.maxsize
        )
        if would_archive is not None:
            print(
                f"--refresh would move {would_move} drift-log row(s) into "
                f"{args.archive.name}, making this a TWO-FILE commit — which "
                "cannot be a terminating refresh (§12.2.1 requires exactly "
                f"{DEFAULT_STATUS.name}). Run `--trim-drift-log` as its own content "
                "commit FIRST, then re-run --refresh. If the overflow is caused by a "
                "NEW drift event, pass it to that content step instead — "
                "`--trim-drift-log --drift-source ... --drift-resolution ... --date ...` "
                "— since pre-trimming cannot help with a row that does not exist yet.",
                file=sys.stderr,
            )
            return 2
        # No archive WRITE is needed — but the trim can STILL change the status
        # text, when the overflow rows are already present in the archive (an
        # idempotent re-run, or a --trim-drift-log whose archive write landed and
        # whose status write did not). Discarding the trimmed text there wrote a
        # still-over-budget status and reported success — a fail-open found by
        # out-of-family review, round 1. Decide from the status DELTA, and keep
        # the trimmed text; this stays a one-file write either way.
        moved = would_move
        if trimmed_text != new_text:
            moved = len(_get_table_data_rows(new_text, DRIFT_LOG_HEADING)) - len(
                _get_table_data_rows(trimmed_text, DRIFT_LOG_HEADING)
            )
            new_text = trimmed_text
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
        head_bytes = len(new_text.encode("utf-8"))
        # The same pre-write hard-cap refusal the rotation and trim paths carry:
        # --next-action can push the head past the cap, and writing it would ship
        # a status file --check rejects (codex round 12 [P2]).
        if head_bytes > HEAD_BYTE_BUDGET:
            print(
                f"--refresh would leave {args.status.name} at {head_bytes} B, over the "
                f"{HEAD_BYTE_BUDGET} B hard cap (by {head_bytes - HEAD_BYTE_BUDGET} B) — "
                "refusing to write a status file --check would reject. Shorten "
                "--next-action/--notes, or run --trim-drift-log first.",
                file=sys.stderr,
            )
            return 2
        args.status.write_text(new_text)
        print(
            f"refreshed {args.status}: hash={state.hash12()} in_flight={state.open_pr_count} "
            f"drift_log_moved={moved} "
            f"head_bytes={head_bytes}/{HEAD_BYTE_BUDGET} "
            f"(headroom {HEAD_BYTE_BUDGET - head_bytes} B)"
        )
        return 0

    ap.print_help()
    return 0


def _cli() -> int:
    """Surface a structural refusal as a clean exit 2, never a traceback."""
    try:
        return main()
    except RoadmapStatusError as e:
        print(f"roadmap_status_refresh: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_cli())

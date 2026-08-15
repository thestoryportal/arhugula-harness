#!/usr/bin/env python3
"""Deterministic forward-work briefing -- the engine behind the `/prime` slash command.

Every figure is derived at run time from a named source. Nothing is hand-maintained,
nothing is imputed, and no wall-clock `now()` is read -- two runs at the same HEAD with
the same remote state emit byte-identical output.

Fail-loud discipline (mirrors `tools/arc_metrics.py`): an input that cannot be read is
reported as `UNAVAILABLE: <cause>`, never silently zeroed and never reported as a clean
zero. A section that could not look must not read as a section that looked and found
nothing.

Sources
  .harness/forward-register.yaml   row inventory + status (current, and via `git show`
                                   at the prior session boundary for the delta)
  git log                          session clustering, PR->merge timestamps
  tools/codex_context_guard.py     roadmap terminating-refresh lag state
  gh pr list                       open PRs (network; fail-soft-but-loud)

Session boundary: commits are clustered by inactivity gap -- a gap larger than
--gap-hours (default 5) starts a new session. This is a fixed rule over commit
timestamps, so the "last session" window is reproducible rather than judged.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTER_REL = ".harness/forward-register.yaml"
REGISTER = ROOT / REGISTER_REL

DEFAULT_GAP_HOURS = 5.0
DESC_WIDTH = 138
RATE_WINDOW = 10  # closure-bearing sessions used for the throughput estimate

# Buckets in report order: (status, heading, gloss, counts_toward_estimate)
BUCKETS: list[tuple[str, str, str, bool]] = [
    ("open", "IN FLIGHT", "arc opened, not yet closed", True),
    ("design_substrate_gated", "OPERATOR-GATED", "grounded; blocked on your decision", False),
    ("operator_gated", "OPERATOR-GATED", "grounded; blocked on your decision", False),
    ("registered_finding", "ACTIONABLE", "grounded findings, agent-executable", True),
    ("held", "HELD", "ratified defers -- do not reopen without a fresh operator call", False),
]

PR_IN_SUBJECT = re.compile(r"\(#(\d+)\)\s*$")
PR_REFERENCE = re.compile(r"#(\d+)")
ID_SORT = re.compile(r"^([A-Za-z-]*?)-?(\d+)$")


class UnavailableError(Exception):
    """A named input could not be read. Carries the cause for verbatim reporting."""


@dataclass(frozen=True)
class Commit:
    sha: str
    ts: int
    subject: str


def run(*args: str, check: bool = True, timeout: int = 60) -> str:
    try:
        proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UnavailableError(f"`{' '.join(args[:3])}`: {exc}") from exc
    if check and proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip().splitlines()
        cause = detail[0][:160] if detail else f"exit {proc.returncode}"
        raise UnavailableError(f"`{' '.join(args[:3])}` exit {proc.returncode}: {cause}")
    return proc.stdout


def brief(text: str, width: int = DESC_WIDTH) -> str:
    """Collapse to one line and truncate at a word boundary. Deterministic."""
    flat = " ".join(str(text).split())
    if len(flat) <= width:
        return flat
    cut = flat[:width]
    space = cut.rfind(" ")
    if space > width * 0.6:
        cut = cut[:space]
    return cut.rstrip(" ,;:.-—") + "…"


def id_key(item_id: str) -> tuple[str, int]:
    match = ID_SORT.match(item_id)
    if not match:
        return (item_id, 0)
    return (match.group(1), int(match.group(2)))


def load_register(text: str, origin: str) -> tuple[dict[str, dict], dict]:
    try:
        doc = yaml.safe_load(text)
        return {it["id"]: it for it in doc["items"]}, doc.get("snapshot", {}) or {}
    except (yaml.YAMLError, KeyError, TypeError) as exc:
        raise UnavailableError(f"{origin} did not parse as the register schema: {exc}") from exc


def git_commits(limit: int) -> list[Commit]:
    out = run("git", "log", f"-{limit}", "--format=%H\x1f%ct\x1f%s")
    commits: list[Commit] = []
    for line in out.splitlines():
        parts = line.split("\x1f", 2)
        if len(parts) != 3:
            continue
        commits.append(Commit(parts[0], int(parts[1]), parts[2]))
    if not commits:
        raise UnavailableError("git log returned no commits")
    return commits


def cluster_sessions(commits: list[Commit], gap_hours: float) -> list[list[Commit]]:
    """Split a newest-first commit list into sessions on inactivity gaps."""
    gap = gap_hours * 3600
    sessions: list[list[Commit]] = []
    current = [commits[0]]
    for newer, older in itertools.pairwise(commits):
        if newer.ts - older.ts > gap:
            sessions.append(current)
            current = [older]
        else:
            current.append(older)
    sessions.append(current)
    return sessions


def pr_merge_timestamps(commits: list[Commit]) -> dict[int, int]:
    """PR number -> merge commit timestamp, from trailing `(#N)` in squash subjects."""
    stamps: dict[int, int] = {}
    for commit in commits:  # newest-first; setdefault keeps the newest match
        match = PR_IN_SUBJECT.search(commit.subject)
        if match:
            stamps.setdefault(int(match.group(1)), commit.ts)
    return stamps


def row_pr(item: dict) -> int | None:
    """Closing PR number for a row -- the highest `#N` reference in its `pr` field.

    The field carries three shapes and all three are live in the register:

    - a YAML integer (`pr: 1331` -- B-136/B-161/B-162/B-163)
    - a bare numeric string (`pr: '994'`)
    - free prose citing several legs plus bare dates
      ("#1224 (fork filing) + #1233 (the 2026-08-05 ratification) + #1241 (build leg)")

    Only the prose shape is scanned for `#`-prefixed tokens, because matching bare digits
    inside prose would read `2026` out of a date. The highest reference is the closing
    leg. A row citing no PR at all (e.g. an operator ratification) returns None and is
    reported as unmapped -- never imputed.
    """
    raw = item.get("pr")
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw
    text = str(raw).strip()
    if text.isdigit():
        return int(text)
    found = PR_REFERENCE.findall(text)
    return max(int(n) for n in found) if found else None


def fmt_span(minutes: float) -> str:
    if minutes < 90:
        return f"{minutes:.0f}m"
    hours = minutes / 60
    if hours < 40:
        return f"{hours:.1f}h"
    return f"{hours:.0f}h"


# --------------------------------------------------------------------------- sections


def section_delta(
    sessions: list[list[Commit]],
    current: dict[str, dict],
    gap_hours: float,
    out: list[str],
) -> None:
    """What closed / surfaced / transited during the most recent session."""
    head_session = sessions[0]
    span_min = (head_session[0].ts - head_session[-1].ts) / 60
    day = run("git", "show", "-s", "--format=%cs", head_session[0].sha).strip()
    out.append(
        f"LAST SESSION  {day}  |  {len(head_session)} commits over {fmt_span(span_min)}"
        f"  (boundary: >{gap_hours:g}h gap)"
    )

    if len(sessions) < 2:
        out.append("  delta   UNAVAILABLE: no prior session in the scanned window")
        return

    boundary = sessions[1][0]
    try:
        prior_text = run("git", "show", f"{boundary.sha}:{REGISTER_REL}")
        prior, _ = load_register(prior_text, f"register at {boundary.sha[:8]}")
    except UnavailableError as exc:
        out.append(f"  delta   UNAVAILABLE: {exc}")
        return

    surfaced = sorted(set(current) - set(prior), key=id_key)
    closed: list[str] = []
    transited: list[str] = []
    for item_id in sorted(set(current) & set(prior), key=id_key):
        was = prior[item_id].get("status")
        now = current[item_id].get("status")
        if was == now:
            continue
        if now == "closed":
            closed.append(item_id)
        else:
            transited.append(f"{item_id} {was}->{now}")

    new_and_closed = [i for i in surfaced if current[i].get("status") == "closed"]
    all_closed = closed + new_and_closed
    out.append(f"  closed    {len(all_closed):>2}   " + (", ".join(all_closed) or "none"))
    out.append(f"  surfaced  {len(surfaced):>2}   " + (", ".join(surfaced) or "none"))
    out.append(f"  transited {len(transited):>2}   " + (", ".join(transited) or "none"))
    # A row can be both surfaced and closed in one session -- list it once.
    for item_id in dict.fromkeys(all_closed + surfaced):
        out.append(f"      {item_id:<7} {brief(current[item_id]['title'], 110)}")


def section_estimate(
    sessions: list[list[Commit]],
    commits: list[Commit],
    current: dict[str, dict],
    counts: dict[str, int],
    out: list[str],
) -> None:
    """Remaining wall clock, from this repo's own measured closure throughput."""
    stamps = pr_merge_timestamps(commits)
    closed_ts: list[int] = []
    unmapped = 0
    for item in current.values():
        if item.get("status") != "closed":
            continue
        pr = row_pr(item)
        ts = stamps.get(pr) if pr else None
        if ts is None:
            unmapped += 1
        else:
            closed_ts.append(ts)

    # Attribute each measured closure to the session window containing it.
    measured: list[tuple[float, int]] = []  # (session span minutes, rows closed)
    for session in sessions:
        newest, oldest = session[0].ts, session[-1].ts
        rows = sum(1 for ts in closed_ts if oldest <= ts <= newest)
        if rows:
            measured.append(((newest - oldest) / 60, rows))
    window = measured[:RATE_WINDOW]

    actionable = sum(counts.get(status, 0) for status, _, _, inc in BUCKETS if inc)
    blocked = sum(counts.get(status, 0) for status, _, _, inc in BUCKETS if not inc)

    out.append(f"ESTIMATE TO CLOSE  ({actionable} agent-executable rows)")
    if not window:
        out.append("  UNAVAILABLE: no closure-bearing session in the scanned window")
        return

    total_min = sum(span for span, _ in window)
    total_rows = sum(rows for _, rows in window)
    rate = total_min / total_rows
    per_session = total_rows / len(window)

    out.append(
        f"  basis     {total_rows} rows closed across {len(window)} sessions"
        f" = {fmt_span(rate)}/row, {per_session:.1f} rows/session"
    )
    out.append(
        f"  remaining {fmt_span(actionable * rate)} active"
        f"  (~{actionable / per_session:.0f} sessions at the observed rate)"
    )
    out.append(
        f"  excluded  {blocked} rows blocked on you (operator-gated + held) -- not estimable"
    )
    caveats = []
    if unmapped:
        caveats.append(
            f"{unmapped} older closed rows have no PR in the scanned log (pre-history-floor); "
            "they are outside the rate window and do not move the estimate"
        )
    caveats.append("span-based: counts elapsed session time, not effort")
    out.append("  caveat    " + "; ".join(caveats))


def section_work(current: dict[str, dict], counts: dict[str, int], out: list[str]) -> None:
    total_open = sum(n for status, n in counts.items() if status != "closed")
    out.append(f"REMAINING FORWARD WORK  ({total_open} rows)")
    emitted: set[str] = set()
    for status, heading, gloss, _ in BUCKETS:
        rows = sorted((i for i, it in current.items() if it.get("status") == status), key=id_key)
        if not rows:
            continue
        out.append(f"  -- {heading} ({len(rows)}) -- {gloss}")
        for item_id in rows:
            out.append(f"  {item_id:<7} {brief(current[item_id]['title'])}")
            emitted.add(item_id)

    stray = sorted(
        (i for i, it in current.items() if it.get("status") != "closed" and i not in emitted),
        key=id_key,
    )
    if stray:
        out.append(f"  -- UNCLASSIFIED ({len(stray)}) -- status not in the known bucket set")
        for item_id in stray:
            status = current[item_id].get("status")
            out.append(f"  {item_id:<7} [{status}] {brief(current[item_id]['title'], 120)}")


def _flag_worktree(out: list[str], flags: list[str]) -> None:
    try:
        porcelain = [x for x in run("git", "status", "--porcelain").splitlines() if x.strip()]
    except UnavailableError as exc:
        flags.append(f"worktree state UNAVAILABLE: {exc}")
        return
    dirty = [x for x in porcelain if not x.startswith("??")]
    untracked = [x for x in porcelain if x.startswith("??")]
    if dirty:
        flags.append(f"{len(dirty)} uncommitted change(s): " + ", ".join(x[3:] for x in dirty[:4]))
    if untracked:
        flags.append(
            f"{len(untracked)} untracked path(s): " + ", ".join(x[3:] for x in untracked[:5])
        )
    if not porcelain:
        out.append("  worktree  clean")


def _flag_branches(flags: list[str]) -> None:
    """Branch hygiene is a REMOTE-list discipline, so read the remote, not local refs.

    `.claude/skills/ship-pr/SKILL.md` §"Branch hygiene close-out" is explicit that the
    §10 rule "is about the remote (GitHub) branch list, not local `.git/refs/heads/*`
    pointers -- local refs are single-clone, cosmetic, and reflog-recoverable regardless".
    Flagging local topic refs produced a standing false action item on every run.
    """
    try:
        listing = run("git", "ls-remote", "--heads", "origin", timeout=90)
    except UnavailableError as exc:
        flags.append(f"remote branch list UNAVAILABLE: {exc}")
        return
    branches = sorted(
        line.split("refs/heads/", 1)[1] for line in listing.splitlines() if "refs/heads/" in line
    )
    stale = [b for b in branches if b != "main"]
    if stale:
        flags.append(
            f"{len(stale)} remote branch(es) beyond main -- CLAUDE.md s10 requires none "
            f"before a merge action (e.g. {', '.join(stale[:3])})"
        )


def _flag_worktrees(flags: list[str]) -> None:
    """Report the count only -- collectability is `codex_worktree_gc`'s judgement, not ours.

    That tool proves cleanliness, inactivity and merge status before calling a worktree
    collectable; asserting "candidate" here would manufacture action items for worktrees
    that are active, dirty, detached, or unmerged.
    """
    try:
        trees = [x for x in run("git", "worktree", "list").splitlines() if x.strip()]
    except UnavailableError as exc:
        flags.append(f"worktree list UNAVAILABLE: {exc}")
        return
    if len(trees) > 1:
        flags.append(
            f"{len(trees) - 1} extra worktree(s) registered -- not classified here; run "
            "`uv run python tools/codex_worktree_gc.py --dry-run` for what is collectable"
        )


def _flag_sync(flags: list[str]) -> None:
    """Compare origin/main against the LOCAL MAIN REF, never HEAD.

    /prime is normally run from a topic branch or a linked worktree, where
    `origin/main...HEAD` measures that checkout and not main -- reporting it as
    "local main N ahead" is simply false there.
    """
    try:
        parts = run(
            "git", "rev-list", "--left-right", "--count", "origin/main...refs/heads/main"
        ).split()
        behind, ahead = int(parts[0]), int(parts[1])
    except (UnavailableError, ValueError, IndexError) as exc:
        flags.append(f"main-vs-origin state UNAVAILABLE: {exc}")
        return
    if behind or ahead:
        flags.append(
            f"local main {ahead} ahead / {behind} behind origin/main "
            "(as of last fetch; none performed)"
        )


def _flag_roadmap(out: list[str], flags: list[str]) -> None:
    """Surface the context guard's own hard findings plus the refresh-lag state.

    The guard exits non-zero whenever it has any hard finding, so its exit code is a
    verdict, not a failure -- read stdout regardless and let a JSON parse failure (the
    genuine "could not look" case) be the only UNAVAILABLE.
    """
    try:
        guard = json.loads(
            run(
                "uv",
                "run",
                "python",
                "tools/codex_context_guard.py",
                "check",
                "--json",
                check=False,
                timeout=180,
            )
        )
    except (UnavailableError, json.JSONDecodeError) as exc:
        flags.append(f"context guard UNAVAILABLE: {exc}")
        return

    for finding in guard.get("findings") or []:
        if finding.get("severity") == "hard":
            flags.append(f"guard {finding.get('code')}: {brief(finding.get('message', ''), 110)}")

    if guard.get("owed_lag"):
        flags.append(
            "terminating roadmap refresh OWED -- next commit must be the refresh (s12.2.1)"
        )
    elif guard.get("lag_expected"):
        out.append("  roadmap   at the s12.2.1 fixed point (expected one-commit lag)")


def _flag_prs(out: list[str], flags: list[str]) -> None:
    try:
        prs = json.loads(
            run(
                "gh",
                "pr",
                "list",
                "--state",
                "open",
                "--json",
                "number,title,isDraft,mergeable,statusCheckRollup",
                timeout=90,
            )
        )
    except (UnavailableError, json.JSONDecodeError) as exc:
        flags.append(f"open PRs UNAVAILABLE: {exc}")
        return
    if not prs:
        out.append("  open PRs  none")
        return
    for pr in prs:
        checks = pr.get("statusCheckRollup") or []
        # Fail closed: SUCCESS is the ONLY green conclusion. Enumerating the bad ones
        # instead would silently score ACTION_REQUIRED / STARTUP_FAILURE / STALE as ok
        # and render a non-green PR as green, against the repo's strict-CI rule.
        pending = sum(1 for c in checks if not c.get("conclusion"))
        bad = sum(1 for c in checks if c.get("conclusion") and c.get("conclusion") != "SUCCESS")
        state = f"mergeable={pr.get('mergeable')}"
        if checks:
            state += f", checks {len(checks) - bad - pending}ok/{bad}bad/{pending}pending"
        else:
            state += ", no checks reported (not-yet-started, NOT green)"
        flags.append(f"open PR #{pr['number']} {brief(pr['title'], 60)} -- {state}")


def section_git(out: list[str]) -> None:
    out.append("GIT ACTIONS")
    flags: list[str] = []
    _flag_worktree(out, flags)
    _flag_branches(flags)
    _flag_worktrees(flags)
    _flag_sync(flags)
    _flag_roadmap(out, flags)
    _flag_prs(out, flags)
    for flag in flags:
        out.append(f"  FLAG      {flag}")
    if not flags:
        out.append("  no action required")


# ------------------------------------------------------------------------------- main


def build_report(gap_hours: float, limit: int) -> str:
    commits = git_commits(limit)
    sessions = cluster_sessions(commits, gap_hours)
    current, snapshot = load_register(REGISTER.read_text(), REGISTER_REL)

    counts: dict[str, int] = {}
    for item in current.values():
        status = item.get("status", "?")
        counts[status] = counts.get(status, 0) + 1
    closed = counts.get("closed", 0)
    total = len(current)

    out: list[str] = []
    head = commits[0]
    out.append(
        f"PRIME  |  HEAD {head.sha[:8]}  |  register {total} rows, "
        f"digest {snapshot.get('identity_digest', '?')}"
    )
    out.append(
        f"CLOSED TO DATE  {closed}/{total} ({closed / total * 100:.1f}%)  |  "
        + "  ".join(
            f"{status}={counts.get(status, 0)}" for status, _, _, _ in BUCKETS if counts.get(status)
        )
    )
    out.append("")
    section_delta(sessions, current, gap_hours, out)
    out.append("")
    section_estimate(sessions, commits, current, counts, out)
    out.append("")
    section_work(current, counts, out)
    out.append("")
    section_git(out)
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--gap-hours",
        type=float,
        default=DEFAULT_GAP_HOURS,
        help="inactivity gap that starts a new session (default 5)",
    )
    parser.add_argument("--limit", type=int, default=1500, help="commits to scan (default 1500)")
    args = parser.parse_args()
    try:
        print(build_report(args.gap_hours, args.limit))
    except UnavailableError as exc:
        print(
            f"PRIME ABORTED -- a load-bearing input could not be read: {exc}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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

# Buckets in report order: (status, heading, gloss, counts_toward_estimate).
#
# A `*_gated` row is NOT asserted to be blocked on the operator. CLAUDE.md §12.4.1 is
# explicit that a gate label means "drive it to its genuine gate", not "parked" -- and
# the live counterexample is B-139, whose own fork doc says a C5+C7/C9 council is owed
# BEFORE the operator ratifies, i.e. its next step is agent-executable. Deciding which
# gated rows are agent-ready needs per-row prose judgement, which would not be
# deterministic, so they are reported separately and excluded from the estimate FLOOR
# rather than silently relabelled as the operator's problem.
BUCKETS: list[tuple[str, str, str, bool]] = [
    ("open", "IN FLIGHT", "arc opened, not yet closed", True),
    (
        "design_substrate_gated",
        "GATED",
        "grounded; a decision gate is open -- NOT parked (s12.4.1): the next step may "
        "still be agent-executable (e.g. an owed council), so ground each before blocking",
        False,
    ),
    (
        "operator_gated",
        "GATED",
        "grounded; a decision gate is open -- NOT parked (s12.4.1): ground before blocking",
        False,
    ),
    ("registered_finding", "ACTIONABLE", "grounded findings, agent-executable", True),
    ("held", "HELD", "ratified defers -- do not reopen without a fresh operator call", False),
]

PR_IN_SUBJECT = re.compile(r"\(#(\d+)\)\s*$")
PR_REFERENCE = re.compile(r"#(\d+)")
# A leading bare number is the closing leg ("1078 (impl leg); spec leg at PR #1077").
# The lookahead keeps a leading date ("2026-08-05 ...") from reading as a PR. It must
# exclude DIGITS as well as "-": with a bare (?!-) the engine backtracks "2026" -> "202",
# sees "6" (not "-"), and matches 202. Excluding digits denies every backtrack too.
PR_LEADING_BARE = re.compile(r"^(\d+)(?![\d-])")
ID_SORT = re.compile(r"^([A-Za-z-]*?)-?(\d+)$")
# Everything in the report reaches the model's prompt inside a Markdown fence, and some
# of it is network-controlled (PR titles, remote refnames -- git permits backticks in a
# refname). Strip what could close the fence or read as instructions. Applied in brief(),
# so every rendered string goes through it.
UNSAFE_IN_PROMPT = re.compile(r"[`\x00-\x1f\x7f]")


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
    """Collapse to one line, strip fence-breakers, truncate at a word boundary.

    The sanitization lives HERE rather than at the untrusted call sites, because every
    string in the report reaches the model's prompt through `/prime` and is relayed
    inside a Markdown fence. Guarding only the obviously-untrusted fields left holes:
    a git refname may legally contain backticks, so a remote branch name could close
    the fence just as a PR title could. One choke point covers titles, branch names,
    register rows, and anything added later.
    """
    flat = " ".join(UNSAFE_IN_PROMPT.sub("", str(text)).split())
    if len(flat) <= width:
        return flat
    cut = flat[:width]
    space = cut.rfind(" ")
    if space > width * 0.6:
        cut = cut[:space]
    return cut.rstrip(" ,;:.-—") + "…"


def safe_title(text: str, width: int = 60) -> str:
    """Network-controlled text at report width. Sanitization is `brief`'s job."""
    return brief(text, width)


def check_outcome(check: dict) -> str | None:
    """Terminal outcome of one statusCheckRollup entry, or None if still running.

    The rollup is a UNION: a CheckRun reports `conclusion`, while a legacy commit status
    (StatusContext) reports `state` and carries no `conclusion` at all. Reading only
    `conclusion` scores every legacy status as forever-pending -- which both hides a
    terminal FAILURE from the bad count and stops a green one from ever counting.
    """
    for field in ("conclusion", "state"):
        value = check.get(field)
        if value:
            return str(value).upper()
    return None


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

    In prose, two token shapes count and a third must not:

    - `#N` anywhere ("spec leg at PR #1077")
    - a LEADING bare number, which is how the closing leg is written when a row cites
      several ("1078 (impl leg); spec leg at PR #1077" -- B-65; "1078 (...)" -- B-67).
      Without it B-65 resolved to 1077, the wrong PR, and B-67 to None.
    - a bare date component must NOT count: `2026-08-05` would otherwise read as PR 2026.
      The leading-number rule excludes it via a `(?!-)` lookahead, and non-leading bare
      numbers are never scanned at all.

    The highest surviving candidate is the closing leg. A row citing no PR (e.g. an
    operator ratification) returns None and is reported as unmapped -- never imputed.
    """
    raw = item.get("pr")
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw
    text = str(raw).strip()
    if text.isdigit():
        return int(text)
    candidates = [int(n) for n in PR_REFERENCE.findall(text)]
    leading = PR_LEADING_BARE.match(text)
    if leading:
        candidates.append(int(leading.group(1)))
    return max(candidates) if candidates else None


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

    gated = sum(counts.get(status, 0) for status, heading, _, _ in BUCKETS if heading == "GATED")
    held = counts.get("held", 0)

    out.append(f"ESTIMATE TO CLOSE  ({actionable} agent-executable rows -- a FLOOR)")
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
        f"  excluded  {blocked} rows ({gated} gated + {held} held). The gated rows are NOT "
        "asserted blocked on you -- s12.4.1: ground each; some have an agent-executable "
        "next step (an owed council), so the figure above is a floor, not a total."
    )
    caveats = []
    if unmapped:
        # Do NOT claim these are all old. The bucket also holds rows that cite no PR at
        # all (an operator ratification), which row_pr supports on purpose -- calling
        # those "pre-history-floor" would be a false explanation.
        caveats.append(
            f"{unmapped} closed rows have no PR resolvable in the scanned log -- older "
            "than the history floor, cited no PR, or beyond --limit; each is outside the "
            "rate window and does not move the estimate"
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

    The CURRENT CI branch is exempt: the same rule permits it and deletes it only after
    post-merge CI, so flagging it would fire on every ordinary pre-merge run.

    Identifying "current" by NAME alone is not enough. `rev-parse --abbrev-ref HEAD`
    returns the literal "HEAD" in a detached worktree, and detached review worktrees are
    a normal mode here (AGENTS.md requires isolated worktrees) -- so a name-only rule
    flagged this very PR's own branch. Matching the remote tip SHA against HEAD covers
    the detached case; the name check still covers a pushed branch whose local tip has
    since moved on.
    """
    try:
        listing = run("git", "ls-remote", "--heads", "origin", timeout=90)
        current = run("git", "rev-parse", "--abbrev-ref", "HEAD").strip()
        head_sha = run("git", "rev-parse", "HEAD").strip()
    except UnavailableError as exc:
        flags.append(f"remote branch list UNAVAILABLE: {exc}")
        return

    remote: dict[str, str] = {}
    for line in listing.splitlines():
        if "refs/heads/" in line:
            sha, ref = line.split("refs/heads/", 1)
            remote[ref.strip()] = sha.strip()

    # Exempt exactly ONE branch, because the rule permits exactly one: the current CI
    # branch. Prefer the name when HEAD is attached. When detached, fall back to the ref
    # at HEAD -- but only if it is UNAMBIGUOUS: if several refs share the SHA (a copied
    # branch beside its stale predecessor) there is no deterministic way to tell which
    # is current, so exempt none and let them be reported. Over-reporting is the safe
    # direction for a hygiene flag; silently exempting a stale branch is not.
    exempt = {"main"}
    if current in remote:
        exempt.add(current)
    else:
        at_head = [name for name, sha in remote.items() if sha == head_sha]
        if len(at_head) == 1:
            exempt.add(at_head[0])

    stale = sorted(name for name in remote if name not in exempt)
    if stale:
        flags.append(
            f"{len(stale)} remote branch(es) beyond main + the current CI branch -- "
            f"CLAUDE.md s10 requires none before a merge action "
            f"(e.g. {', '.join(brief(b, 40) for b in stale[:3])})"
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
                # gh defaults to 30 and truncates SILENTLY -- the one failure mode this
                # report must never have.
                "--limit",
                "200",
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
        # Fail closed: SUCCESS is the ONLY green outcome. Enumerating the bad ones
        # instead would silently score ACTION_REQUIRED / STARTUP_FAILURE / STALE as ok
        # and render a non-green PR as green, against the repo's strict-CI rule.
        outcomes = [check_outcome(c) for c in checks]
        pending = sum(1 for o in outcomes if o is None)
        bad = sum(1 for o in outcomes if o is not None and o != "SUCCESS")
        state = f"mergeable={pr.get('mergeable')}"
        if checks:
            state += f", checks {len(checks) - bad - pending}ok/{bad}bad/{pending}pending"
        else:
            state += ", no checks reported (not-yet-started, NOT green)"
        flags.append(f"open PR #{pr['number']} {safe_title(pr['title'])} -- {state}")


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

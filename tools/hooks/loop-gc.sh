#!/usr/bin/env bash
# SessionStart worktree hygiene visibility (U-HK-26).
#
# The autonomous loop ships PRs whose worktrees go stale after merge; nothing reaps
# them (git-arc-guard checks commits/branches and session-end-cleanup is advisory-only).
# SessionStart is a latency-sensitive lease/context boundary, so this hook only reports
# candidates. The controller performs explicit reaping after merge/closeout.
#
#   ALL MODES → VISIBILITY: inject advisory additionalContext listing stale-worktree
#               candidates + their branch refs + a MEMORY.md over-cap flag + the
#               U-HK-44 unreconciled-subagent clause. Never delete.
#
# Runs as deterministic hook bash and always exits 0.

set -uo pipefail
_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -f "$_DIR/lib.sh" ] || exit 0
# shellcheck source=lib.sh
. "$_DIR/lib.sh"
hook_review_isolated && exit 0
[ -f "$_DIR/loop_lib.sh" ] || exit 0
# shellcheck source=loop_lib.sh
. "$_DIR/loop_lib.sh"

PROJECT_DIR=$(hook_project_dir); [ -z "$PROJECT_DIR" ] && exit 0

# Advisory visibility only. Cheap pre-check: only pay for the gh
# merged-set lookup when there is MORE than one worktree (the common case — sitting
# in main with no linked worktrees — pays nothing and adds zero SessionStart latency).
CANDS=""
WTC=$(git -C "$PROJECT_DIR" worktree list 2>/dev/null | grep -c .)
[ "${WTC:-0}" -ge 2 ] 2>/dev/null && CANDS=$(loop_gc_worktrees report)

MEMFLAG=""
# Claude Code keys project memory by the MAIN repo path (not a worktree) with '/' -> '-'.
# The first `git worktree list` entry is always the main working tree, so derive the
# encoded memory dir from it — portable across checkouts/users (was hardcoded; codex P2).
# Strip the `worktree ` prefix (not awk $2) so a path containing spaces survives.
MAIN_REPO=$(git -C "$PROJECT_DIR" worktree list --porcelain 2>/dev/null | sed -n '1s/^worktree //p')
[ -z "$MAIN_REPO" ] && MAIN_REPO="$PROJECT_DIR"
MEM="$HOME/.claude/projects/$(printf '%s' "$MAIN_REPO" | tr '/' '-')/memory/MEMORY.md"
if [ -f "$MEM" ]; then
  SZ=$(wc -c < "$MEM" | tr -d ' ')
  [ "${SZ:-0}" -gt 24400 ] 2>/dev/null && MEMFLAG="MEMORY.md ${SZ}B > 24400B cap — compact (shorten index lines; full text lives at memory/<slug>.md)."
fi

# ── U-HK-44 unreconciled-subagent sweep + prune ───────────────────────────────
# Reports subagent lifecycle keys that recorded a `start` and never an accepted `stop`
# in the U-HK-43 registry, and prunes rows older than 7 days. Honesty framing (inherited
# from U-HK-43): Agent-tool subagents are API tasks, not OS processes — there is no pid
# and no `kill -0`, so the term is UNRECONCILED, never "orphaned"; nothing is killed.
#
# Cheap pre-check (existing discipline): no registry file → the whole feature is skipped
# and SessionStart pays nothing. The sweep+prune is ONE /usr/bin/python3 invocation,
# self-bounded (~2s lock-acquisition deadline on the prune arm only) and
# failure-invisible: any python failure yields no clause on stdout, leaves loop-gc
# otherwise byte-identical, and this hook still exits 0.
UNREC=""
REGISTRY="$PROJECT_DIR/.harness/.agents-registry.jsonl"
if [ -f "$REGISTRY" ]; then
  UNREC=$(/usr/bin/python3 - "$REGISTRY" 2>/dev/null <<'PY'
import calendar
import fcntl
import json
import os
import sys
import time
from pathlib import Path

STALE = 30 * 60.0        # unreconciled younger than this is a LIVE fan-out → never alarm
KEEP = 7 * 86400.0       # rows older than this are pruned
DEADLINE = 2.0           # lock-ACQUISITION budget for the prune arm; never blocks longer

registry = Path(sys.argv[1])
now = time.time()


def parsed(text):
    """Parseable object rows, paired with their exact source line.

    A SIGKILL mid-write can leave ONE torn tail line: malformed lines are SKIPPED, never
    aborting the sweep (and they are dropped by the prune rewrite below).
    """
    out = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        if isinstance(row, dict):
            out.append((line, row))
    return out


def human(age):
    if age == float("inf"):
        return "transcript missing"
    if age >= 86400:
        return "%dd" % int(age // 86400)
    if age >= 3600:
        return "%dh" % int(age // 3600)
    return "%dm" % int(age // 60)


try:
    raw = registry.read_text(encoding="utf-8", errors="replace")
except Exception:
    raise SystemExit(0)

# ── sweep (no lock — reading an append-only file needs none) ──────────────────
# Key: `agent_id` when non-empty, else the transcript path (U-HK-43 records the fallback
# PARENT-FIRST, so a start and its stop land on the same key). PER-KEY counting:
# unreconciled = count(start) - count(stop) on that key. Every accepted stop counts (no
# dedup) and offsets ONLY its own key, so N fan-out siblings sharing one fallback key are
# never zeroed by a single stop. `stop_blocked` is NONTERMINAL — the subagent retries, so
# it never reconciles anything.
starts, stops, paths = {}, {}, {}
for _, row in parsed(raw):
    transcript = (row.get("transcript") or "").strip()
    key = (row.get("agent_id") or "").strip() or transcript
    if not key:
        continue
    if transcript:
        paths.setdefault(key, transcript)
    event = row.get("event")
    if event == "start":
        starts[key] = starts.get(key, 0) + 1
    elif event == "stop":
        stops[key] = stops.get(key, 0) + 1

stale = []
for key, count in starts.items():
    deficit = count - stops.get(key, 0)
    if deficit <= 0:
        continue
    path = paths.get(key, "")
    if not path:
        continue  # no recorded transcript → nothing to age against → stay quiet
    try:
        age = now - os.stat(path).st_mtime
    except OSError:
        # Path recorded but the file is GONE — the agent is certainly not live → stale.
        age = float("inf")
    if age > STALE:
        stale.append((age, key, deficit))

clause = ""
if stale:
    total = sum(deficit for _, _, deficit in stale)
    age, key, _ = max(stale, key=lambda entry: entry[0])
    clause = "%d unreconciled subagent(s) (oldest: %s, %s)." % (total, key, human(age))

# ── prune (REWRITE — takes the SAME advisory lock the U-HK-43 appender takes) ──
# An unlocked tmp-file + rename swap races a concurrent append onto the replaced inode and
# silently loses accepted events. Lock busy past the deadline → SKIP this tick; SessionStart
# is never blocked.


def prune():
    lock = registry.with_suffix(".lock")
    try:
        stream = lock.open("a+")
    except Exception:
        return
    with stream:
        deadline = time.monotonic() + DEADLINE
        while True:
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    return  # lock held elsewhere → skip the prune, report anyway
                time.sleep(0.01)
        # Lock held. Re-read INSIDE the locked region: rows appended between the sweep's
        # unlocked read and this acquisition MUST survive the rewrite.
        try:
            current = registry.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return
        kept, dropped = [], 0
        for line, row in parsed(current):
            try:
                old = now - calendar.timegm(
                    time.strptime(row["ts"], "%Y-%m-%dT%H:%M:%SZ")
                ) > KEEP
            except Exception:
                old = False  # missing/unparseable ts → conservatively KEEP
            if old:
                dropped += 1
            else:
                kept.append(line)
        present = [line for line in current.splitlines() if line.strip()]
        if dropped == 0 and len(kept) == len(present):
            return  # nothing to drop → no rewrite, no inode churn
        tmp = registry.with_name(registry.name + ".tmp.%d" % os.getpid())
        try:
            with tmp.open("w", encoding="utf-8") as out:
                for line in kept:
                    out.write(line + "\n")
                out.flush()
                os.fsync(out.fileno())
            # Renames the REGISTRY only. The LOCK file is NEVER unlinked, recreated or
            # renamed — unlink+recreate would let two holders each believe they hold
            # exclusivity on different inodes.
            os.replace(str(tmp), str(registry))
        except Exception:
            try:
                tmp.unlink()
            except Exception:
                pass


prune()
if clause:
    sys.stdout.write(clause + "\n")
PY
  )
fi
# ── end U-HK-44 sweep ─────────────────────────────────────────────────────────

[ -z "$CANDS" ] && [ -z "$MEMFLAG" ] && [ -z "$UNREC" ] && exit 0

MSG="[hygiene]"
if [ -n "$CANDS" ]; then
  N=$(printf '%s\n' "$CANDS" | grep -c .)
  LIST=$(printf '%s\n' "$CANDS" | paste -sd'; ' -)
  # Branch refs are presented as a comma-separated DATA list, never an executable
  # `git branch -d ...` string — a ref name can contain shell metacharacters (codex P2).
  BRANCHES=$(printf '%s\n' "$CANDS" | sed -E 's/.*\(([^)]+)\)$/\1/' | paste -sd', ' -)
  MSG="$MSG ${N} stale merged worktree(s) — the explicit post-merge closeout reaps them, or remove manually: ${LIST}. Their merged branch refs (prune each with git branch -d; listed as data): ${BRANCHES}."
fi
[ -n "$MEMFLAG" ] && MSG="$MSG ${MEMFLAG}"
[ -n "$UNREC" ] && MSG="$MSG ${UNREC}"

hook_emit SessionStart "$MSG"

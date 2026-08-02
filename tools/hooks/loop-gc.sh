#!/usr/bin/env bash
# SessionStart worktree hygiene visibility (U-HK-26).
#
# The autonomous loop ships PRs whose worktrees go stale after merge; nothing reaps
# them (git-arc-guard checks commits/branches and session-end-cleanup is advisory-only).
# SessionStart is a latency-sensitive lease/context boundary, so this hook only reports
# candidates. The controller performs explicit reaping after merge/closeout.
#
#   ALL MODES → VISIBILITY: inject advisory additionalContext listing stale-worktree
#               candidates + their branch refs + a MEMORY.md over-cap flag. Never delete.
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

[ -z "$CANDS" ] && [ -z "$MEMFLAG" ] && exit 0

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

hook_emit SessionStart "$MSG"

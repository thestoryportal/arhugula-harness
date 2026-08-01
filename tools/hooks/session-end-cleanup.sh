#!/usr/bin/env bash
# SessionEnd cleanup (U-HK-09). Side-effect-only (SessionEnd output is ignored by
# Claude Code). Safe maintenance:
#   1. Prune old local pre-compaction checkpoints, keeping the most recent 10.
#   2. Write an ADVISORY git-hygiene report (merged branches, worktrees, MEMORY.md
#      cap) — does NOT auto-delete branches/worktrees. Destructive ops stay explicit
#      per the guardrailed-autonomy posture; the report just surfaces candidates.
# Merged-branch detection cross-refs local branches against gh merged-PR head refs
# (squash-merge-safe; plain `--is-ancestor` misses squash merges).
#
# Trigger: SessionEnd, matcher "*".

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"
hook_review_isolated && exit 0

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

CKDIR=".harness/.checkpoints"
mkdir -p "$CKDIR" 2>/dev/null || true

# 1) Prune timestamped precompact snapshots, keep the 10 newest (lexical = chrono).
#    session-specific precompact-latest-*.md pointers do not match precompact-2*.
ls -1 "$CKDIR"/precompact-2*.md 2>/dev/null | sort -r | tail -n +11 | while IFS= read -r f; do
  rm -f "$f" 2>/dev/null || true
done

# 2) Advisory hygiene report (non-destructive).
DEFAULT_BRANCH=$(hook_default_branch)
MERGED=$(hook_bounded 6 gh pr list --state merged --limit 60 --json headRefName --jq '.[].headRefName' 2>/dev/null)
REPORT="$CKDIR/session-end-report.md"
{
  echo "# Session-end hygiene report ($(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null))"
  echo
  echo "## Merged local branches (deletion candidates — NOT auto-deleted)"
  git for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null | while IFS= read -r b; do
    [ "$b" = "$DEFAULT_BRANCH" ] && continue
    if printf '%s\n' "$MERGED" | grep -qxF "$b"; then echo "- $b"; fi
  done
  echo
  echo "## Worktrees"
  git worktree list 2>/dev/null | sed 's/^/- /'
  echo
  echo "## MEMORY.md cap"
  MEM="$HOME/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/MEMORY.md"
  if [ -f "$MEM" ]; then
    SZ=$(wc -c < "$MEM" | tr -d ' ')
    if [ "${SZ:-0}" -gt 24400 ] 2>/dev/null; then echo "- size=${SZ}B / cap=24400B — OVER CAP, compact"; else echo "- size=${SZ}B / cap=24400B — ok"; fi
  else
    echo "- (MEMORY.md not found at expected path)"
  fi
} > "$REPORT" 2>/dev/null || true

exit 0

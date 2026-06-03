#!/usr/bin/env bash
# Autonomous git-workflow guard (U-HK-16) — ADVISORY. Stop matcher "*".
#
# Reminds (never auto-drives) about git-arc completeness so no work is left orphaned:
# the workspace arc is branch → commit → push → PR → CI-green → merge → fixed-point
# refresh (CLAUDE.md §12.2). At turn end this flags the common drop-points:
#   - uncommitted changes on a feature branch (work not saved),
#   - committed-but-unpushed commits (PR can't see them),
#   - local default branch BEHIND origin (stale-main drift — the §12.1 hazard).
#
# It is purely informational: it prints a `systemMessage` (visible reminder) and exits
# 0. It NEVER emits `decision:block` and NEVER auto-approves anything — so it is not an
# autonomy/auto-continue mechanism, just a hygiene mirror. Bounded git calls.
#
# Trigger: Stop "*". Test: tools/hooks/test_git_arc_guard.sh.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0   # not a git repo → nothing to say

PAYLOAD=$(hook_read_stdin)
# Don't re-flag inside a stop-hook continuation (parity with the other Stop hooks).
[ "$(hook_json "$PAYLOAD" '.stop_hook_active')" = "true" ] && exit 0

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
DEFAULT=$(hook_default_branch)
declare -a NOTES=()

# 1) Uncommitted tracked changes (a dirty tree at turn end = unsaved work).
if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
  NOTES+=("uncommitted changes present on '${BRANCH}' — commit before the arc closes")
fi

# 2) Committed-but-unpushed: only meaningful when an upstream is configured.
if UPSTREAM=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null); then
  AHEAD=$(git rev-list --count "${UPSTREAM}..HEAD" 2>/dev/null || echo 0)
  [ "${AHEAD:-0}" -gt 0 ] 2>/dev/null && NOTES+=("${AHEAD} commit(s) on '${BRANCH}' not pushed to ${UPSTREAM}")
fi

# 3) Local default branch behind origin (stale-main drift). Uses a no-network read of
#    the already-fetched remote ref; if origin/<default> is unknown, stay silent.
if git rev-parse --verify --quiet "origin/${DEFAULT}" >/dev/null 2>&1; then
  BEHIND=$(git rev-list --count "${DEFAULT}..origin/${DEFAULT}" 2>/dev/null || echo 0)
  [ "${BEHIND:-0}" -gt 0 ] 2>/dev/null && NOTES+=("local '${DEFAULT}' is ${BEHIND} commit(s) behind origin/${DEFAULT} — fetch/rebase before new work (§12.1 stale-main hazard)")
fi

[ "${#NOTES[@]}" -eq 0 ] && exit 0   # arc clean → silent

MSG="[git-arc-guard] arc hygiene:"
for n in "${NOTES[@]}"; do MSG="${MSG}
  • ${n}"; done

jq -nc --arg m "$MSG" '{"systemMessage":$m}'
exit 0

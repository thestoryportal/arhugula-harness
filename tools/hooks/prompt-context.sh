#!/usr/bin/env bash
# UserPromptSubmit context injector (U-HK-08). Injects a compact roadmap orientation
# (next-action + a cheap drift flag) into every prompt so context persists within a
# long running session — SessionStart fires only once at open, but state drifts as
# PRs land. Fast + NON-BLOCKING + NO NETWORK (UserPromptSubmit has a 30s budget and
# fires on every prompt, so the full audit / gh calls stay in session-start). Drift
# detection here is a local-only proxy (roadmap_status.md's git_head vs local HEAD);
# the real §12.1 audit (with open-PR/fork inputs) remains the SessionStart hook's job.
#
# Trigger: UserPromptSubmit (no matcher — fires on all prompts).

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"
hook_review_isolated && exit 0

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

ROADMAP_STATUS=".harness/roadmap_status.md"
[ -f "$ROADMAP_STATUS" ] || exit 0

NEXT=$(hook_roadmap_next "$ROADMAP_STATUS")

# Cheap local drift proxy (no network): roadmap_status.md's pinned git_head vs local
# HEAD. ONLY meaningful on the default branch — roadmap_status.md pins main's
# git_head, so on any feature/worktree branch local HEAD legitimately differs and
# the proxy would false-positive on every prompt. Mirror session-start.sh: skip the
# drift check off the default branch (next-action still injects). The real §12.1
# audit covers main.
CUR_BRANCH=$(git symbolic-ref --quiet --short HEAD 2>/dev/null)
DEF_BRANCH=$(hook_default_branch)
STORED_HEAD=$(grep -E '\| *`git_head`' "$ROADMAP_STATUS" 2>/dev/null | head -1 | grep -oE '[a-f0-9]{8}' | head -1)
LHEAD=$(git rev-parse HEAD 2>/dev/null | head -c 8)
DFLAG=""
if [ "$CUR_BRANCH" = "$DEF_BRANCH" ] && [ -n "$STORED_HEAD" ] && [ -n "$LHEAD" ] && [ "$STORED_HEAD" != "$LHEAD" ]; then
  # A terminating refresh commit makes a one-ahead local HEAD expected (§12.2.1) — not
  # drift. §12.2.1 requires BOTH (a) the reserved title prefix AND (b) a
  # roadmap-status-only changed-file set (EXACTLY roadmap_status.md — see
  # hook_is_roadmap_status_only_set). Keying on the title alone (as before) would let
  # a substantive commit mis-titled with the reserved prefix silently suppress a real
  # drift warning — the exact false-negative post-merge-refresh.sh guards against.
  LAST=$(git log -1 --format=%s 2>/dev/null)
  EXEMPT=""
  if echo "$LAST" | grep -qE '^ops: roadmap status refresh '; then
    CHANGED_FILES=$(git show --name-only --pretty=format: HEAD 2>/dev/null | grep -v '^$' | sort -u)
    hook_is_roadmap_status_only_set "$CHANGED_FILES" && EXEMPT="1"
  fi
  [ -z "$EXEMPT" ] \
    && DFLAG=" [possible drift: local HEAD ${LHEAD} != roadmap ${STORED_HEAD}; run the §12.1 audit]"
fi

hook_emit "UserPromptSubmit" "[roadmap] next=${NEXT:-?}${DFLAG}"

#!/usr/bin/env bash
# UserPromptSubmit context injector (U-HK-08). Injects a compact roadmap orientation
# (next-action + a cheap drift flag) into every prompt so context persists within a
# long running session — SessionStart fires only once at open, but state drifts as
# PRs land. Fast + NON-BLOCKING + NO NETWORK (UserPromptSubmit has a 30s budget and
# fires on every prompt, so the full audit / gh calls stay in session-start). Drift
# detection here is a local-only proxy (dashboard git_head vs local HEAD); the real
# §12.1 audit (with open-PR/fork inputs) remains the SessionStart hook's job.
#
# Trigger: UserPromptSubmit (no matcher — fires on all prompts).

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

DASH=".harness/roadmap_status.md"
[ -f "$DASH" ] || exit 0

NEXT=$(hook_roadmap_next "$DASH")

# Cheap local drift proxy (no network): dashboard's pinned git_head vs local HEAD.
DHEAD=$(grep -E '\| *`git_head`' "$DASH" 2>/dev/null | head -1 | grep -oE '[a-f0-9]{8}' | head -1)
LHEAD=$(git rev-parse HEAD 2>/dev/null | head -c 8)
DFLAG=""
if [ -n "$DHEAD" ] && [ -n "$LHEAD" ] && [ "$DHEAD" != "$LHEAD" ]; then
  # A terminating refresh commit makes a one-ahead local HEAD expected (§12.2.1) — not
  # drift. §12.2.1 requires BOTH (a) the reserved title prefix AND (b) the ONLY changed
  # file is the dashboard. Keying on the title alone (as before) would let a substantive
  # commit mis-titled with the reserved prefix silently suppress a real drift warning —
  # the exact false-negative post-merge-refresh.sh guards against. Require both here too.
  LAST=$(git log -1 --format=%s 2>/dev/null)
  EXEMPT=""
  if echo "$LAST" | grep -qE '^ops: roadmap status refresh '; then
    CHANGED_FILES=$(git show --name-only --pretty=format: HEAD 2>/dev/null | grep -v '^$' | sort -u)
    [ "$CHANGED_FILES" = ".harness/roadmap_status.md" ] && EXEMPT="1"
  fi
  [ -z "$EXEMPT" ] \
    && DFLAG=" [possible drift: local HEAD ${LHEAD} != dashboard ${DHEAD}; run the §12.1 audit]"
fi

hook_emit "UserPromptSubmit" "[roadmap] next=${NEXT:-?}${DFLAG}"

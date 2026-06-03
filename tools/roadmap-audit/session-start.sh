#!/usr/bin/env bash
# Roadmap session-start audit — fires at every Claude Code session open.
# Implements CLAUDE.md §12.1 audit + §12.2.1 fixed-point carve-out.
# Emits JSON with additionalContext per Claude Code SessionStart hook protocol.
#
# Token budget: match=~17 tokens, lag=~25 tokens, drift=~35 tokens.
# Total preamble overhead at session start: under 50 tokens worst case.
#
# Always exit 0; encode any failure in additionalContext to avoid silent skip.
# Shared conventions (emit shape, hash recipe, bounded fetch, default branch) live
# in tools/hooks/lib.sh — sourced below. Tested by tools/roadmap-audit/test_session_start.sh.

set -uo pipefail

# Source the shared hook library; if missing, no-op rather than crash a session.
_LIB="$(dirname "${BASH_SOURCE[0]}")/../hooks/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=../hooks/lib.sh
. "$_LIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

DASHBOARD=".harness/roadmap_status.md"
ROADMAP="Project_Roadmap_v1.md"

# Single-line additionalContext for the SessionStart event (wraps the lib helper).
emit() { hook_emit "SessionStart" "$1"; }

[ -f "$DASHBOARD" ] || emit "[ROADMAP] absent — see Project_Roadmap_v1.md §7"
[ -f "$ROADMAP" ] || emit "[ROADMAP] dashboard exists but roadmap absent"

# Compute current workspace_state_hash per CLAUDE.md §12.1 step 2 recipe.
HEAD=$(git rev-parse HEAD 2>/dev/null | head -c 8)
PRS=$(gh pr list --state open --json number,headRefName --jq '. | sort_by(.number) | map("\(.number):\(.headRefName)") | join(",")' 2>/dev/null || echo "")
FORKS=$(ls .harness/class_1_fork_*.md .harness/class_2_fork_*.md 2>/dev/null | wc -l | tr -d ' ')
BATCH=$(ls .harness/phase-7d-retirement-events-batch-*.md 2>/dev/null | sort -V | tail -1)
COMPUTED=$(hook_state_hash "$HEAD" "$PRS" "$FORKS" "$BATCH")

# Extract stored hash + next_action from dashboard.
DASHBOARD_HASH=$(grep '`workspace_state_hash`' "$DASHBOARD" 2>/dev/null | head -1 | grep -oE '[a-f0-9]{12}' | head -1)
NEXT=$(hook_roadmap_next "$DASHBOARD")

PR_COUNT=$([ -z "$PRS" ] && echo 0 || echo "$PRS" | tr ',' '\n' | grep -c .)

# Recurrence guard (CLAUDE.md §12.3 / dashboard drift-log line-92 precedent): when on the
# default branch, detect a local checkout trailing origin. The base hook reads only the LOCAL
# dashboard + HEAD, so a checkout behind origin yields a globally-stale next-action that still
# looks locally-consistent (the Cluster A/B drift, 2026-05-31). Only fires on the default branch
# so feature-branch worktrees that intentionally trail main get no noise. Best-effort fetch is
# bounded (and a no-op offline) so the hook can never hang — it falls back to the existing origin
# ref, which sibling worktrees/jobs keep fresh.
DEFAULT_BRANCH=$(hook_default_branch)
CURRENT_BRANCH=$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo "")
if [ "$CURRENT_BRANCH" = "$DEFAULT_BRANCH" ]; then
  hook_bounded 4 git fetch --quiet --no-tags origin "$DEFAULT_BRANCH" >/dev/null 2>&1 || true
  BEHIND=$(git rev-list --count "HEAD..origin/${DEFAULT_BRANCH}" 2>/dev/null || echo 0)
  if [ "${BEHIND:-0}" -gt 0 ] 2>/dev/null; then
    emit "[ROADMAP] behind-origin=${BEHIND} on ${DEFAULT_BRANCH} — fast-forward (git merge --ff-only origin/${DEFAULT_BRANCH}) before deriving next-action; dashboard next=${NEXT:-?} may be stale (§12.3 / line-92 precedent)."
  fi
fi

if [ "$COMPUTED" = "$DASHBOARD_HASH" ]; then
  emit "[ROADMAP] hash=ok next=${NEXT:-?} in_flight=${PR_COUNT} forks=${FORKS}"
fi

# Hash mismatch — check §12.2.1 fixed-point carve-out.
# The carve-out keys on the commit-title PREFIX "ops: roadmap status refresh",
# format-agnostic on the post-NNN suffix — refreshes have been titled both
# `post-PR-NNN` (early) and `post-#NNN` / `post-#NNN/#NNN` / `post-#NNN (...)`
# (later). Matching the prefix (not a specific NNN format) keeps the lag-expected
# fixed point robust to either convention so a one-commit-behind dashboard after
# any refresh is never mis-flagged as drift.
LAST_TITLE=$(git log -1 --format=%s 2>/dev/null)
if echo "$LAST_TITLE" | grep -qE '^ops: roadmap status refresh '; then
  emit "[ROADMAP] hash=lag-expected next=${NEXT:-?} (post-refresh fixed-point §12.2.1)"
fi

# Genuine drift — surface for §12.3 halt-and-reconcile.
emit "[ROADMAP DRIFT] dashboard=${DASHBOARD_HASH:-none} computed=${COMPUTED} next=${NEXT:-?} action=§12.3"

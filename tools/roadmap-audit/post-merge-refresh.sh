#!/usr/bin/env bash
# Roadmap post-merge refresh reminder — fires after a `gh pr merge` Bash call.
# Implements the §12.2 post-PR-merge audit toil as an ADVISORY reminder:
# it does NOT edit the dashboard (that needs judgment about recently_completed /
# next_action). It detects "a substantive PR just merged → a terminating refresh
# is owed", PRE-COMPUTES the new workspace_state_hash, and injects a checklist so
# the mechanical hash-by-hand step is gone.
#
# Trigger: PostToolUse, matcher "Bash". The matcher fires on EVERY Bash call, so
# this script early-exits unless the command contained `gh pr merge`.
#
# Noise discipline (the criterion that keeps advisory hooks alive): emit ONLY when
# origin/<default> actually advanced past the dashboard's pinned git_head to a
# commit whose title does NOT begin with `ops: roadmap status refresh `. That
# single condition covers (a) failed merges — origin didn't advance, and
# (b) refresh-PR merges — already a refresh, no follow-on owed. See CLAUDE.md
# §12.2 + §12.2.1.
#
# Always exit 0; encode any failure as silence to avoid blocking the tool flow.

set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

DASHBOARD=".harness/roadmap_status.md"
[ -f "$DASHBOARD" ] || exit 0

# --- Read the tool command from PostToolUse stdin JSON. -----------------------
# PostToolUse delivers {"tool_name":"Bash","tool_input":{"command":"..."},...}.
PAYLOAD=$(cat 2>/dev/null || echo "")
CMD=$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.command // empty' 2>/dev/null || echo "")

# Early-exit unless this Bash call was a PR merge.
printf '%s' "$CMD" | grep -qE 'gh +pr +merge' || exit 0

emit() {
  # PostToolUse additionalContext injection (mirrors the SessionStart hook shape).
  jq -nc --arg ctx "$1" \
    '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":$ctx}}'
  exit 0
}

# --- Determine the default branch + best-effort fetch (timeout-guarded). -------
DEFAULT_BRANCH=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
[ -z "$DEFAULT_BRANCH" ] && DEFAULT_BRANCH=main

# Portable bounded runner: kill a child that outlives SECS. Used so the post-merge
# fetch can NEVER hang the PostToolUse turn — even on a stock macOS that ships
# neither `timeout` nor `gtimeout`. (PostToolUse runs after the tool; an unbounded
# git hang would otherwise hold the turn up to Claude Code's hook timeout.)
_bounded() { # _bounded SECS cmd...
  local secs="$1"; shift
  "$@" & local p=$!
  ( sleep "$secs"; kill -0 "$p" 2>/dev/null && kill "$p" 2>/dev/null ) >/dev/null 2>&1 & local w=$!
  wait "$p" 2>/dev/null; local rc=$?
  kill "$w" 2>/dev/null; wait "$w" 2>/dev/null
  return "$rc"
}

# Fetch ALWAYS (origin doesn't advance locally on `gh pr merge`; skipping it makes
# the hook inert), but ALWAYS bounded (prefer GNU timeout; else the pure-bash
# watchdog) so it can't hang the turn.
TIMEOUT_BIN=""
command -v timeout  >/dev/null 2>&1 && TIMEOUT_BIN="timeout 6"
command -v gtimeout >/dev/null 2>&1 && TIMEOUT_BIN="gtimeout 6"
if [ -n "$TIMEOUT_BIN" ]; then
  $TIMEOUT_BIN git fetch --quiet --no-tags origin "$DEFAULT_BRANCH" >/dev/null 2>&1 || true
else
  _bounded 6 git fetch --quiet --no-tags origin "$DEFAULT_BRANCH" >/dev/null 2>&1 || true
fi

# --- Did origin actually advance past the dashboard's pinned head? -------------
# `gh pr merge` advances the REMOTE; the local checkout lags until pulled, so we
# read origin/<default>, not local HEAD. POST_MERGE_REFRESH_REF overrides the
# compared ref for unit tests only (default: origin/<default>).
COMPARE_REF="${POST_MERGE_REFRESH_REF:-origin/${DEFAULT_BRANCH}}"
ORIGIN_HEAD=$(git rev-parse "$COMPARE_REF" 2>/dev/null | head -c 8)
[ -z "$ORIGIN_HEAD" ] && exit 0

# Dashboard's pinned git_head (first 8 hex after `git_head` cell).
DASHBOARD_HEAD=$(grep -E '\| *`git_head`' "$DASHBOARD" 2>/dev/null | head -1 | grep -oE '[a-f0-9]{8}' | head -1)
[ -z "$DASHBOARD_HEAD" ] && DASHBOARD_HEAD=$(grep -iE 'git_head' "$DASHBOARD" 2>/dev/null | head -1 | grep -oE '[a-f0-9]{8}' | head -1)

# No advance → failed/no-op merge → stay silent.
[ "$ORIGIN_HEAD" = "$DASHBOARD_HEAD" ] && exit 0

# The merged tip is itself a terminating refresh → no follow-on owed → stay silent.
# §12.2.1 defines a terminating refresh as BOTH (a) the title prefix AND (b) the
# ONLY changed file is the dashboard. Checking the title alone would wrongly
# suppress the owed reminder for a substantive PR mis-titled with the reserved
# prefix (or a merge whose tip is a refresh over substantive commits). Require both.
ORIGIN_TITLE=$(git log -1 --format=%s "$COMPARE_REF" 2>/dev/null)
if printf '%s' "$ORIGIN_TITLE" | grep -qE '^ops: roadmap status refresh '; then
  CHANGED=$(git show --name-only --pretty=format: "$COMPARE_REF" 2>/dev/null | grep -v '^$' | sort -u)
  if [ "$CHANGED" = ".harness/roadmap_status.md" ]; then
    exit 0   # genuine dashboard-only terminating refresh → no follow-on owed
  fi
fi

# --- Substantive merge confirmed: pre-compute the new anchor + remind. ---------
# Hash recipe per CLAUDE.md §12.1 step 2, computed against origin/<default> so the
# value is correct before the local checkout is fast-forwarded.
PRS=$(gh pr list --state open --json number,headRefName \
        --jq '. | sort_by(.number) | map("\(.number):\(.headRefName)") | join(",")' 2>/dev/null || echo "")
# Read FORKS + BATCH from the MERGED ref, not the pre-merge local working tree.
# `gh pr merge` advances the remote but not the local checkout, so reading these
# inputs via `ls` would pair pre-merge fork/batch state with the post-merge
# ORIGIN_HEAD — yielding a hash that won't match the next SessionStart audit
# (which reads them post-fast-forward), producing a false drift report. The
# git-ls-tree path format (`.harness/<name>`) matches the SessionStart `ls` path
# format, so the two hashes agree when the trees agree.
FORKS=$(git ls-tree --name-only "$COMPARE_REF" .harness/ 2>/dev/null | grep -cE '/class_[12]_fork_.*\.md$')
BATCH=$(git ls-tree --name-only "$COMPARE_REF" .harness/ 2>/dev/null | grep -E '/phase-7d-retirement-events-batch-.*\.md$' | sort -V | tail -1)
COMPUTED=$(printf '%s|%s|%s|%s' "$ORIGIN_HEAD" "$PRS" "$FORKS" "$BATCH" | shasum -a 256 | head -c 12)

emit "[ROADMAP] substantive merge detected (origin/${DEFAULT_BRANCH} @ ${ORIGIN_HEAD}: \"${ORIGIN_TITLE}\"). A terminating refresh is owed per §12.2 (Hook A will NOT catch its own merge). Steps: (1) git -C \"$PROJECT_DIR\" fetch && git merge --ff-only origin/${DEFAULT_BRANCH}; (2) update ${DASHBOARD}: workspace_state_hash=${COMPUTED}, git_head=${ORIGIN_HEAD}, last_refreshed=now, prepend recently_completed, re-derive next_action; (3) commit title prefix 'ops: roadmap status refresh ' (dashboard-only → §12.2.1 fixed point, no recursion)."

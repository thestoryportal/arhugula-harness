#!/usr/bin/env bash
# Roadmap post-merge refresh reminder — fires after a `gh pr merge` Bash call.
# Implements the §12.2 post-PR-merge audit toil as an ADVISORY reminder:
# it does NOT edit roadmap_status.md (that needs judgment about recently_completed /
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
# Shared conventions (emit, stdin parse, bounded fetch, default branch, hash recipe)
# live in tools/hooks/lib.sh — sourced below. Tested by test_post_merge_refresh.sh.

set -uo pipefail

# Source the shared hook library; if missing, no-op rather than block the tool flow.
_LIB="$(dirname "${BASH_SOURCE[0]}")/../hooks/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=../hooks/lib.sh
. "$_LIB"
hook_review_isolated && exit 0

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

ROADMAP_STATUS=".harness/roadmap_status.md"
[ -f "$ROADMAP_STATUS" ] || exit 0

# --- Read the tool command from PostToolUse stdin JSON. -----------------------
# PostToolUse delivers {"tool_name":"Bash","tool_input":{"command":"..."},...}.
PAYLOAD=$(hook_read_stdin)
CMD=$(hook_json "$PAYLOAD" '.tool_input.command')

# Early-exit unless this Bash call was a PR merge.
printf '%s' "$CMD" | grep -qE 'gh +pr +merge' || exit 0

# Single-line additionalContext for the PostToolUse event (wraps the lib helper).
emit() { hook_emit "PostToolUse" "$1"; }

# --- Determine the default branch + best-effort fetch (bounded). ---------------
DEFAULT_BRANCH=$(hook_default_branch)

# Fetch ALWAYS (origin doesn't advance locally on `gh pr merge`; skipping it makes
# the hook inert), but ALWAYS bounded so it can't hang the PostToolUse turn — even
# on a stock macOS without GNU timeout (hook_bounded falls back to a pure-bash
# watchdog).
hook_bounded 6 git fetch --quiet --no-tags origin "$DEFAULT_BRANCH" >/dev/null 2>&1 || true

# --- Did origin actually advance past the dashboard's pinned head? -------------
# `gh pr merge` advances the REMOTE; the local checkout lags until pulled, so we
# read origin/<default>, not local HEAD. POST_MERGE_REFRESH_REF overrides the
# compared ref for unit tests only (default: origin/<default>).
COMPARE_REF="${POST_MERGE_REFRESH_REF:-origin/${DEFAULT_BRANCH}}"
ORIGIN_HEAD=$(git rev-parse "$COMPARE_REF" 2>/dev/null | head -c 8)
[ -z "$ORIGIN_HEAD" ] && exit 0

# roadmap_status.md's pinned git_head (first 8 hex after `git_head` cell).
STORED_HEAD=$(grep -E '\| *`git_head`' "$ROADMAP_STATUS" 2>/dev/null | head -1 | grep -oE '[a-f0-9]{8}' | head -1)
[ -z "$STORED_HEAD" ] && STORED_HEAD=$(grep -iE 'git_head' "$ROADMAP_STATUS" 2>/dev/null | head -1 | grep -oE '[a-f0-9]{8}' | head -1)

# No advance → failed/no-op merge → stay silent.
[ "$ORIGIN_HEAD" = "$STORED_HEAD" ] && exit 0

# The merged tip is itself a terminating refresh → no follow-on owed → stay silent.
# §12.2.1 defines a terminating refresh as BOTH (a) the title prefix AND (b) a
# roadmap-status-only changed-file set (EXACTLY roadmap_status.md — see
# hook_is_roadmap_status_only_set). Misclassifying a genuine refresh as substantive
# here is the worst case: it would emit "refresh owed" for a refresh → spawn another
# refresh → the §12.2.1 recursion the fixed point exists to STOP. Checking the title
# alone would symmetrically wrongly suppress the owed reminder for a substantive PR
# mis-titled with the reserved prefix (or a merge whose tip is a refresh over
# substantive commits). Require both.
ORIGIN_TITLE=$(git log -1 --format=%s "$COMPARE_REF" 2>/dev/null)
if printf '%s' "$ORIGIN_TITLE" | grep -qE '^ops: roadmap status refresh '; then
  CHANGED=$(git show --name-only --pretty=format: "$COMPARE_REF" 2>/dev/null | grep -v '^$' | sort -u)
  if hook_is_roadmap_status_only_set "$CHANGED"; then
    exit 0   # genuine roadmap-status-only terminating refresh → no follow-on owed
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
COMPUTED=$(hook_state_hash "$ORIGIN_HEAD" "$PRS" "$FORKS" "$BATCH")

emit "[ROADMAP] substantive merge detected (origin/${DEFAULT_BRANCH} @ ${ORIGIN_HEAD}: \"${ORIGIN_TITLE}\"). A terminating refresh is owed per §12.2 (Hook A will NOT catch its own merge). Steps: (1) git -C \"$PROJECT_DIR\" fetch && git merge --ff-only origin/${DEFAULT_BRANCH}; (2) update ${ROADMAP_STATUS}: workspace_state_hash=${COMPUTED}, git_head=${ORIGIN_HEAD}, last_refreshed=now, prepend recently_completed, re-derive next_action; (3) commit title prefix 'ops: roadmap status refresh ' (roadmap-status-only → §12.2.1 fixed point, no recursion)."

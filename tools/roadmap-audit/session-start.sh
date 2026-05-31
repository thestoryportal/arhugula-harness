#!/usr/bin/env bash
# Roadmap session-start audit — fires at every Claude Code session open.
# Implements CLAUDE.md §12.1 audit + §12.2.1 fixed-point carve-out.
# Emits JSON with additionalContext per Claude Code SessionStart hook protocol.
#
# Token budget: match=~17 tokens, lag=~25 tokens, drift=~35 tokens.
# Total preamble overhead at session start: under 50 tokens worst case.
#
# Always exit 0; encode any failure in additionalContext to avoid silent skip.

set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

DASHBOARD=".harness/roadmap_status.md"
ROADMAP="Project_Roadmap_v1.md"

emit() {
  # Single-line additionalContext via jq for safe JSON quoting.
  jq -nc --arg ctx "$1" '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":$ctx}}'
  exit 0
}

[ -f "$DASHBOARD" ] || emit "[ROADMAP] absent — see Project_Roadmap_v1.md §7"
[ -f "$ROADMAP" ] || emit "[ROADMAP] dashboard exists but roadmap absent"

# Compute current workspace_state_hash per CLAUDE.md §12.1 step 2 recipe.
HEAD=$(git rev-parse HEAD 2>/dev/null | head -c 8)
PRS=$(gh pr list --state open --json number,headRefName --jq '. | sort_by(.number) | map("\(.number):\(.headRefName)") | join(",")' 2>/dev/null || echo "")
FORKS=$(ls .harness/class_1_fork_*.md .harness/class_2_fork_*.md 2>/dev/null | wc -l | tr -d ' ')
BATCH=$(ls .harness/phase-7d-retirement-events-batch-*.md 2>/dev/null | sort -V | tail -1)
COMPUTED=$(printf '%s|%s|%s|%s' "$HEAD" "$PRS" "$FORKS" "$BATCH" | shasum -a 256 | head -c 12)

# Extract stored hash + next_action from dashboard.
DASHBOARD_HASH=$(grep '`workspace_state_hash`' "$DASHBOARD" 2>/dev/null | head -1 | grep -oE '[a-f0-9]{12}' | head -1)
NEXT=$(grep -oE '\*\*`R-[A-Za-z0-9-]+`\*\*' "$DASHBOARD" 2>/dev/null | head -1 | tr -d '`*')

PR_COUNT=$([ -z "$PRS" ] && echo 0 || echo "$PRS" | tr ',' '\n' | grep -c .)

if [ "$COMPUTED" = "$DASHBOARD_HASH" ]; then
  emit "[ROADMAP] hash=ok next=${NEXT:-?} in_flight=${PR_COUNT} forks=${FORKS}"
fi

# Hash mismatch — check §12.2.1 fixed-point carve-out.
LAST_TITLE=$(git log -1 --format=%s 2>/dev/null)
if echo "$LAST_TITLE" | grep -qE '^ops: roadmap status refresh post-PR-[0-9]+'; then
  emit "[ROADMAP] hash=lag-expected next=${NEXT:-?} (post-refresh fixed-point §12.2.1)"
fi

# Genuine drift — surface for §12.3 halt-and-reconcile.
emit "[ROADMAP DRIFT] dashboard=${DASHBOARD_HASH:-none} computed=${COMPUTED} next=${NEXT:-?} action=§12.3"

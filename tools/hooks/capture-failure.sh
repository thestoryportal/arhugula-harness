#!/usr/bin/env bash
# Failure + token-cap capture (U-HK-07). Logs tool failures (PostToolUseFailure) and
# API/turn errors (StopFailure: max_output_tokens, rate_limit, authentication_failed,
# ...) to a gitignored .harness/session-issues.jsonl for session learning (goal #3 +
# the report's #1 friction — output-token-cap truncation that obscured handoffs).
# When the same error signature recurs (cardinality >=2), nudges a memory entry.
#
# Trigger: wired at BOTH PostToolUseFailure and StopFailure. StopFailure output is
# ignored by Claude Code, so for it this hook only LOGS; the memory-candidate nudge
# is emitted only on PostToolUseFailure (where additionalContext is honored).

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0
mkdir -p .harness 2>/dev/null || exit 0
LOG=".harness/session-issues.jsonl"

PAYLOAD=$(hook_read_stdin)
EVENT=$(hook_json "$PAYLOAD" '.hook_event_name')
TOOL=$(hook_json "$PAYLOAD" '.tool_name')
ERRTYPE=$(hook_json "$PAYLOAD" '.error_type')
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")
SIG="${EVENT}:${TOOL}:${ERRTYPE}"   # recurrence key

ROW=$(jq -nc --arg ts "$TS" --arg ev "$EVENT" --arg tool "$TOOL" --arg et "$ERRTYPE" --arg sig "$SIG" \
  '{ts:$ts,event:$ev,tool:$tool,error_type:$et,sig:$sig}' 2>/dev/null) || exit 0
printf '%s\n' "$ROW" >> "$LOG" 2>/dev/null || exit 0

# Recurrence: count rows with this signature. >=2 (cardinality, per §12.5.1) → nudge.
COUNT=$(grep -cF "\"sig\":\"$SIG\"" "$LOG" 2>/dev/null || echo 0)
if [ "$EVENT" = "PostToolUseFailure" ] && [ "${COUNT:-0}" -ge 2 ]; then
  hook_emit "PostToolUseFailure" "[session-learning] recurring failure (${COUNT}x this session): ${SIG}. Per CLAUDE.md §12.5.1 (cardinality >=2) consider a memory entry or a fix — see .harness/session-issues.jsonl."
fi
exit 0

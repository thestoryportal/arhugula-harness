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
#
# U-CTX-07 (2026-08-10): the signature gained a 4th segment (exit code, or a command
# head when no exit code is available) so distinct failing commands sharing the same
# EVENT:TOOL:ERRTYPE no longer collide into one bucket. AND a PER-SESSION emission cap
# was added: the first TWO nudges of a session are always emitted; every qualifying
# nudge after that is capped/deduped (logged, never re-emitted) — a live session
# observed the un-capped hook re-emit the SAME nudge ~20x in one session, spamming
# additionalContext into nearly every turn. This is independent of the per-signature
# recurrence threshold (still >=2) — the cap bounds TOTAL nudges, not per-sig nudges.

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
SESSION=$(hook_json "$PAYLOAD" '.session_id')
[ -z "$SESSION" ] && SESSION="unknown"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")

# 4th signature segment: prefer the tool's exit code (when the tool surfaces one on
# tool_error); fall back to a truncated head of the failing Bash command. Either way
# this differentiates e.g. "Bash:command_failed" failures from `git status` vs
# `npm test` instead of collapsing them into one bucket.
EXITCODE=$(hook_json "$PAYLOAD" '.tool_error.exit_code')
if [ -n "$EXITCODE" ]; then
  EXIT_OR_CMDHEAD="$EXITCODE"
else
  CMDRAW=$(hook_json "$PAYLOAD" '.tool_input.command')
  EXIT_OR_CMDHEAD=$(printf '%s' "$CMDRAW" | cut -c1-40)
fi
SIG="${EVENT}:${TOOL}:${ERRTYPE}:${EXIT_OR_CMDHEAD}"   # recurrence key (semantic, for display)

# Recurrence: count PRIOR rows with this signature WITHIN THE CURRENT SESSION (i.e.
# before this occurrence is appended below). The log is a gitignored append-only file
# that persists across sessions in the same worktree, so an unscoped count would
# report the first repeat of an old failure as "2x this session" on a fresh open.
# Scoping on session_id keeps the "this session" claim true. >=2 (cardinality, per
# §12.5.1) → this occurrence would nudge, subject to the per-session emission cap below.
PRIOR_SIG_COUNT=$(grep -F "\"sig\":\"$SIG\"" "$LOG" 2>/dev/null | grep -cF "\"session\":\"$SESSION\"")
RECUR_COUNT=$((${PRIOR_SIG_COUNT:-0} + 1))
WOULD_NUDGE=false
[ "$EVENT" = "PostToolUseFailure" ] && [ "$RECUR_COUNT" -ge 2 ] && WOULD_NUDGE=true

# Per-session emission cap (U-CTX-07): only the first TWO nudges of a session are
# EVER emitted (additionalContext injected into a turn); every qualifying nudge after
# that is capped — logged to the jsonl as always, but never re-emitted. Bounds TOTAL
# nudges per session, independent of the per-signature recurrence threshold above.
EMIT_NOW=false
if [ "$WOULD_NUDGE" = true ]; then
  PRIOR_EMIT_COUNT=$(grep -F "\"session\":\"$SESSION\"" "$LOG" 2>/dev/null | grep -cF '"emitted":true')
  [ "${PRIOR_EMIT_COUNT:-0}" -lt 2 ] && EMIT_NOW=true
fi

ROW=$(jq -nc --arg ts "$TS" --arg ev "$EVENT" --arg tool "$TOOL" --arg et "$ERRTYPE" --arg sig "$SIG" --arg sess "$SESSION" --argjson emitted "$EMIT_NOW" \
  '{ts:$ts,event:$ev,tool:$tool,error_type:$et,sig:$sig,session:$sess,emitted:$emitted}' 2>/dev/null) || exit 0
printf '%s\n' "$ROW" >> "$LOG" 2>/dev/null || exit 0

if [ "$EMIT_NOW" = true ]; then
  hook_emit "PostToolUseFailure" "[session-learning] recurring failure (${RECUR_COUNT}x this session): ${SIG}. Per CLAUDE.md §12.5.1 (cardinality >=2) consider a memory entry or a fix — see .harness/session-issues.jsonl."
fi
exit 0

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
  # Flatten BEFORE truncating (codex P2): `cut -c1-40` alone keeps 40 chars of
  # EVERY line, so a heredoc/generated script produced an arbitrarily large
  # signature despite the cap. Newlines/tabs become spaces, then one global cut.
  EXIT_OR_CMDHEAD=$(printf '%s' "$CMDRAW" | tr '\n\t' '  ' | cut -c1-40)
fi
SIG="${EVENT}:${TOOL}:${ERRTYPE}:${EXIT_OR_CMDHEAD}"   # recurrence key (semantic, for display)

# --- Critical section: count + append must be atomic (codex P2 — overlapping
# failure hooks for parallel tool calls all read the same prior counts before any
# appends; a 12-way identical-failure probe emitted SIX rows past the 2-cap).
# mkdir is the portable atomic primitive (macOS ships no flock binary). On a
# crashed holder the lock goes stale: reclaim when older than 10s. If the lock
# cannot be acquired, the row is STILL LOGGED but emission is SUPPRESSED (codex
# round-2: a lockless fallback let 20 contenders emit 3-6 nudges — the cap
# decision must stay serialized, and losing one nudge is the safe direction).
# A hook never blocks or fails the tool flow either way.
# CAPTURE_FAILURE_LOCK_TRIES: test seam (default 50 × 0.1s ≈ 5s).
LOCKDIR="${LOG}.lock"
_LOCKED=false
for _try in $(seq 1 "${CAPTURE_FAILURE_LOCK_TRIES:-50}"); do
  if mkdir "$LOCKDIR" 2>/dev/null; then _LOCKED=true; break; fi
  # stale-lock reclaim (crashed holder): BSD stat first (macOS), GNU fallback (CI)
  _now=$(date +%s)
  _lockts=$(stat -f %m "$LOCKDIR" 2>/dev/null || stat -c %Y "$LOCKDIR" 2>/dev/null || echo "$_now")
  if [ $((_now - _lockts)) -gt 10 ]; then
    rmdir "$LOCKDIR" 2>/dev/null || true
    continue
  fi
  sleep 0.1
done

# Recurrence: count PRIOR rows with this signature WITHIN THE CURRENT SESSION (i.e.
# before this occurrence is appended below). The log is a gitignored append-only file
# that persists across sessions in the same worktree, so an unscoped count would
# report the first repeat of an old failure as "2x this session" on a fresh open.
# Scoping on session_id keeps the "this session" claim true. Counting PARSES each
# JSONL row (codex P2: a raw grep for "sig":"$SIG" missed every command containing
# JSON-escaped characters — e.g. quotes in `python -c "..."` — so quoted-command
# failures never reached the threshold); `fromjson?` skips torn/malformed lines.
# >=2 (cardinality, per §12.5.1) → this occurrence would nudge, subject to the
# per-session emission cap below.
PRIOR_SIG_COUNT=$(jq -Rr --arg sig "$SIG" --arg sess "$SESSION" \
  'fromjson? | select(.sig == $sig and .session == $sess) | 1' "$LOG" 2>/dev/null | grep -c . || true)
RECUR_COUNT=$((${PRIOR_SIG_COUNT:-0} + 1))
WOULD_NUDGE=false
[ "$EVENT" = "PostToolUseFailure" ] && [ "$RECUR_COUNT" -ge 2 ] && WOULD_NUDGE=true

# Per-session emission cap (U-CTX-07): only the first TWO nudges of a session are
# EVER emitted (additionalContext injected into a turn); every qualifying nudge after
# that is capped — logged to the jsonl as always, but never re-emitted. Bounds TOTAL
# nudges per session, independent of the per-signature recurrence threshold above.
EMIT_NOW=false
if [ "$WOULD_NUDGE" = true ] && [ "$_LOCKED" = true ]; then
  # Emission requires the lock: an unserialized cap decision is exactly the
  # overlapping-hooks spam this cap exists to stop (codex round-2). Unlocked
  # invocations log their row below but never emit.
  PRIOR_EMIT_COUNT=$(jq -Rr --arg sess "$SESSION" \
    'fromjson? | select(.session == $sess and .emitted == true) | 1' "$LOG" 2>/dev/null | grep -c . || true)
  [ "${PRIOR_EMIT_COUNT:-0}" -lt 2 ] && EMIT_NOW=true
fi

ROW=$(jq -nc --arg ts "$TS" --arg ev "$EVENT" --arg tool "$TOOL" --arg et "$ERRTYPE" --arg sig "$SIG" --arg sess "$SESSION" --argjson emitted "$EMIT_NOW" \
  '{ts:$ts,event:$ev,tool:$tool,error_type:$et,sig:$sig,session:$sess,emitted:$emitted}' 2>/dev/null) || { [ "$_LOCKED" = true ] && rmdir "$LOCKDIR" 2>/dev/null; exit 0; }
printf '%s\n' "$ROW" >> "$LOG" 2>/dev/null || { [ "$_LOCKED" = true ] && rmdir "$LOCKDIR" 2>/dev/null; exit 0; }
[ "$_LOCKED" = true ] && rmdir "$LOCKDIR" 2>/dev/null || true
# --- End critical section.

if [ "$EMIT_NOW" = true ]; then
  hook_emit "PostToolUseFailure" "[session-learning] recurring failure (${RECUR_COUNT}x this session): ${SIG}. Per CLAUDE.md §12.5.1 (cardinality >=2) consider a memory entry or a fix — see .harness/session-issues.jsonl."
fi
exit 0

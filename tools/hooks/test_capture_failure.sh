#!/usr/bin/env bash
# Hermetic test for capture-failure.sh (U-HK-07). Asserts logging + recurrence nudge.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/capture-failure.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
mkdir -p "$REPO/.harness"
LOG="$REPO/.harness/session-issues.jsonl"

run() { printf '%s' "$1" | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null; }

PTF='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"command_failed"}'
SF='{"hook_event_name":"StopFailure","error_type":"max_output_tokens"}'

# 1) first PostToolUseFailure → logged, no nudge yet (count=1).
OUT=$(run "$PTF")
[ "$(wc -l < "$LOG" | tr -d ' ')" = "1" ] && ok "first failure logged" || bad "not logged once"
[ -z "$OUT" ] && ok "no nudge on first occurrence" || bad "nudged too early: $OUT"

# 2) second identical failure → count=2 → nudge.
OUT=$(run "$PTF")
[ "$(wc -l < "$LOG" | tr -d ' ')" = "2" ] && ok "second failure logged" || bad "not logged twice"
printf '%s' "$OUT" | grep -q "recurring failure" && ok "nudges memory candidate at cardinality 2" || bad "no nudge at 2: $OUT"

# 3) StopFailure (token cap) → logged, no emit (output ignored by CC).
OUT=$(run "$SF")
grep -q "max_output_tokens" "$LOG" && ok "StopFailure token-cap logged" || bad "token-cap not logged"
[ -z "$OUT" ] && ok "StopFailure emits nothing (output ignored)" || bad "StopFailure emitted: $OUT"

# 4) rows are valid JSON.
while IFS= read -r line; do echo "$line" | jq -e . >/dev/null || { bad "invalid JSON row: $line"; break; }; done < "$LOG"
ok "all log rows valid JSON"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

#!/usr/bin/env bash
# Hermetic test for subagent-validate.sh (U-HK-17). Synthetic SubagentStart/Stop
# payloads + throwaway transcript JSONL files. Asserts: Start injects a contract;
# Stop blocks on an empty final turn, passes on a non-empty one (string + array
# content shapes), honors the stop_hook_active guard, and FAILS OPEN on missing
# transcript / unknown shape.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/subagent-validate.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

TMP="$(mktemp -d)"; { [ -n "$TMP" ] && [ -d "$TMP" ]; } || { echo "FATAL mktemp"; exit 1; }
trap 'rm -rf "$TMP"' EXIT

run() { printf '%s' "$1" | bash "$HOOK"; }
pl_stop() { jq -nc --arg t "$1" --argjson a "${2:-false}" \
  '{"hook_event_name":"SubagentStop","transcript_path":$t,"stop_hook_active":$a}'; }

# 1) SubagentStart → additionalContext contract.
OUT=$(run '{"hook_event_name":"SubagentStart"}')
echo "$OUT" | jq -e '.hookSpecificOutput.additionalContext | test("final message"; "i")' >/dev/null 2>&1 \
  && ok "SubagentStart injects contract" || bad "no contract: $OUT"

# 2) Non-empty final assistant turn (string content) → silent.
T="$TMP/good.jsonl"
{
  echo '{"message":{"role":"user","content":"do x"}}'
  echo '{"message":{"role":"assistant","content":"Here is the result: 42"}}'
} > "$T"
OUT=$(run "$(pl_stop "$T")")
[ -z "$OUT" ] && ok "non-empty string result → no block" || bad "blocked good result: $OUT"

# 3) Non-empty final assistant turn (array content) → silent.
T="$TMP/good_arr.jsonl"
echo '{"message":{"role":"assistant","content":[{"type":"text","text":"done: ok"}]}}' > "$T"
OUT=$(run "$(pl_stop "$T")")
[ -z "$OUT" ] && ok "non-empty array result → no block" || bad "blocked good array result: $OUT"

# 4) Empty final assistant turn (assistant turns exist) → block once.
T="$TMP/empty.jsonl"
{
  echo '{"message":{"role":"assistant","content":"thinking..."}}'
  echo '{"message":{"role":"assistant","content":"   "}}'
} > "$T"
OUT=$(run "$(pl_stop "$T")")
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "empty final turn → block" || bad "did not block empty: $OUT"

# 5) stop_hook_active guard → silent even on empty.
OUT=$(run "$(pl_stop "$T" true)")
[ -z "$OUT" ] && ok "stop_hook_active guard → no re-block" || bad "blocked despite active flag: $OUT"

# 6) Missing transcript path → fail open (silent).
OUT=$(run "$(pl_stop "$TMP/nope.jsonl")")
[ -z "$OUT" ] && ok "missing transcript → fail open" || bad "blocked on missing transcript: $OUT"

# 7) Unknown shape (no assistant turns at all) → fail open (silent).
T="$TMP/weird.jsonl"; echo '{"some":"other","schema":true}' > "$T"
OUT=$(run "$(pl_stop "$T")")
[ -z "$OUT" ] && ok "unknown shape → fail open" || bad "blocked on unknown shape: $OUT"

echo "----"
echo "subagent_validate: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

#!/usr/bin/env bash
# Hermetic test for prompt-lint.sh (U-HK-22). Asserts: bare deictic imperatives are
# flagged; everything with context, every workspace idiom, and every slash-command is
# silent (silent-when-well-formed AC).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/prompt-lint.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

run() { # $1 = prompt text
  printf '%s' "{\"hook_event_name\":\"UserPromptSubmit\",\"prompt\":$(jq -Rn --arg p "$1" '$p')}" \
    | bash "$HOOK" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null
}
flags()  { local o; o=$(run "$1"); printf '%s' "$o" | grep -q "prompt-lint" && ok "FLAG '$1'" || bad "expected flag, silent: '$1'"; }
silent() { local o; o=$(run "$1"); [ -z "$o" ] && ok "silent '$1'" || bad "unexpected flag '$1' -> $o"; }

# --- should FLAG (vague) ---
flags "fix it"
flags "Fix it."
flags "do this"
flags "make it better"
flags "it"
flags "change that"

# --- should be SILENT (well-formed / idiom / command) ---
silent "continue"
silent "continue to wave 3"
silent "ship it"
silent "go ahead"
silent "yes"
silent "fix the off-by-one in lib.sh hook_state_hash"
silent "do this: refactor the permission guard deny-list"
silent "/clear"
silent "/resolve this"
silent "make it better by extracting the shared watchdog"   # has trailing context
silent ""

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

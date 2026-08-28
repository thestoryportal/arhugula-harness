#!/usr/bin/env bash
# Hermetic test for agent-prompt-advisory.sh (U-SR-03, charter WR-08b).
#
# The four properties that matter, in the order they can fail:
#   1. it fires on an Agent PreToolUse payload, under the event name the runtime honors;
#   2. it can NEVER deny -- no decision-bearing key is ever emitted (a deny would break the
#      laws:prompt delegate the advisory asks for);
#   3. it fires on EVERY call, not the first -- a future per-session cap reds this test
#      rather than silently reintroducing the un-rehearsed passive memory WR-08 replaced;
#   4. it is actually WIRED at PreToolUse/"Agent" in settings.json -- a hook nothing routes
#      to is unreachable, and the script's own green says nothing about that.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/agent-prompt-advisory.sh"
REPO="$(cd "$SCRIPT_DIR/../.." && pwd)"
SETTINGS="$REPO/.claude/settings.json"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

run() { # $1 = tool_name
  printf '{"hook_event_name":"PreToolUse","tool_name":"%s","tool_input":{"prompt":"go"}}' "$1" \
    | bash "$HOOK"
}

# --- 1. fires on Agent, under the honored event name ---
OUT=$(run Agent)
printf '%s' "$OUT" | jq -e '.hookSpecificOutput.hookEventName == "PreToolUse"' >/dev/null 2>&1 \
  && ok "emits under hookEventName PreToolUse" || bad "wrong/absent hookEventName: $OUT"

CTX=$(printf '%s' "$OUT" | jq -r '.hookSpecificOutput.additionalContext // empty')
printf '%s' "$CTX" | grep -q 'agent-prompt-advisory' \
  && ok "Agent call is advised" || bad "no advisory on an Agent call: $OUT"
printf '%s' "$CTX" | grep -q 'laws:prompt' \
  && ok "advisory names the laws:prompt authoring route" || bad "advisory omits laws:prompt: $CTX"

# One advisory LINE (charter WR-08b), not a block: a multi-line nudge is the shape
# capture-failure.sh had to cap after it spammed ~20 turns (U-CTX-07).
[ "$(printf '%s' "$CTX" | wc -l | tr -d ' ')" = "0" ] \
  && ok "advisory is a single line" || bad "advisory spans multiple lines"

# --- 2. cannot deny: no decision-bearing key, ever ---
printf '%s' "$OUT" | jq -e '
  (.hookSpecificOutput | has("permissionDecision") | not)
  and (.hookSpecificOutput | has("permissionDecisionReason") | not)
  and (has("decision") | not)
' >/dev/null 2>&1 && ok "emits no decision-bearing key (advisory-only by construction)" \
                 || bad "a decision key is present -- this hook could deny: $OUT"

# --- 3. every call, not just the first ---
A=$(run Agent | jq -r '.hookSpecificOutput.additionalContext // empty')
B=$(run Agent | jq -r '.hookSpecificOutput.additionalContext // empty')
[ -n "$A" ] && [ "$A" = "$B" ] \
  && ok "advises on every Agent call (uncapped)" || bad "second Agent call was not advised"

# --- silence on anything that is not an Agent call ---
for tool in Bash Read Edit Write Task; do
  o=$(run "$tool")
  [ -z "$o" ] && ok "silent on $tool" || bad "advised a $tool call: $o"
done

# The payload is a surface the runtime owns, so the shapes it can hand over are inventoried
# rather than assumed: `tool_name` absent entirely, and no payload at all. Both must be
# silent-and-exit-0 -- an advisory that errors on an odd payload would surface as a hook
# failure on a tool call it has no business affecting.
for payload in '{"hook_event_name":"PreToolUse"}' '{}' ''; do
  o=$(printf '%s' "$payload" | bash "$HOOK"); rc=$?
  label=$([ -z "$payload" ] && echo "empty stdin" || echo "payload $payload")
  { [ -z "$o" ] && [ "$rc" -eq 0 ]; } \
    && ok "silent, exit 0 on $label" || bad "$label -> rc=$rc out=$o"
done

# --- 4. wired where the runtime will reach it ---
jq -e --arg c '${CLAUDE_PROJECT_DIR}/tools/hooks/agent-prompt-advisory.sh' '
  .hooks.PreToolUse
  | map(select(.matcher == "Agent"))
  | map(.hooks[].command) | index($c) != null
' "$SETTINGS" >/dev/null 2>&1 \
  && ok "wired at PreToolUse matcher Agent in settings.json" \
  || bad "settings.json does not route PreToolUse/Agent to this hook"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

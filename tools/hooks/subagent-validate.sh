#!/usr/bin/env bash
# Subagent self-validation (U-HK-17). SubagentStart (inject contract) + SubagentStop
# (validate output shape; block→retry once on malformed).
#
# SubagentStart: inject a short validation-contract reminder as additionalContext so
#   the subagent returns a usable result (non-empty; the final message IS the return
#   value). SubagentStart cannot block — advisory only.
# SubagentStop: read the subagent's final assistant message from the transcript and,
#   if it is empty/whitespace (a malformed/no-op result), `decision:block` ONCE so the
#   subagent retries. The stop_hook_active guard prevents an infinite retry loop.
#
# This is a QUALITY GATE on subagent output — it never auto-approves a tool call and
# never bypasses a permission prompt, so it is not an autonomy/auto-mode mechanism.
#
# Transcript-shape assumption (best-effort, FAIL-OPEN): the transcript at
# `transcript_path` is JSONL; the last line carrying an assistant text turn exposes it
# at `.message.content` (string) or `.message.content[].text` (array). If the path is
# absent/unreadable OR the shape doesn't match, the hook stays SILENT (exit 0) — it
# never blocks on its own uncertainty.
#
# Trigger: SubagentStart "*" + SubagentStop "*". Test: tools/hooks/test_subagent_validate.sh.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PAYLOAD=$(hook_read_stdin)
EVENT=$(hook_json "$PAYLOAD" '.hook_event_name')

if [ "$EVENT" = "SubagentStart" ]; then
  jq -nc '{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":"[subagent-validate] Return a concrete, non-empty result: your FINAL message is the value handed back to the caller (not shown to the user). State the conclusion/data directly — do not end with only a tool call or an empty turn."}}'
  exit 0
fi

# SubagentStop. Loop guard first.
[ "$(hook_json "$PAYLOAD" '.stop_hook_active')" = "true" ] && exit 0

# Prefer the direct final-message field if the runtime provides it (SubagentStop may expose
# `last_assistant_message`); else read the SUBAGENT transcript (`agent_transcript_path`),
# falling back to `transcript_path`. This avoids validating the parent session's transcript.
LASTMSG=$(hook_json "$PAYLOAD" '.last_assistant_message')
if [ -n "$LASTMSG" ]; then
  if [ -z "$(printf '%s' "$LASTMSG" | tr -d '[:space:]')" ]; then
    jq -nc '{"decision":"block","reason":"[subagent-validate] your final turn was empty — return a concrete non-empty result; your last message is the value handed to the caller."}'
  fi
  exit 0
fi

TRANSCRIPT=$(hook_json "$PAYLOAD" '.agent_transcript_path')
[ -z "$TRANSCRIPT" ] && TRANSCRIPT=$(hook_json "$PAYLOAD" '.transcript_path')
[ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ] && exit 0   # no transcript → fail-open

# Count assistant turns. None at all → unknown shape → fail open (silent).
ANY=$(jq -rs '[ .[] | select(type=="object" and (.message.role? == "assistant")) ] | length' "$TRANSCRIPT" 2>/dev/null || echo 0)
[ "${ANY:-0}" -gt 0 ] 2>/dev/null || exit 0

# Text of the LITERAL LAST assistant turn (the return value). Tolerate string + array
# content shapes. A turn that ends on whitespace or only a tool_use (no text) yields
# empty here — exactly the malformed "ended with only a tool call / empty turn" case.
LASTTEXT=$(jq -rs '
  [ .[] | select(type=="object" and (.message.role? == "assistant")) ] | last | .message.content
  | if type=="string" then .
    elif type=="array" then ([ .[] | select(.type?=="text") | .text ] | join(" "))
    else "" end
' "$TRANSCRIPT" 2>/dev/null || echo "")

if [ -z "$(printf '%s' "$LASTTEXT" | tr -d '[:space:]')" ]; then
  jq -nc '{"decision":"block","reason":"[subagent-validate] your final turn was empty (or only a tool call) — return a concrete non-empty result; your last message is the value handed to the caller."}'
fi
exit 0

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
# Lifecycle registry (U-HK-43). Every terminal decision point also appends ONE compact
# JSON row to `.harness/.agents-registry.jsonl` so a later sweep (U-HK-44) can report
# UNRECONCILED subagents. Honesty framing: Agent-tool subagents are API tasks, not OS
# processes — there is no pid and no `kill -0`, so this tracks lifecycle EVENTS only and
# reports "unreconciled", never "orphaned". Background-Bash pid fields in hook payloads
# are unverified; nothing here builds on them.
#
# Trigger: SubagentStart "*" + SubagentStop "*". Test: tools/hooks/test_subagent_validate.sh.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PAYLOAD=$(hook_read_stdin)
EVENT=$(hook_json "$PAYLOAD" '.hook_event_name')

# Append one lifecycle row: {ts, event, session, agent_id, transcript, cwd}.
#   start        — SubagentStart.
#   stop         — SubagentStop the gate ACCEPTED (terminal; reconciles a start).
#   stop_blocked — SubagentStop the gate BLOCKED (NONTERMINAL: the subagent retries, so
#                  the key stays unreconciled until an accepted result lands).
# `agent_id` is the correlation key (empty tolerated); the transcript fallback is
# PARENT-FIRST (`.transcript_path // .agent_transcript_path`) because SubagentStart
# payloads never carry `agent_transcript_path` (hooks-events reference) — child-first
# would record a start and its stop under UNMATCHABLE keys. Fan-out siblings sharing
# the parent path is expected: U-HK-44 counts per-key (starts − stops), never zeroing
# N starts on one stop. (The GATE's transcript read below stays child-first — that is
# about reading the right transcript, not about key identity.)
#
# The whole acquire→append→release runs inside ONE /usr/bin/python3 invocation that
# enforces its OWN ~2s deadline: this hook has no `hook_bounded` wrapper and the
# SubagentStart/Stop registrations carry no settings timeout, so the bound is
# self-imposed. The deadline governs lock ACQUISITION ONLY — once flock is held the
# retry loop is left and nothing can interrupt the write. Past the deadline the write is
# SKIPPED (never partial). Failure-invisible by construction: any failure (unwritable
# dir, missing python, contended lock) leaves the gate's behavior and output
# byte-identical and returns 0, adding at most ~2s before the gate's decision emission.
_registry_append() {
  local event="$1" dir agent session transcript
  dir=$(hook_project_dir)
  [ -n "$dir" ] || return 0
  agent=$(hook_json "$PAYLOAD" '.agent_id')
  session=$(hook_json "$PAYLOAD" '.session_id')
  transcript=$(hook_json "$PAYLOAD" '.transcript_path')
  [ -z "$transcript" ] && transcript=$(hook_json "$PAYLOAD" '.agent_transcript_path')
  # Payload data travels by argv — NEVER stdin (stdin already delivered the hook payload
  # to hook_read_stdin; the heredoc only carries the script, per lib.sh:157-189).
  /usr/bin/python3 - "$dir/.harness/.agents-registry.jsonl" "$event" "$session" "$agent" \
    "$transcript" "$PWD" <<'PY' >/dev/null 2>&1 || true
import fcntl
import json
import sys
import time
from pathlib import Path

registry = Path(sys.argv[1])
event, session, agent, transcript, cwd = sys.argv[2:7]
line = json.dumps(
    {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event,
        "session": session,
        "agent_id": agent,
        "transcript": transcript,
        "cwd": cwd,
    },
    separators=(",", ":"),
) + "\n"
# Bounded-line hygiene. Atomicity comes from the lock below, not from PIPE_BUF (which
# governs pipes, not O_APPEND files), so an over-long row is dropped rather than risked.
if len(line.encode("utf-8")) >= 4000:
    raise SystemExit(0)
registry.parent.mkdir(parents=True, exist_ok=True)
# Sibling advisory lock: .harness/.agents-registry.lock (U-HK-44's prune takes the SAME
# lock before its tmp-file + rename swap).
lock = registry.with_suffix(".lock")
deadline = time.monotonic() + 2.0
# Lock FIRST on the sibling .lock; the registry fd is opened for append only INSIDE the
# locked region and never carried across a rename (U-HK-44's prune swaps the inode).
with lock.open("a+") as stream:
    while True:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.monotonic() >= deadline:
                raise SystemExit(0)  # past deadline → skip the write entirely
            time.sleep(0.01)
    # Lock held. The deadline was acquisition-only and is now structurally inert: the
    # loop is left, no alarm/timer exists, so nothing can interrupt this write.
    with registry.open("a", encoding="utf-8") as out:
        out.write(line)
        out.flush()
PY
  return 0
}

if [ "$EVENT" = "SubagentStart" ]; then
  _registry_append start
  jq -nc '{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":"[subagent-validate] Return a concrete, non-empty result: your FINAL message is the value handed back to the caller (not shown to the user). State the conclusion/data directly — do not end with only a tool call or an empty turn."}}'
  exit 0
fi

# SubagentStop. Loop guard first. This early exit is an ACCEPTED terminal stop (the gate
# emits nothing and the subagent is done), so it MUST record its `stop` row — skipping it
# would leave a permanent phantom unreconciled key.
if [ "$(hook_json "$PAYLOAD" '.stop_hook_active')" = "true" ]; then
  _registry_append stop
  exit 0
fi

# Prefer the direct final-message field if the runtime provides it (SubagentStop may expose
# `last_assistant_message`); else read the SUBAGENT transcript (`agent_transcript_path`),
# falling back to `transcript_path`. This avoids validating the parent session's transcript.
LASTMSG=$(hook_json "$PAYLOAD" '.last_assistant_message')
if [ -n "$LASTMSG" ]; then
  if [ -z "$(printf '%s' "$LASTMSG" | tr -d '[:space:]')" ]; then
    _registry_append stop_blocked
    jq -nc '{"decision":"block","reason":"[subagent-validate] your final turn was empty — return a concrete non-empty result; your last message is the value handed to the caller."}'
  else
    _registry_append stop
  fi
  exit 0
fi

TRANSCRIPT=$(hook_json "$PAYLOAD" '.agent_transcript_path')
[ -z "$TRANSCRIPT" ] && TRANSCRIPT=$(hook_json "$PAYLOAD" '.transcript_path')
# no transcript → fail-open. A fail-open stop is NOT blocked, so it is terminal: record it.
if [ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ]; then
  _registry_append stop
  exit 0
fi

# Count assistant turns. None at all → unknown shape → fail open (silent, terminal).
ANY=$(jq -rs '[ .[] | select(type=="object" and (.message.role? == "assistant")) ] | length' "$TRANSCRIPT" 2>/dev/null || echo 0)
if ! [ "${ANY:-0}" -gt 0 ] 2>/dev/null; then
  _registry_append stop
  exit 0
fi

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
  _registry_append stop_blocked
  jq -nc '{"decision":"block","reason":"[subagent-validate] your final turn was empty (or only a tool call) — return a concrete non-empty result; your last message is the value handed to the caller."}'
else
  _registry_append stop
fi
exit 0

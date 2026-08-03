#!/usr/bin/env bash
# Hermetic test for subagent-validate.sh (U-HK-17 + U-HK-43). Synthetic
# SubagentStart/Stop payloads + throwaway transcript JSONL files. Asserts: Start injects
# a contract; Stop blocks on an empty final turn, passes on a non-empty one (string +
# array content shapes), honors the stop_hook_active guard, and FAILS OPEN on missing
# transcript / unknown shape.
#
# U-HK-43 cases (10+) additionally assert the lifecycle-registry append: start /
# stop / stop_blocked rows, the stop_hook_active terminal `stop`, gate output
# byte-identical under an unwritable registry dir, and the flock envelope (5 concurrent
# appends untorn; a lock held past the in-process deadline skips the write and still
# exits promptly).
#
# CLAUDE_PROJECT_DIR is exported to a throwaway dir so `hook_project_dir` resolves the
# registry INSIDE the scratch tree — no case may touch the real workspace `.harness/`.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/subagent-validate.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

TMP="$(mktemp -d)"; { [ -n "$TMP" ] && [ -d "$TMP" ]; } || { echo "FATAL mktemp"; exit 1; }
trap 'chmod -R u+rwX "$TMP" 2>/dev/null; rm -rf "$TMP"' EXIT

# Scratch project dir: every hook invocation below resolves the U-HK-43 registry HERE.
PROJ="$TMP/proj"; mkdir -p "$PROJ/.harness"
export CLAUDE_PROJECT_DIR="$PROJ"
REG="$PROJ/.harness/.agents-registry.jsonl"
reg_rows() { jq -s 'length' "$REG" 2>/dev/null || echo -1; }   # -1 ⇒ a line is torn
reg_count() { jq -s --arg e "$1" '[ .[] | select(.event==$e) ] | length' "$REG" 2>/dev/null || echo -1; }

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

# 8) last_assistant_message provided directly → used without a transcript read.
OUT=$(run '{"hook_event_name":"SubagentStop","last_assistant_message":"here is the result"}')
[ -z "$OUT" ] && ok "non-empty last_assistant_message → no block" || bad "blocked good direct msg: $OUT"
OUT=$(run '{"hook_event_name":"SubagentStop","last_assistant_message":"   "}')
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "empty last_assistant_message → block" || bad "did not block empty direct msg: $OUT"

# 9) agent_transcript_path is preferred over transcript_path (subagent vs parent).
T="$TMP/agent.jsonl"; echo '{"message":{"role":"assistant","content":"   "}}' > "$T"
P="$TMP/parent.jsonl"; echo '{"message":{"role":"assistant","content":"parent ok"}}' > "$P"
OUT=$(printf '%s' "$(jq -nc --arg a "$T" --arg p "$P" '{"hook_event_name":"SubagentStop","agent_transcript_path":$a,"transcript_path":$p}')" | bash "$HOOK")
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "uses agent_transcript_path (subagent), not parent" || bad "validated wrong transcript: $OUT"

# ---------------------------------------------------------------------------
# U-HK-43 — lifecycle registry. Byte-exact gate-output fixtures first: these are the
# EXACT bytes the hook emitted before the registry existed (captured from the committed
# pre-U-HK-43 hook), so any drift in the gate's emission fails here.
EXP_START="$TMP/exp-start.json"
cat > "$EXP_START" <<'EOF'
{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":"[subagent-validate] Return a concrete, non-empty result: your FINAL message is the value handed back to the caller (not shown to the user). State the conclusion/data directly — do not end with only a tool call or an empty turn."}}
EOF
EXP_BLOCK_T="$TMP/exp-block-transcript.json"
cat > "$EXP_BLOCK_T" <<'EOF'
{"decision":"block","reason":"[subagent-validate] your final turn was empty (or only a tool call) — return a concrete non-empty result; your last message is the value handed to the caller."}
EOF
EXP_BLOCK_D="$TMP/exp-block-direct.json"
cat > "$EXP_BLOCK_D" <<'EOF'
{"decision":"block","reason":"[subagent-validate] your final turn was empty — return a concrete non-empty result; your last message is the value handed to the caller."}
EOF

# 10) AC1 — SubagentStart writes exactly one well-formed `start` row; the emitted
#     additionalContext is BYTE-IDENTICAL to the pre-registry hook's.
: > "$REG"
printf '%s' "$(jq -nc '{"hook_event_name":"SubagentStart","session_id":"s1","agent_id":"a1","agent_transcript_path":"/tmp/a1.jsonl"}')" \
  | bash "$HOOK" > "$TMP/start.out" 2>"$TMP/start.err"
RC=$?
[ "$RC" -eq 0 ] && ok "AC1 SubagentStart exits 0" || bad "AC1 start exit $RC"
cmp -s "$TMP/start.out" "$EXP_START" && ok "AC1 additionalContext byte-identical" \
  || bad "AC1 start emission drifted: $(cat "$TMP/start.out")"
[ ! -s "$TMP/start.err" ] && ok "AC1 no stderr leak" || bad "AC1 stderr: $(cat "$TMP/start.err")"
[ "$(reg_rows)" = "1" ] && ok "AC1 exactly one registry line" || bad "AC1 rows=$(reg_rows): $(cat "$REG")"
jq -e '.event=="start" and .agent_id=="a1" and .session=="s1" and .transcript=="/tmp/a1.jsonl"
       and (.ts|test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")) and (.cwd|length>0)' \
  "$REG" >/dev/null 2>&1 && ok "AC1 start row well-formed (6 fields)" || bad "AC1 malformed row: $(cat "$REG")"

# 10b) Registry fallback is PARENT-FIRST (transcript_path, then agent_transcript_path):
#      Start payloads never carry agent_transcript_path, so child-first would record a
#      start and its stop under unmatchable keys (codex round-1 on #1200).
: > "$REG"
printf '%s' '{"hook_event_name":"SubagentStart","transcript_path":"/tmp/parent.jsonl"}' | bash "$HOOK" >/dev/null 2>&1
jq -e '.transcript=="/tmp/parent.jsonl" and .agent_id==""' "$REG" >/dev/null 2>&1 \
  && ok "AC1 start falls back to transcript_path; empty agent_id tolerated" || bad "AC1 fallback: $(cat "$REG")"

# 10c) Same-key discriminator: a realistic Start (parent path only) + its accepted Stop
#      (BOTH paths, no agent_id) must land on the SAME transcript key. Kills a
#      child-first regression: under child-first the stop row would carry the child
#      path and never reconcile the start.
: > "$REG"
TC="$TMP/child10c.jsonl"; echo '{"message":{"role":"assistant","content":"done"}}' > "$TC"
printf '%s' '{"hook_event_name":"SubagentStart","transcript_path":"/tmp/parent10c.jsonl"}' | bash "$HOOK" >/dev/null 2>&1
printf '%s' "$(jq -nc --arg t "$TC" '{"hook_event_name":"SubagentStop","transcript_path":"/tmp/parent10c.jsonl","agent_transcript_path":$t}')" \
  | bash "$HOOK" >/dev/null 2>&1
K1=$(jq -r 'select(.event=="start") | .transcript' "$REG"); K2=$(jq -r 'select(.event=="stop") | .transcript' "$REG")
{ [ -n "$K1" ] && [ "$K1" = "$K2" ]; } \
  && ok "AC1/AC2 start and stop share one fallback key ($K1)" \
  || bad "asymmetric fallback keys: start='$K1' stop='$K2'"

# 11) AC2 — Stop with a non-empty (accepted) result → one terminal `stop` row, silent.
: > "$REG"
T="$TMP/acc.jsonl"; echo '{"message":{"role":"assistant","content":"result 7"}}' > "$T"
OUT=$(printf '%s' "$(jq -nc --arg t "$T" '{"hook_event_name":"SubagentStop","agent_transcript_path":$t,"agent_id":"a1","session_id":"s1"}')" | bash "$HOOK" 2>"$TMP/acc.err")
RC=$?
{ [ -z "$OUT" ] && [ "$RC" -eq 0 ] && [ ! -s "$TMP/acc.err" ]; } && ok "AC2 accepted stop stays silent" || bad "AC2 output=$OUT rc=$RC"
{ [ "$(reg_rows)" = "1" ] && [ "$(reg_count stop)" = "1" ]; } && ok "AC2 one terminal stop row" || bad "AC2 rows=$(reg_rows): $(cat "$REG")"

# 12) AC3 — Stop with an EMPTY result → `stop_blocked` (NOT `stop`) AND the existing
#     decision:block is still emitted, byte-identical.
: > "$REG"
T="$TMP/emp.jsonl"; echo '{"message":{"role":"assistant","content":"   "}}' > "$T"
printf '%s' "$(jq -nc --arg t "$T" '{"hook_event_name":"SubagentStop","agent_transcript_path":$t,"agent_id":"a1"}')" \
  | bash "$HOOK" > "$TMP/blk.out" 2>"$TMP/blk.err"
cmp -s "$TMP/blk.out" "$EXP_BLOCK_T" && ok "AC3 decision:block byte-identical (transcript path)" \
  || bad "AC3 block emission drifted: $(cat "$TMP/blk.out")"
{ [ "$(reg_count stop_blocked)" = "1" ] && [ "$(reg_count stop)" = "0" ]; } \
  && ok "AC3 records stop_blocked, NOT terminal stop" || bad "AC3 rows: $(cat "$REG")"

# 12b) Same discriminator on the direct last_assistant_message path.
: > "$REG"
printf '%s' '{"hook_event_name":"SubagentStop","last_assistant_message":"   ","agent_id":"a2"}' \
  | bash "$HOOK" > "$TMP/blk2.out" 2>/dev/null
cmp -s "$TMP/blk2.out" "$EXP_BLOCK_D" && ok "AC3 direct-message block byte-identical" \
  || bad "AC3 direct block drifted: $(cat "$TMP/blk2.out")"
{ [ "$(reg_count stop_blocked)" = "1" ] && [ "$(reg_count stop)" = "0" ]; } \
  && ok "AC3 direct empty message → stop_blocked" || bad "AC3 direct rows: $(cat "$REG")"
: > "$REG"
printf '%s' '{"hook_event_name":"SubagentStop","last_assistant_message":"here it is","agent_id":"a2"}' | bash "$HOOK" >/dev/null 2>&1
{ [ "$(reg_count stop)" = "1" ] && [ "$(reg_count stop_blocked)" = "0" ]; } \
  && ok "AC3 direct non-empty message → terminal stop" || bad "AC3 direct accept rows: $(cat "$REG")"

# 13) stop_hook_active early exit is an ACCEPTED terminal stop — it MUST record `stop`
#     before exiting, else the key is a permanent phantom unreconciled entry.
: > "$REG"
OUT=$(printf '%s' "$(jq -nc --arg t "$T" '{"hook_event_name":"SubagentStop","agent_transcript_path":$t,"stop_hook_active":true,"agent_id":"a9"}')" | bash "$HOOK")
[ -z "$OUT" ] && ok "stop_hook_active still silent" || bad "stop_hook_active emitted: $OUT"
{ [ "$(reg_rows)" = "1" ] && jq -e '.event=="stop" and .agent_id=="a9"' "$REG" >/dev/null 2>&1; } \
  && ok "stop_hook_active records terminal stop before exit" || bad "stop_hook_active rows: $(cat "$REG")"

# 13b) Fail-open stops (missing transcript / unknown shape) are not blocked, so they are
#      terminal and must reconcile too.
: > "$REG"
printf '%s' "$(pl_stop "$TMP/nope.jsonl")" | bash "$HOOK" >/dev/null 2>&1
W="$TMP/weird2.jsonl"; echo '{"some":"other"}' > "$W"
printf '%s' "$(pl_stop "$W")" | bash "$HOOK" >/dev/null 2>&1
{ [ "$(reg_rows)" = "2" ] && [ "$(reg_count stop)" = "2" ]; } \
  && ok "fail-open stops recorded as terminal" || bad "fail-open rows: $(cat "$REG")"

# 14) AC4 — unwritable registry dir → gate behavior byte-identical, exit 0, no stderr.
RO="$TMP/ro"; mkdir -p "$RO/.harness"; chmod 500 "$RO/.harness"
printf '%s' '{"hook_event_name":"SubagentStart"}' | CLAUDE_PROJECT_DIR="$RO" bash "$HOOK" > "$TMP/ro.out" 2>"$TMP/ro.err"
RC=$?
{ [ "$RC" -eq 0 ] && [ ! -s "$TMP/ro.err" ] && cmp -s "$TMP/ro.out" "$EXP_START"; } \
  && ok "AC4 unwritable dir: Start byte-identical, exit 0, no stderr" || bad "AC4 rc=$RC err=$(cat "$TMP/ro.err") out=$(cat "$TMP/ro.out")"
printf '%s' "$(jq -nc --arg t "$T" '{"hook_event_name":"SubagentStop","agent_transcript_path":$t}')" \
  | CLAUDE_PROJECT_DIR="$RO" bash "$HOOK" > "$TMP/ro2.out" 2>"$TMP/ro2.err"
RC=$?
{ [ "$RC" -eq 0 ] && [ ! -s "$TMP/ro2.err" ] && cmp -s "$TMP/ro2.out" "$EXP_BLOCK_T"; } \
  && ok "AC4 unwritable dir: block byte-identical, exit 0, no stderr" || bad "AC4 stop rc=$RC err=$(cat "$TMP/ro2.err")"
[ ! -e "$RO/.harness/.agents-registry.jsonl" ] && ok "AC4 no registry written" || bad "AC4 registry appeared under 500 dir"
chmod 700 "$RO/.harness"

# 15) AC5 — 5 concurrent SubagentStarts → exactly 5 independently parseable rows, untorn.
: > "$REG"
for i in 1 2 3 4 5; do
  printf '%s' "$(jq -nc --arg a "c$i" '{"hook_event_name":"SubagentStart","agent_id":$a,"session_id":"cs"}')" \
    | bash "$HOOK" >/dev/null 2>&1 &
done
wait
LINES=$(wc -l < "$REG" | tr -d ' ')
{ [ "$LINES" = "5" ] && [ "$(reg_rows)" = "5" ]; } && ok "AC5 5 concurrent starts → 5 untorn lines" \
  || bad "AC5 lines=$LINES parsed=$(reg_rows): $(cat "$REG")"
[ "$(jq -r '.agent_id' "$REG" 2>/dev/null | sort | tr '\n' ',')" = "c1,c2,c3,c4,c5," ] \
  && ok "AC5 all 5 rows complete + distinct" || bad "AC5 ids: $(jq -r '.agent_id' "$REG" | sort | tr '\n' ',')"

# 15b) AC5 skip path — a lock held PAST the in-process deadline: the hook must still exit
#      promptly (~2s, not the holder's 8s), gate behavior unchanged, and write NOTHING
#      partial. Deterministic: the holder announces on stdout once flock is held.
: > "$REG"
/usr/bin/python3 -c '
import fcntl, sys, time
f = open(sys.argv[1], "a+")
fcntl.flock(f.fileno(), fcntl.LOCK_EX)
sys.stdout.write("held\n"); sys.stdout.flush()
time.sleep(8)
' "$PROJ/.harness/.agents-registry.lock" > "$TMP/holder.out" 2>/dev/null &
HOLDER=$!
for _ in $(seq 1 200); do [ -s "$TMP/holder.out" ] && break; sleep 0.05; done
[ -s "$TMP/holder.out" ] && ok "AC5b lock holder acquired flock" || bad "AC5b holder never acquired lock"
S=$(date +%s)
printf '%s' '{"hook_event_name":"SubagentStart"}' | bash "$HOOK" > "$TMP/hold.out" 2>"$TMP/hold.err"
RC=$?
ELAPSED=$(( $(date +%s) - S ))
[ "$ELAPSED" -le 4 ] && ok "AC5b hook exits promptly under a held lock (${ELAPSED}s ≤ 4s, holder holds 8s)" \
  || bad "AC5b hook waited ${ELAPSED}s"
{ [ "$RC" -eq 0 ] && [ ! -s "$TMP/hold.err" ] && cmp -s "$TMP/hold.out" "$EXP_START"; } \
  && ok "AC5b gate behavior unchanged past deadline" || bad "AC5b rc=$RC err=$(cat "$TMP/hold.err")"
[ ! -s "$REG" ] && ok "AC5b past-deadline write skipped, nothing partial" || bad "AC5b partial write: $(cat "$REG")"
kill "$HOLDER" 2>/dev/null; wait "$HOLDER" 2>/dev/null
printf '%s' '{"hook_event_name":"SubagentStart","agent_id":"after"}' | bash "$HOOK" >/dev/null 2>&1
{ [ "$(reg_rows)" = "1" ] && jq -e '.agent_id=="after"' "$REG" >/dev/null 2>&1; } \
  && ok "AC5b registry usable again once the lock frees" || bad "AC5b post-release rows: $(cat "$REG")"

echo "----"
echo "subagent_validate: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

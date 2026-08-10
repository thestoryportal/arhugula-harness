#!/usr/bin/env bash
# Hermetic test for capture-failure.sh (U-HK-07 + U-CTX-07). Asserts logging +
# recurrence nudge + the 4-segment signature + the per-session emission cap.

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

# 5) session-scoped recurrence (P3 regression): the same sig in a NEW session must
#    NOT inherit the prior session's count. Fresh log; two distinct session_ids.
: > "$LOG"
S1='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"e","session_id":"sess-A"}'
S2='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"e","session_id":"sess-B"}'
run "$S1" >/dev/null                       # sess-A count=1
OUT=$(run "$S2")                           # sess-B first occurrence → count=1, no nudge
printf '%s' "$OUT" | grep -q "recurring" && bad "cross-session count leaked (P3): $OUT" || ok "new session does not inherit prior count"
OUT=$(run "$S2")                           # sess-B second occurrence → count=2 → nudge
printf '%s' "$OUT" | grep -q "recurring failure (2x" && ok "same-session recurrence still nudges at 2" || bad "same-session nudge missing: $OUT"
[ "$(grep -c '"session":"sess-B"' "$LOG")" = "2" ] && ok "rows tagged with session_id" || bad "session_id not recorded"

# 6) U-CTX-07 (+ codex round-4): the 4th segment COMPOSES exit code and command
#    head — exit code alone collapsed unrelated commands that both exit 1.
: > "$LOG"
EC='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"command_failed","session_id":"sess-EC","tool_input":{"command":"npm test"},"tool_error":{"exit_code":"1"}}'
run "$EC" >/dev/null
SIG_ROW=$(tail -1 "$LOG")
printf '%s' "$SIG_ROW" | jq -e '.sig == "PostToolUseFailure:Bash:command_failed:1:npm test"' >/dev/null \
  && ok "sig composes exit_code + command head" || bad "sig not composed: $SIG_ROW"

# 6b) codex round-4: same exit code, DIFFERENT commands → distinct signatures — the
#     second command's first failure must NOT count as a recurrence of the first.
EC2='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"command_failed","session_id":"sess-EC","tool_input":{"command":"git status"},"tool_error":{"exit_code":"1"}}'
OUT=$(run "$EC2")
[ -z "$OUT" ] && ok "distinct command with same exit code is NOT a recurrence" || bad "cross-command false recurrence: $OUT"
[ "$(jq -rs '[.[].sig] | unique | length' "$LOG")" = "2" ] && ok "two distinct sigs logged for two commands" || bad "sigs collapsed: $(jq -rs '[.[].sig]' "$LOG")"

# 7) U-CTX-07: falls back to a (truncated) command head when no exit_code is present.
: > "$LOG"
CH='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"command_failed","session_id":"sess-CH","tool_input":{"command":"some very long failing command that keeps going past forty characters for sure"}}'
run "$CH" >/dev/null
SIG_ROW=$(tail -1 "$LOG")
printf '%s' "$SIG_ROW" | jq -e '.sig == "PostToolUseFailure:Bash:command_failed:some very long failing command that keep"' >/dev/null \
  && ok "sig falls back to a 40-char command head" || bad "sig missing cmdhead fallback: $SIG_ROW"

# 8) U-CTX-07: per-session emission cap — only the first TWO nudges of a session are
#    ever emitted; every qualifying nudge after that is capped (logged, not re-emitted).
: > "$LOG"
CAP='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"cap_test","session_id":"sess-CAP"}'
O1=$(run "$CAP")   # recur=1 → no nudge (below cardinality threshold)
O2=$(run "$CAP")   # recur=2 → nudge #1
O3=$(run "$CAP")   # recur=3 → nudge #2
O4=$(run "$CAP")   # recur=4 → would-nudge but cap reached → suppressed
O5=$(run "$CAP")   # recur=5 → still suppressed
[ -z "$O1" ] && ok "cap: occurrence 1 no nudge" || bad "cap: occurrence 1 nudged: $O1"
printf '%s' "$O2" | grep -q "recurring failure" && ok "cap: occurrence 2 nudges (1st emission)" || bad "cap: occurrence 2 missing nudge: $O2"
printf '%s' "$O3" | grep -q "recurring failure" && ok "cap: occurrence 3 nudges (2nd emission)" || bad "cap: occurrence 3 missing nudge: $O3"
[ -z "$O4" ] && ok "cap: occurrence 4 suppressed (cap reached)" || bad "cap: occurrence 4 not capped: $O4"
[ -z "$O5" ] && ok "cap: occurrence 5 suppressed (cap reached)" || bad "cap: occurrence 5 not capped: $O5"
[ "$(wc -l < "$LOG" | tr -d ' ')" = "5" ] && ok "cap: all 5 occurrences still logged (cap only suppresses emission)" || bad "cap: log row count wrong"
[ "$(grep -c '"emitted":true' "$LOG")" = "2" ] && ok "cap: exactly 2 rows marked emitted:true this session" || bad "cap: emitted:true row count wrong"

# 9) codex P2: a command with JSON-escaped characters (quotes) must still reach the
#    recurrence threshold — the old raw grep compared the raw sig against the
#    JSON-escaped logged value and never matched, so quoted commands never nudged.
: > "$LOG"
QC='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"command_failed","session_id":"sess-QC","tool_input":{"command":"python -c \"print(1)\" --flag"}}'
run "$QC" >/dev/null
OUT=$(run "$QC")
printf '%s' "$OUT" | grep -q "recurring failure (2x" && ok "quoted-command recurrence reaches threshold (parsed count)" || bad "quoted-command recurrence broken: $OUT"

# 10) codex P2: a MULTILINE command head must be flattened then globally truncated —
#     cut -c1-40 alone kept 40 chars of EVERY line (unbounded signature).
: > "$LOG"
ML='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"command_failed","session_id":"sess-ML","tool_input":{"command":"line-one-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\nline-two-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\nline-three-ccccc"}}'
run "$ML" >/dev/null
SIGLEN=$(tail -1 "$LOG" | jq -r .sig | wc -c | tr -d ' ')
# sig = "PostToolUseFailure:Bash:command_failed:" (39 chars) + <=40 head + newline from wc
[ "$SIGLEN" -le 81 ] && ok "multiline command head globally bounded (sig ${SIGLEN}B)" || bad "multiline sig unbounded: ${SIGLEN}B"
[ "$(tail -1 "$LOG" | wc -l | tr -d ' ')" = "1" ] && ok "multiline command produced a single JSONL row" || bad "row not single-line"

# 11) codex P2: the emission cap must hold under PARALLEL invocations — the unlocked
#     read-then-append let overlapping hooks all see the same prior count (a 12-way
#     probe emitted 6). With the mkdir lock, exactly 2 of these emit.
: > "$LOG"
PAR='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"par_test","session_id":"sess-PAR"}'
run "$PAR" >/dev/null   # seed: recur=1 (below threshold) so every parallel run qualifies
for _i in 1 2 3 4 5 6 7 8 9 10 11 12; do
  ( printf '%s' "$PAR" | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" >/dev/null 2>&1 ) &
done
wait
EMITTED=$(grep -c '"emitted":true' "$LOG")
[ "$EMITTED" = "2" ] && ok "parallel 12-way probe emits exactly 2 (lock holds the cap)" || bad "parallel cap broken: $EMITTED emitted"
[ "$(wc -l < "$LOG" | tr -d ' ')" = "13" ] && ok "parallel probe: all 13 occurrences logged" || bad "parallel probe: log row count $(wc -l < "$LOG")"
[ ! -d "$LOG.lock" ] && ok "lock released after parallel probe" || bad "lock directory leaked"

# 12) codex round-2: when the lock CANNOT be acquired, the row is still logged but
#     emission is SUPPRESSED — an unserialized cap decision re-opens the spam (a
#     20-contender lockless run emitted 3-6). Hold the lock externally with a fresh
#     mtime; CAPTURE_FAILURE_LOCK_TRIES=2 keeps the test fast.
: > "$LOG"
LT='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"lock_test","session_id":"sess-LT"}'
run "$LT" >/dev/null   # recur=1 seed
mkdir "$LOG.lock"      # fresh external holder (mtime now — not stale-reclaimable)
OUT=$(printf '%s' "$LT" | CLAUDE_PROJECT_DIR="$REPO" CAPTURE_FAILURE_LOCK_TRIES=2 bash "$HOOK" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)
rmdir "$LOG.lock"
[ -z "$OUT" ] && ok "lock timeout suppresses emission (cap stays serialized)" || bad "lock timeout emitted: $OUT"
[ "$(wc -l < "$LOG" | tr -d ' ')" = "2" ] && ok "lock timeout still logs the row" || bad "lock-timeout row not logged"
[ "$(tail -1 "$LOG" | jq -r .emitted)" = "false" ] && ok "lock-timeout row marked emitted:false" || bad "lock-timeout row emitted flag wrong"

# 13) codex round-3: stale-lock takeover must be OWNERSHIP-SAFE — with an AGED
#     stale lock pre-seeded and 12 parallel qualifying contenders, the bare-rmdir
#     reclaim let one contender destroy another's fresh acquisition (3 emitted).
#     The mv-takeover keeps the cap exact: still exactly 2 emitted.
: > "$LOG"
ST='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"stale_test","session_id":"sess-ST"}'
run "$ST" >/dev/null   # seed: recur=1 so every parallel run qualifies
mkdir "$LOG.lock"
touch -t 202001010000 "$LOG.lock" 2>/dev/null || touch -d '2020-01-01' "$LOG.lock" 2>/dev/null
for _i in 1 2 3 4 5 6 7 8 9 10 11 12; do
  ( printf '%s' "$ST" | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" >/dev/null 2>&1 ) &
done
wait
EMITTED=$(grep -c '"emitted":true' "$LOG")
[ "$EMITTED" = "2" ] && ok "aged-stale-lock 12-way probe emits exactly 2 (ownership-safe takeover)" || bad "stale-takeover cap broken: $EMITTED emitted"
[ "$(wc -l < "$LOG" | tr -d ' ')" = "13" ] && ok "stale-takeover probe: all 13 occurrences logged" || bad "stale probe: log rows $(wc -l < "$LOG")"
[ ! -d "$LOG.lock" ] && ok "lock released after stale-takeover probe" || bad "lock directory leaked after stale probe"

# 14) codex round-4: release must verify OWNERSHIP — a hook must never delete a
#     lock it does not own. Seed a foreign-owned FRESH lock; the hook times out
#     (suppressed emission per #12) and the foreign lock must SURVIVE.
: > "$LOG"
FO='{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","error_type":"own_test","session_id":"sess-FO"}'
run "$FO" >/dev/null
mkdir "$LOG.lock"; printf '%s' "someone-else" > "$LOG.lock/owner"
printf '%s' "$FO" | CLAUDE_PROJECT_DIR="$REPO" CAPTURE_FAILURE_LOCK_TRIES=2 bash "$HOOK" >/dev/null 2>&1
[ -d "$LOG.lock" ] && [ "$(cat "$LOG.lock/owner")" = "someone-else" ] \
  && ok "foreign-owned fresh lock survives (ownership-checked release)" || bad "foreign lock deleted or mutated"
rm -rf "$LOG.lock"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

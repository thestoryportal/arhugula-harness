#!/usr/bin/env bash
# Hermetic test for stop-loop.sh (U-HK-14). Asserts: inert off-mode, continue-with-
# next-action in loop mode, halt-marker stand-down, iteration-cap termination, and the
# counter increments per turn.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/stop-loop.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"; { [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL mktemp"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
mkdir -p "$REPO/.harness"
# C-HE-09 §2 (U-HE-29): the loop ledger is a SHARED venue outside every worktree, so it is
# no longer reachable as "$REPO/.harness/loop_status.md". Pin it hermetically for this run.
export HARNESS_LOOP_STATUS_PATH="$REPO/shared-loop_status.md"

# The loop always runs inside a git checkout, and several hook paths shell out to git. A
# non-repo scratch dir makes those degrade in ways production never sees, so the fixture is
# a real repo.
( cd "$REPO" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init ) >/dev/null 2>&1

# Minimal dashboard with a Next action section carrying an R-id.
cat > "$REPO/.harness/roadmap_status.md" <<'EOF'
## Next action
Drive `R-410` next.
---
EOF

run_on()  { printf '{}' | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"; }
run_off() { printf '{}' | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"; }
unset HARNESS_LOOP

# 1) INERT off-mode.
OUT=$(run_off); [ -z "$OUT" ] && ok "inert off-mode" || bad "spoke off-mode: $OUT"

# Merge-gate reviewers inherit loop mode but are lifecycle-isolated and must not mutate
# the controller's counter or force another turn.
OUT=$(printf '{}' | HARNESS_LOOP=1 HARNESS_CODEX_REVIEW_ISOLATED=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && [ ! -f "$REPO/.harness/.loop-iter" ] \
  && ok "isolated reviewer neither blocks nor touches loop counter" \
  || bad "isolated reviewer affected loop state: $OUT"

# 2) Continue: blocks + injects next-action; counter → 1.
OUT=$(run_on)
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "blocks to continue in loop mode" || bad "did not block: $OUT"
echo "$OUT" | jq -e '.reason | test("R-410")' >/dev/null 2>&1 && ok "injects next-action R-410" || bad "no next-action: $OUT"
[ "$(cat "$REPO/.harness/.loop-iter")" = "1" ] && ok "counter incremented to 1" || bad "counter wrong: $(cat "$REPO/.harness/.loop-iter" 2>/dev/null)"

# 3) Counter increments per turn.
run_on >/dev/null; run_on >/dev/null
[ "$(cat "$REPO/.harness/.loop-iter")" = "3" ] && ok "counter increments per turn (=3)" || bad "counter=$(cat "$REPO/.harness/.loop-iter")"

# 4) Iteration cap → stop + reset (HARNESS_LOOP_MAX=2 with counter already 3).
OUT=$(printf '{}' | HARNESS_LOOP=1 HARNESS_LOOP_MAX=2 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && ok "iteration cap → allows stop" || bad "blocked past cap: $OUT"
[ ! -f "$REPO/.harness/.loop-iter" ] && ok "counter reset at cap" || bad "counter not reset"
[ -f "$REPO/.harness/.loop-halt" ] && ok "cap raises halt marker (real boundary)" || bad "cap did not raise halt marker"
grep -q '| STOP | lane=[^|]* | iteration cap' "$HARNESS_LOOP_STATUS_PATH" && ok "cap logged to ledger" || bad "cap not logged"
rm -f "$REPO/.harness/.loop-halt"

# 5) Halt marker → stand down (allow stop) + marker PRESERVED for the runner (codex P1:
#    the in-session hook must not consume the gate signal the outer runner needs to see).
: > "$REPO/.harness/.loop-halt"
OUT=$(run_on)
[ -z "$OUT" ] && ok "halt marker → allows stop" || bad "blocked despite halt: $OUT"
[ -f "$REPO/.harness/.loop-halt" ] && ok "halt marker preserved for runner" || bad "halt marker was consumed"
grep -q '| STOP | lane=[^|]* | halt marker' "$HARNESS_LOOP_STATUS_PATH" && ok "halt logged to ledger" || bad "halt not logged"
rm -f "$REPO/.harness/.loop-halt"

# 6) Non-numeric HARNESS_LOOP_MAX must not break the cap (codex P2): falls back to 25,
#    so a counter ≥ 25 still stops instead of blocking forever.
printf '30' > "$REPO/.harness/.loop-iter"
OUT=$(printf '{}' | HARNESS_LOOP=1 HARNESS_LOOP_MAX=abc CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && ok "non-numeric MAX → defaults to 25, counter 30 stops" || bad "invalid MAX kept blocking: $OUT"

# 7) Skip-set injection (the defer-and-ADVANCE mechanism — the load-bearing fix). With a
#    ledger carrying open DEFERRED-HIL rows, the continue-reason must carry those item-IDs
#    (so a fresh headless `claude -p` child skips them off the static pointer) and must
#    instruct defer-and-advance, NOT halt-at-gate. Since U-HE-29 a row that PRECEDES an
#    ACTIVATE is included too (C-HE-09 §4, option b): the ledger is shared across lanes, so
#    an ACTIVATE-scoped window would let one lane's activation un-skip another lane's
#    still-open gate and the loop would re-attempt it. Only a RESOLVED-HIL row clears an
#    item — over-skipping is safe, under-skipping re-loops.
rm -f "$REPO/.harness/.loop-iter" "$REPO/.harness/.loop-halt"
cat > "$HARNESS_LOOP_STATUS_PATH" <<'EOF'
# ledger
| ts | kind | detail |
|---|---|---|
| t0 | DEFERRED-HIL | R-999 — still open, never resolved |
| t1 | ACTIVATE | this run |
| t2 | DEFERRED-HIL | R-888 — deferred then answered |
| t3 | RESOLVED-HIL | R-888 — the operator answered it |
| t2 | DEFERRED-HIL | R-410 — needs container runtime |
| t3 | DEFERRED-HIL | R-300 — needs OpenAI creds |
EOF
OUT=$(run_on)
echo "$OUT" | jq -e '.reason | test("ALREADY DEFERRED")'         >/dev/null 2>&1 && ok "reason carries the skip-set header" || bad "no skip-set header: $OUT"
echo "$OUT" | jq -e '.reason | test("R-410")'                    >/dev/null 2>&1 && ok "skip-set includes R-410 (this run)" || bad "R-410 missing from skip-set"
echo "$OUT" | jq -e '.reason | test("R-300")'                    >/dev/null 2>&1 && ok "skip-set includes R-300 (this run)" || bad "R-300 missing from skip-set"
echo "$OUT" | jq -e '.reason | test("R-999")'                    >/dev/null 2>&1 && ok "skip-set INCLUDES a still-open pre-ACTIVATE row (C-HE-09 §4)" || bad "ACTIVATE dropped an open deferral: $OUT"
echo "$OUT" | jq -e '.reason | test("R-888") | not'              >/dev/null 2>&1 && ok "skip-set EXCLUDES a RESOLVED item (the only exit)" || bad "resolved item leaked into skip-set: $OUT"
echo "$OUT" | jq -e '.reason | test("do NOT raise .loop-halt")'  >/dev/null 2>&1 && ok "instructs defer-NOT-halt at a gate" || bad "missing defer-not-halt guidance"
echo "$OUT" | jq -e '.reason | test("tools/04-loop/defer.sh")'      >/dev/null 2>&1 && ok "instructs the allowlisted defer.sh wrapper (not a denied raw source)" || bad "missing defer.sh wrapper guidance"
echo "$OUT" | jq -e '.reason | test("tools/04-loop/halt.sh")'       >/dev/null 2>&1 && ok "instructs the allowlisted halt.sh wrapper for stand-down" || bad "missing halt.sh wrapper guidance"
echo "$OUT" | jq -e '.reason | test("exhausted")'                >/dev/null 2>&1 && ok "exhaustion is the ONLY stand-down condition" || bad "missing exhaustion condition"


# 8) Context ceiling (U-HE-58, plan §9 B4 / decision 7). The three arms of the verdict enum,
#    driven end-to-end through the hook off a real transcript file — the reading, the ceiling
#    and the dispatch, not just the presence of the call. MEMENTO_ROOT is pinned at a path
#    that does not exist so the ceiling resolves to the 250,000 default and the suite never
#    depends on whether the operator has the plugin installed.
rm -f "$REPO/.harness/.loop-iter" "$REPO/.harness/.loop-halt"
: > "$HARNESS_LOOP_STATUS_PATH"
export MEMENTO_ROOT="$REPO/no-such-memento"

usage_record() {  # $1 = total tokens, split across the four prompt components
  printf '{"type":"assistant","message":{"usage":{"input_tokens":%s,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0}}}\n' "$1"
}
OVER="$REPO/over.jsonl";  usage_record 300000 > "$OVER"
UNDER="$REPO/under.jsonl"; usage_record 1000  > "$UNDER"
payload() { printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$1" "$REPO"; }
run_ceiling() {  # $1 = transcript, $2 = "headless" or "attended"
  local headless=""; [ "$2" = headless ] && headless=1
  payload "$1" | HARNESS_LOOP=1 HARNESS_LOOP_HEADLESS="$headless" \
    CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"
}

# 8a) Under the ceiling → the normal continuation, unchanged.
OUT=$(run_ceiling "$UNDER" attended)
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "under ceiling → still continues" || bad "under-ceiling did not continue: $OUT"
echo "$OUT" | jq -e '.reason | test("R-410")' >/dev/null 2>&1 && ok "under ceiling → normal next-action reason" || bad "under-ceiling lost the next-action"
echo "$OUT" | jq -e '.reason | test("CONTEXT CEILING") | not' >/dev/null 2>&1 && ok "under ceiling → no close-out reason" || bad "under-ceiling emitted a close-out: $OUT"
[ ! -f "$REPO/.harness/.loop-halt" ] && ok "under ceiling → no halt raised" || bad "under-ceiling raised halt"
rm -f "$REPO/.harness/.loop-iter"

# 8b) Over the ceiling, headless → allow the stop; the runner relaunches. Blocking here
#     would put a second session on one worktree, and a halt would stop the runner dead.
OUT=$(run_ceiling "$OVER" headless)
[ -z "$OUT" ] && ok "over ceiling + headless → allows the stop" || bad "headless blocked at ceiling: $OUT"
[ ! -f "$REPO/.harness/.loop-halt" ] && ok "over ceiling + headless → no halt (runner must relaunch)" || bad "headless ceiling raised halt — runner would stand down"
grep -q '| STOP | lane=[^|]* | context ceiling 300000/250000 — headless' "$HARNESS_LOOP_STATUS_PATH" && ok "headless ceiling logged with the reading" || bad "headless ceiling not logged"

# 8c) Over the ceiling, attended → block once with the close-out instruction.
OUT=$(run_ceiling "$OVER" attended)
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "over ceiling + attended → blocks" || bad "attended did not block at ceiling: $OUT"
echo "$OUT" | jq -e '.reason | test("CONTEXT CEILING")' >/dev/null 2>&1 && ok "attended ceiling → close-out reason" || bad "no close-out reason: $OUT"
echo "$OUT" | jq -e '.reason | test("300000")' >/dev/null 2>&1 && ok "close-out names the reading" || bad "close-out omits the token count"
echo "$OUT" | jq -e '.reason | test("context-save-lean")' >/dev/null 2>&1 && ok "close-out names the recipe (memento absent → the workspace checkpoint)" || bad "close-out names no recipe: $OUT"
echo "$OUT" | jq -e '.reason | test("R-410")' >/dev/null 2>&1 && ok "close-out carries the next-action into the handoff" || bad "close-out drops the next-action"

# 8d) Blocked once, never twice — the bound. A second over-ceiling stop stands down at the
#     spent marker 8c wrote, instead of spending more context on the problem that IS too
#     much context. Without this the attended arm blocks every turn forever.
[ "$(cat "$REPO/.harness/.loop-ceiling-spent" 2>/dev/null)" = "s1" ] && ok "attended ceiling records the session as spent (the bound)" || bad "no spent marker — the close-out block would repeat forever"
OUT=$(run_ceiling "$OVER" attended)
[ -z "$OUT" ] && ok "second over-ceiling stop stands down (blocked once, never twice)" || bad "close-out block repeated: $OUT"
rm -f "$REPO/.harness/.loop-ceiling-spent"

# 8d-ii) The second bound. Writing the spent marker is a best-effort file write; if it fails
#        the close-out arm would re-block every turn forever, so the arm also spends a turn
#        on the counter and the cap carries it. Witnessed by making the marker path
#        unwritable (a directory cannot be truncated into) so the primary bound cannot take.
rm -f "$REPO/.harness/.loop-iter"
mkdir -p "$REPO/.harness/.loop-ceiling-spent"
OUT=$(run_ceiling "$OVER" attended)
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "spent marker unwritable → the close-out still blocks" || bad "close-out lost with an unwritable marker: $OUT"
[ "$(cat "$REPO/.harness/.loop-iter")" = "1" ] && ok "close-out spends a turn on the counter (the second bound)" || bad "close-out did not count its turn: $(cat "$REPO/.harness/.loop-iter" 2>/dev/null)"
#        The counter carries it to the cap: with the spent-marker unwritable, a session that
#        has already spent MAX turns takes step 3 and stands down rather than blocking again.
#        (Step 3 is what fires here, which is the point — the close-out arm must not be able
#        to outrun the cap, whatever happens to its own marker.)
printf '30' > "$REPO/.harness/.loop-iter"
OUT=$(printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$OVER" "$REPO" \
  | HARNESS_LOOP=1 HARNESS_LOOP_MAX=2 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && ok "a counter at the cap stands the session down even with the ceiling over" || bad "close-out escaped both bounds: $OUT"
rm -rf "$REPO/.harness/.loop-ceiling-spent"
rm -f "$REPO/.harness/.loop-iter" "$REPO/.harness/.loop-halt"

# 8d-iii) The spent marker is keyed by SESSION, not by lane (pass-1 concurrency lens P1). A
#         second session sharing the worktree must get its own one block, and must never be
#         stood down by another session's reading.
rm -f "$REPO/.harness/.loop-iter" "$REPO/.harness/.loop-ceiling-spent"
OUT=$(printf '{"transcript_path":"%s","session_id":"alpha","cwd":"%s"}' "$OVER" "$REPO" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
echo "$OUT" | jq -e '.reason | test("CONTEXT CEILING")' >/dev/null 2>&1 && ok "session alpha gets its close-out block" || bad "alpha not blocked: $OUT"
[ "$(cat "$REPO/.harness/.loop-ceiling-spent")" = "alpha" ] && ok "the spent marker records the session id, not a bare flag" || bad "spent marker content: $(cat "$REPO/.harness/.loop-ceiling-spent" 2>/dev/null)"
OUT=$(printf '{"transcript_path":"%s","session_id":"alpha","cwd":"%s"}' "$OVER" "$REPO" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && ok "alpha's SECOND stop stands down (spent)" || bad "alpha re-blocked: $OUT"
OUT=$(printf '{"transcript_path":"%s","session_id":"beta","cwd":"%s"}' "$OVER" "$REPO" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
echo "$OUT" | jq -e '.reason | test("CONTEXT CEILING")' >/dev/null 2>&1 && ok "session beta still gets ITS block (spent-ness is per session)" || bad "beta inherited alpha's spent state: $OUT"
[ ! -f "$REPO/.harness/.loop-halt" ] && ok "the attended arm never raises the lane-wide halt marker" || bad "close-out raised .loop-halt — a concurrent run would stand down"
rm -f "$REPO/.harness/.loop-iter" "$REPO/.harness/.loop-ceiling-spent"

# 8e) An unmeasurable session never strands the run, and is never silent either: the loop
#     continues AND the ledger records that nothing was measured. Asserting only the
#     continuation would pass identically with the whole feature removed (pass-1 codex P2),
#     so the ledger line is the assert that actually distinguishes the two.
: > "$HARNESS_LOOP_STATUS_PATH"
OUT=$(printf '{"transcript_path":"%s","session_id":"s1"}' "$REPO/absent.jsonl" | HARNESS_LOOP=1 \
  MEMENTO_ROOT="$REPO/no-such-memento" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "missing transcript → loop continues unmeasured" || bad "missing transcript stranded the loop: $OUT"
grep -q 'context ceiling unreadable' "$HARNESS_LOOP_STATUS_PATH" && ok "missing transcript is RECORDED as unmeasured, not read as under" || bad "unmeasured session left no ledger row: $(cat "$HARNESS_LOOP_STATUS_PATH")"
: > "$HARNESS_LOOP_STATUS_PATH"
OUT=$(printf '{"session_id":"s1"}' | HARNESS_LOOP=1 MEMENTO_ROOT="$REPO/no-such-memento" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
grep -q 'context ceiling unreadable' "$HARNESS_LOOP_STATUS_PATH" && ok "a payload with no transcript_path is recorded too, never scored as zero" || bad "absent transcript_path scored silently: $(cat "$HARNESS_LOOP_STATUS_PATH")"
rm -f "$REPO/.harness/.loop-iter"
unset MEMENTO_ROOT

# 9) The reading itself (context_tokens.py), driven in the consumer's exact invocation. The
#    transcript scan reads backwards in 256 KB chunks, so the cases that can only go wrong
#    there — a record straddling a chunk boundary, a torn final line, a subagent's sidechain
#    — are witnessed here rather than inferred from the end-to-end arms above.
READER="$SCRIPT_DIR/context_tokens.py"
read_verdict() { printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$1" "$REPO" \
  | MEMENTO_ROOT="$REPO/no-such-memento" /usr/bin/python3 "$READER"; }

V=$(read_verdict "$UNDER")
[ "$(echo "$V" | jq -r .ceiling)" = "250000" ] && ok "memento absent → ceiling is the 250,000 default" || bad "wrong default ceiling: $V"
[ "$(echo "$V" | jq -r .tokens)" = "1000" ] && ok "reads the assistant record's usage" || bad "wrong token sum: $V"

# All four prompt components are summed — a reader that took input_tokens alone would put a
# long session far under its real position, which is the whole failure this guards.
FOUR="$REPO/four.jsonl"
printf '{"type":"assistant","message":{"usage":{"input_tokens":1,"cache_creation_input_tokens":20,"cache_read_input_tokens":300,"output_tokens":4000}}}\n' > "$FOUR"
[ "$(read_verdict "$FOUR" | jq -r .tokens)" = "4321" ] && ok "sums all four prompt components" || bad "component sum wrong: $(read_verdict "$FOUR")"

# The ceiling is a floor the session is AT, not one it must pass: exactly at the ceiling is over.
EXACT="$REPO/exact.jsonl"; usage_record 250000 > "$EXACT"
[ "$(read_verdict "$EXACT" | jq -r .verdict)" = "close-out" ] && ok "exactly at the ceiling counts as over" || bad "boundary is off by one: $(read_verdict "$EXACT")"

# Newest record wins: an earlier, larger reading is history, not this session's position.
NEWEST="$REPO/newest.jsonl"; { usage_record 900000; usage_record 1000; } > "$NEWEST"
[ "$(read_verdict "$NEWEST" | jq -r .tokens)" = "1000" ] && ok "newest assistant record wins over an older one" || bad "scan returned a stale record: $(read_verdict "$NEWEST")"

# A subagent's sidechain describes its own context, never this session's.
SIDE="$REPO/side.jsonl"
{ usage_record 1000; printf '{"isSidechain":true,"type":"assistant","message":{"usage":{"input_tokens":900000}}}\n'; } > "$SIDE"
[ "$(read_verdict "$SIDE" | jq -r .tokens)" = "1000" ] && ok "sidechain records are skipped" || bad "a subagent's usage leaked in: $(read_verdict "$SIDE")"

# A transcript still being appended to ends in a torn line; that is ordinary, not fatal.
TORN="$REPO/torn.jsonl"; { usage_record 1000; printf '{"type":"assis'; } > "$TORN"
[ "$(read_verdict "$TORN" | jq -r .tokens)" = "1000" ] && ok "torn final line is skipped, not fatal" || bad "torn line broke the scan: $(read_verdict "$TORN")"

# A corrupt record that is NOT the final line is real corruption, and skipping it would fall
# through to an older, LOWER usage — an over-ceiling session read as comfortably under, which
# is the one failure direction that matters (pass-1 codex P2). It must fail loudly instead.
CORRUPT="$REPO/corrupt.jsonl"
{ usage_record 900000; printf '{"type":"assistant","message":{"usa\n'; printf '{"type":"user"}\n'; } > "$CORRUPT"
read_verdict "$CORRUPT" >/dev/null 2>&1 && bad "a corrupt mid-file record was skipped, not raised" || ok "a corrupt record before the final line fails loudly"
# Captured rather than piped: the reader exits non-zero here BY DESIGN, and under
# `set -o pipefail` a `python | grep` pipeline would report that exit as the grep's failure.
CORRUPT_ERR=$(printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$CORRUPT" "$REPO" \
  | MEMENTO_ROOT="$REPO/no-such-memento" /usr/bin/python3 "$READER" 2>&1 || true)
case "$CORRUPT_ERR" in
  *"unparseable record before the final line"*) ok "the corruption failure names what it could not measure" ;;
  *) bad "corruption error message unhelpful: $CORRUPT_ERR" ;;
esac

# A record straddling the 256 KB chunk boundary must be rejoined, not read as two fragments.
# The RECORD ITSELF has to be longer than TAIL_CHUNK for that path to run: an earlier version
# of this case padded a preceding line instead, which left the assistant record wholly inside
# the first backward window, so the scan returned on it before a second iteration — and
# deleting the whole straddling_head mechanism kept the test green (pass-1 witness lens P2).
# Here the record is ~300 KB and is the last line, so the first window holds only its tail
# (unparseable alone) and the rejoin is the only way its usage is ever read.
STRADDLE="$REPO/straddle.jsonl"
/usr/bin/python3 -c "
import sys
pad = 'x' * 300_000
with open(sys.argv[1], 'w') as f:
    f.write('{\"type\":\"user\",\"n\":1}\n')
    f.write('{\"type\":\"assistant\",\"pad\":\"%s\",\"message\":{\"usage\":{\"input_tokens\":7777}}}\n' % pad)
" "$STRADDLE"
[ "$(read_verdict "$STRADDLE" | jq -r .tokens)" = "7777" ] && ok "a record straddling the 256 KB chunk boundary is rejoined" || bad "chunk straddle lost the record: $(read_verdict "$STRADDLE" 2>&1)"

# A transcript with no assistant record yet reads zero rather than guessing a number.
EMPTY="$REPO/empty.jsonl"; printf '{"type":"user"}\n' > "$EMPTY"
[ "$(read_verdict "$EMPTY" | jq -r .tokens)" = "0" ] && ok "no assistant record → zero, not a guess" || bad "invented a reading: $(read_verdict "$EMPTY")"

# 10) memento installed. The plugin is optional, so neither arm above touches it — but when
#     it IS there it owns the ceiling and supplies the close-out, and nothing in this repo
#     would otherwise notice an upstream rename of either. The fixture stands in for the
#     install, so what it pins is the five names this repo imports and the two paths it reads
#     — not memento's config grammar, which only the real plugin has. That half was checked by
#     hand against upstream promptctl/memento@0d1f5bc when this landed: with a session layer
#     of `ceiling = 400000` the reading of 300,000 came back `under` at a ceiling of 400,000,
#     where the same payload with memento absent came back `close-out` at 250,000. The two
#     numbers differ, which is what makes that a control rather than a coincidence.
FAKE="$REPO/memento"
mkdir -p "$FAKE/lib" "$FAKE/skills/message-in-a-bottle/bin"
cat > "$FAKE/lib/ceiling_config.py" <<'PY'
"""Stands in for memento's ceiling_config: the names tools/hooks/context_tokens.py imports."""
SHARED_AT_START = "shared-at-start.conf"
def anchored(fallback): return fallback
def session_directory(session_id): return __import__("pathlib").Path("/tmp") / session_id
def shared_at_start(path, anchor): return ("shared", anchor)
def in_force(directory, shared): return 400_000
PY
: > "$FAKE/skills/message-in-a-bottle/bin/finalize-session"
fake_verdict() { printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$1" "$REPO" \
  | MEMENTO_ROOT="$FAKE" /usr/bin/python3 "$READER"; }

V=$(fake_verdict "$OVER")
[ "$(echo "$V" | jq -r .ceiling)" = "400000" ] && ok "memento present → its ceiling wins over the default" || bad "memento ceiling ignored: $V"
[ "$(echo "$V" | jq -r .verdict)" = "under" ] && ok "a reading over 250,000 is under a memento ceiling of 400,000" || bad "memento ceiling not applied to the verdict: $V"
echo "$V" | jq -r .close_out | grep -q "finalize-session --reset compact" && ok "memento present → the close-out is its launcher" || bad "close-out ignored the installed launcher: $V"

# --headless is what separates the two over-ceiling arms, and nothing else does.
[ "$(printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$OVER" "$REPO" | MEMENTO_ROOT="$REPO/nope" /usr/bin/python3 "$READER" --headless | jq -r .verdict)" = "relaunch" ] \
  && ok "--headless selects relaunch over close-out" || bad "--headless did not change the verdict"

echo "----"
echo "stop_loop: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

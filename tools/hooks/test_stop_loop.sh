#!/usr/bin/env bash
# Hermetic test for stop-loop.sh (U-HK-14). Asserts: inert off-mode, continue-with-
# next-action in loop mode, halt-marker stand-down, iteration-cap termination, and the
# counter increments per turn.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/stop-loop.sh"
# For hook_bounded, used as the OUTER guard on the hang witness (section 8f). The hook under
# test sources this itself; the suite borrows the same helper rather than calling a `timeout`
# binary stock macOS does not ship.
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

export REPO="$(mktemp -d)"; { [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL mktemp"; exit 1; }
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
[ -f "$REPO/.harness/.loop-ceiling-spent-s1" ] && ok "attended ceiling records the session as spent (the bound)" || bad "no spent marker — the close-out block would repeat forever"
ITER_BEFORE=$(cat "$REPO/.harness/.loop-iter" 2>/dev/null || echo 0)
OUT=$(run_ceiling "$OVER" attended)
[ -z "$OUT" ] && ok "second over-ceiling stop stands down (blocked once, never twice)" || bad "close-out block repeated: $OUT"
# ...and costs NOTHING. A stand-down is not a turn. When the spent check sat BELOW the
# counter, every redundant Stop against an already-closed-out session silently spent a turn
# of the LANE-WIDE counter; sibling Stop hooks re-fire Stop on the same session, so those
# phantom turns accumulate until the cap raises .loop-halt and stands an unrelated concurrent
# run down — the exact outcome this arc's first P1 removed (pass-3 concurrency P1).
[ "$(cat "$REPO/.harness/.loop-iter" 2>/dev/null || echo 0)" = "$ITER_BEFORE" ] && ok "an already-spent stop spends no counter turn" || bad "spent stop drained the lane counter: ${ITER_BEFORE} -> $(cat "$REPO/.harness/.loop-iter" 2>/dev/null)"
run_ceiling "$OVER" attended >/dev/null; run_ceiling "$OVER" attended >/dev/null
[ "$(cat "$REPO/.harness/.loop-iter" 2>/dev/null || echo 0)" = "$ITER_BEFORE" ] && ok "repeated spent stops still spend nothing (no unbounded drain)" || bad "repeated spent stops drained the counter to $(cat "$REPO/.harness/.loop-iter" 2>/dev/null)"
rm -f "$REPO/.harness/.loop-ceiling-spent-s1"

# 8d-ii) The second bound. Writing the spent marker is a best-effort file write; if it fails
#        the close-out arm would re-block every turn forever, so the arm also spends a turn
#        on the counter and the cap carries it. Witnessed by making the marker path
#        unwritable (a directory cannot be truncated into) so the primary bound cannot take.
rm -f "$REPO/.harness/.loop-iter"
mkdir -p "$REPO/.harness/.loop-ceiling-spent-s1"
OUT=$(run_ceiling "$OVER" attended)
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "spent marker unwritable → the close-out still blocks" || bad "close-out lost with an unwritable marker: $OUT"
[ "$(cat "$REPO/.harness/.loop-iter")" = "1" ] && ok "close-out spends a turn on the counter (the second bound)" || bad "close-out did not count its turn: $(cat "$REPO/.harness/.loop-iter" 2>/dev/null)"
#        The assert below is narrower than it looks, and is labelled for what it actually
#        proves: with ITER=30 and MAX=2 the pre-existing step-3 cap intercepts BEFORE step 4
#        runs at all, so this re-exercises section 4's cap rather than any new close-out
#        interaction. It is kept because the ordering itself is the claim — a session already
#        past its cap must stand down whatever the ceiling says — but the close-out arm's own
#        second bound is witnessed by the counter assert above, not here.
printf '30' > "$REPO/.harness/.loop-iter"
OUT=$(printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$OVER" "$REPO" \
  | HARNESS_LOOP=1 HARNESS_LOOP_MAX=2 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && ok "a counter at the cap stands the session down even with the ceiling over" || bad "close-out escaped both bounds: $OUT"
rm -rf "$REPO/.harness/.loop-ceiling-spent-s1"
rm -f "$REPO/.harness/.loop-iter" "$REPO/.harness/.loop-halt"

# 8d-iii) The spent marker is keyed by SESSION, not by lane (pass-1 concurrency lens P1). A
#         second session sharing the worktree must get its own one block, and must never be
#         stood down by another session's reading.
rm -f "$REPO/.harness/.loop-iter" "$REPO/.harness"/.loop-ceiling-spent-*
OUT=$(printf '{"transcript_path":"%s","session_id":"alpha","cwd":"%s"}' "$OVER" "$REPO" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
echo "$OUT" | jq -e '.reason | test("CONTEXT CEILING")' >/dev/null 2>&1 && ok "session alpha gets its close-out block" || bad "alpha not blocked: $OUT"
[ -f "$REPO/.harness/.loop-ceiling-spent-alpha" ] && ok "the spent marker is keyed by session id, so another session cannot overwrite it" || bad "no per-session spent marker: $(ls "$REPO/.harness/" | tr '\n' ' ')"
OUT=$(printf '{"transcript_path":"%s","session_id":"alpha","cwd":"%s"}' "$OVER" "$REPO" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && ok "alpha's SECOND stop stands down (spent)" || bad "alpha re-blocked: $OUT"
OUT=$(printf '{"transcript_path":"%s","session_id":"beta","cwd":"%s"}' "$OVER" "$REPO" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
echo "$OUT" | jq -e '.reason | test("CONTEXT CEILING")' >/dev/null 2>&1 && ok "session beta still gets ITS block (spent-ness is per session)" || bad "beta inherited alpha's spent state: $OUT"
# INTERLEAVED, which is the order a single shared file loses on: beta's block must not clear
# alpha's spent-ness. With the id in the file's CONTENTS, beta's write overwrote alpha's and
# alpha was blocked a second time (pass-1 codex P2); with the id in the NAME it cannot.
OUT=$(printf '{"transcript_path":"%s","session_id":"alpha","cwd":"%s"}' "$OVER" "$REPO" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && ok "alpha stays spent after beta's block (interleaved stops)" || bad "beta's block un-spent alpha — one session's ceiling reached another: $OUT"
[ ! -f "$REPO/.harness/.loop-halt" ] && ok "the attended arm never raises the lane-wide halt marker" || bad "close-out raised .loop-halt — a concurrent run would stand down"
rm -f "$REPO/.harness/.loop-iter" "$REPO/.harness"/.loop-ceiling-spent-*

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

# 8f) The timeout bound, witnessed by an actual hang (pass-2 witness lens P1: nothing
#     exercised it, so deleting `hook_bounded` left the suite green). A FIFO with no writer
#     blocks `open()` forever, which is the real shape of the hazard — a transcript the hook
#     cannot finish reading. The whole hook runs under an OUTER `timeout` so that removing
#     the bound fails the assert fast instead of hanging the suite.
rm -f "$REPO/.harness/.loop-iter" "$REPO/.harness"/.loop-ceiling-spent-*
: > "$HARNESS_LOOP_STATUS_PATH"
FIFO="$REPO/hang.jsonl"; rm -f "$FIFO"; mkfifo "$FIFO"
# The OUTER guard is hook_bounded, not raw `timeout`: stock macOS ships neither `timeout`
# nor `gtimeout` (lib.sh documents exactly this, which is why hook_bounded carries a
# pure-bash fallback). Calling the binary directly would exit 127 there and be read as a
# successful non-timeout — the assert passing for the wrong reason (pass-1 codex P3).
HANG_START=$SECONDS
OUT=$(printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$FIFO" "$REPO" \
  | HARNESS_LOOP=1 HARNESS_LOOP_CEILING_TIMEOUT=1 MEMENTO_ROOT="$REPO/no-such-memento" \
    CLAUDE_PROJECT_DIR="$REPO" hook_bounded 20 bash "$HOOK")
HANG_ELAPSED=$(( SECONDS - HANG_START ))
[ "$HANG_ELAPSED" -lt 15 ] && ok "an unreadable-forever transcript is cut off by the bound, not left to hang" || bad "the ceiling read hung past the bound (outer guard fired after ${HANG_ELAPSED}s)"
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "a timed-out reading still lets the loop continue" || bad "timeout stranded the loop: $OUT"
grep -q 'context ceiling unreadable' "$HARNESS_LOOP_STATUS_PATH" && ok "the timed-out reading is RECORDED as unmeasured" || bad "timeout left no ledger row: $(cat "$HARNESS_LOOP_STATUS_PATH")"
rm -f "$FIFO" "$REPO/.harness/.loop-iter"

# 8g) The counter re-read before the increment (pass-2 witness lens P1: unwitnessed, because
#     nothing wrote .loop-iter between step 3's read and step 5's write). The FIFO holds the
#     hook INSIDE the ceiling step while this test plays the concurrent session and bumps the
#     counter; the hook must then increment what it finds NOW (7 -> 8), not the 0 it read
#     before. Without the re-read it writes 1 and clobbers the other session's turn.
: > "$HARNESS_LOOP_STATUS_PATH"
FIFO="$REPO/slow.jsonl"; rm -f "$FIFO"; mkfifo "$FIFO"
rm -f "$REPO/.harness/.loop-iter"
( printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$FIFO" "$REPO" \
  | HARNESS_LOOP=1 HARNESS_LOOP_CEILING_TIMEOUT=20 MEMENTO_ROOT="$REPO/no-such-memento" \
    CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" > "$REPO/slow.out" ) &
SLOW_PID=$!
# The hook is now blocked opening the FIFO, which is exactly the window step 3's read and
# step 5's write straddle. Another session lands its own turn in that window.
sleep 1
printf '7' > "$REPO/.harness/.loop-iter"
# Unblocks the reader. A FIFO is not seekable, so the reader then fails rather than
# returning `under` — which is fine and is the point: BOTH the unreadable arm and the
# `under` arm fall through to step 5, where the re-read lives. What the FIFO buys is the
# HOLD, which is the only way to open the window at all.
# Bounded: if the hook exited before opening the FIFO (a slow runner reaching the cap at
# step 3 first), an unbounded write to a reader-less FIFO would block forever and hang CI
# instead of failing an assert (pass-2 codex P2).
usage_record 1000 | hook_bounded 15 dd of="$FIFO" 2>/dev/null
wait "$SLOW_PID" 2>/dev/null
[ "$(cat "$REPO/.harness/.loop-iter")" = "8" ] && ok "the continue arm increments the counter it re-reads (7 -> 8), not the stale one" || bad "stale counter written: $(cat "$REPO/.harness/.loop-iter" 2>/dev/null) (expected 8)"
rm -f "$FIFO" "$REPO/slow.out" "$REPO/.harness/.loop-iter"

# 8h) The cap re-check against the FRESH counter (pass-1 concurrency P2 / codex P2). Step 3
#     decides the cap on a value read BEFORE the ceiling subprocess; a concurrent Stop can
#     reach MAX inside that window. Same FIFO fixture as 8g: the hook is blocked mid-step-4
#     while this test plays the other session and drives the counter to the cap. The hook must
#     then stand down, not block a turn its stale authorisation no longer covers.
: > "$HARNESS_LOOP_STATUS_PATH"
FIFO="$REPO/cap.jsonl"; rm -f "$FIFO"; mkfifo "$FIFO"
printf '0' > "$REPO/.harness/.loop-iter"
( printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$FIFO" "$REPO" \
  | HARNESS_LOOP=1 HARNESS_LOOP_MAX=5 HARNESS_LOOP_CEILING_TIMEOUT=20 \
    MEMENTO_ROOT="$REPO/no-such-memento" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" > "$REPO/cap.out" ) &
CAP_PID=$!
sleep 1
printf '5' > "$REPO/.harness/.loop-iter"     # the other session reaches the cap meanwhile
# Unblocks the reader; as in 8g the FIFO is unseekable so step 4 ends in the unreadable arm,
# which falls through to step 5 exactly as a normal `under` reading would. Without the
# re-check, step 5 blocks a turn on step 3's stale `0 < 5`.
# Bounded: if the hook exited before opening the FIFO (a slow runner reaching the cap at
# step 3 first), an unbounded write to a reader-less FIFO would block forever and hang CI
# instead of failing an assert (pass-2 codex P2).
usage_record 1000 | hook_bounded 15 dd of="$FIFO" 2>/dev/null
wait "$CAP_PID" 2>/dev/null
[ ! -s "$REPO/cap.out" ] && ok "a cap reached during the ceiling read stands the turn down" || bad "blocked past the cap on a stale authorisation: $(cat "$REPO/cap.out")"
grep -q 'iteration cap 5 reached while measuring the ceiling' "$HARNESS_LOOP_STATUS_PATH" && ok "the mid-ceiling cap stand-down is logged as such" || bad "mid-ceiling cap not logged: $(cat "$HARNESS_LOOP_STATUS_PATH")"
rm -f "$FIFO" "$REPO/cap.out" "$REPO/.harness/.loop-iter" "$REPO/.harness/.loop-halt"

# 8i) A payload with NO session id still gets a BOUNDED close-out. An earlier revision wrote
#     no marker at all for this case, to avoid two id-less sessions sharing one; codex pass 2
#     showed that trades a collision for something worse — the session is then re-blocked
#     every turn until the lane cap. The bound wins: the marker is written at the bare path,
#     so an id-less session is blocked once like any other. The residual collision between
#     TWO id-less sessions is registered as B-302 item (6) rather than traded away again.
rm -f "$REPO/.harness"/.loop-ceiling-spent-* "$REPO/.harness/.loop-iter"
OUT=$(printf '{"transcript_path":"%s","cwd":"%s"}' "$OVER" "$REPO" | HARNESS_LOOP=1 MEMENTO_ROOT="$REPO/no-such-memento" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
echo "$OUT" | jq -e '.reason | test("CONTEXT CEILING")' >/dev/null 2>&1 && ok "a session with no id still gets its close-out block" || bad "no-id session lost its block: $OUT"
OUT=$(printf '{"transcript_path":"%s","cwd":"%s"}' "$OVER" "$REPO" | HARNESS_LOOP=1 MEMENTO_ROOT="$REPO/no-such-memento" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && ok "a session with no id is bounded too (blocked once, not every turn to the cap)" || bad "no-id session re-blocked: $OUT"
rm -f "$REPO/.harness/.loop-iter" "$REPO/.harness"/.loop-ceiling-spent-*

# NOT WITNESSED, and said plainly rather than faked: that the cap also covers the CLOSE-OUT
# arm. Staging it needs the counter to reach MAX *during* step 4 AND the verdict to be
# close-out — but the only way to hold the hook inside step 4 is the unseekable FIFO above,
# which always ends in the unreadable arm. A first attempt at this case set ITER=MAX up front
# and passed with the cap re-check deleted, because step 3 stood the session down before step
# 4 ever ran; it was removed rather than shipped green. What carries the property instead is
# structure, not a test: the read, the cap check and the increment are straight-line code
# ahead of the close-out emission, on the single path every continuing arm converges to, so
# the arm cannot reach its block without passing the check. 8h pins that the check exists and
# fires; the ordering is visible in the file. B-302 item (7) carries the gap.

# 9) The reading itself (context_tokens.py), driven in the consumer's exact invocation. The
#    transcript scan reads backwards in 256 KB chunks, so the cases that can only go wrong
#    there — a record straddling a chunk boundary, a torn final line, a subagent's sidechain
#    — are witnessed here rather than inferred from the end-to-end arms above.
export READER="$SCRIPT_DIR/context_tokens.py"
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

# A malformed LAST record in a file that ENDS IN A NEWLINE is complete, so it is corruption
# rather than an append caught mid-write. Tolerating it would skip the newest record and read
# the older 900000 one instead (pass-1 codex P2).
SEALED="$REPO/sealed.jsonl"
{ usage_record 900000; printf '{"type":"assistant","message":{"usa\n'; } > "$SEALED"
read_verdict "$SEALED" >/dev/null 2>&1 && bad "a complete-but-malformed final record was tolerated" || ok "a malformed final record in a newline-terminated file fails loudly"

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
#     hand against a real `claude plugin install memento@memento` of promptctl/memento@0d1f5bc:
#     with a session layer of `ceiling = 400000` the reading of 300,000 came back `under` at a
#     ceiling of 400,000, where the same payload with memento absent came back `close-out` at
#     250,000. The two numbers differ, which is what makes that a control rather than a
#     coincidence.
#
#     `shared_unrecorded` and not `shared_at_start`: the two resolve the same ceiling and
#     differ only in that the second WRITES the session's shared-at-start record, which
#     memento's own Stop hook owns (ceiling_config.py:294-305). Checked by hand the same way —
#     the record was deleted, the reading re-run, the ceiling came back unchanged at 400,000
#     and the file was not recreated.
#
#     The asserts here pin MEMENTO_ROOT, so they do not reach the discovery a real session
#     uses. That is its own section below, and it is where the arm that matters lives.
export FAKE="$REPO/memento"
mkdir -p "$FAKE/lib" "$FAKE/skills/message-in-a-bottle/bin"
cat > "$FAKE/lib/ceiling_config.py" <<'PY'
"""Stands in for memento's ceiling_config: the names tools/hooks/context_tokens.py imports.

Both readers are defined, and they differ the way the real ones do: shared_at_start WRITES
the session's record and shared_unrecorded does not. That difference is the point. While
this fixture carried only the name the code calls, reverting the call site failed as an
ImportError -- a symbol-presence pin, green for any pair of names renamed in lockstep and
blind to the property the change was made for. Now the revert is observable as a file
appearing where none should. (merge-gate witness lens, pass 1)
"""
import os, pathlib
SHARED_AT_START = "shared-at-start.conf"
WROTE = pathlib.Path(os.environ["FIXTURE_WRITE_MARKER"])
def anchored(fallback): return fallback
def session_directory(session_id): return pathlib.Path("/tmp") / session_id
def shared_at_start(path, anchor):
    WROTE.write_text("shared_at_start wrote the session record\n")
    return ("shared", anchor)
def shared_unrecorded(path, anchor): return ("shared", anchor)
def in_force(directory, shared): return 400_000
PY
export FIXTURE="$FAKE/lib/ceiling_config.py"
: > "$FAKE/skills/message-in-a-bottle/bin/finalize-session"
MARKER="$REPO/shared-at-start-was-written"
fake_verdict() { printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$1" "$REPO" \
  | MEMENTO_ROOT="$FAKE" FIXTURE_WRITE_MARKER="$MARKER" /usr/bin/python3 "$READER"; }

V=$(fake_verdict "$OVER")
[ "$(echo "$V" | jq -r .ceiling)" = "400000" ] && ok "memento present → its ceiling wins over the default" || bad "memento ceiling ignored: $V"
[ "$(echo "$V" | jq -r .verdict)" = "under" ] && ok "a reading over 250,000 is under a memento ceiling of 400,000" || bad "memento ceiling not applied to the verdict: $V"
echo "$V" | jq -r .close_out | grep -q "finalize-session --reset compact" && ok "memento present → the close-out is its launcher" || bad "close-out ignored the installed launcher: $V"

# --headless is what separates the two over-ceiling arms, and nothing else does.
[ "$(printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$OVER" "$REPO" | MEMENTO_ROOT="$REPO/nope" /usr/bin/python3 "$READER" --headless | jq -r .verdict)" = "relaunch" ] \
  && ok "--headless selects relaunch over close-out" || bad "--headless did not change the verdict"

# 11) Finding memento, which is the arm the asserts above pin away. An install path carries
#     a version segment the plugin name does not name (`.../cache/memento/memento/0.7.0`), so
#     the path cannot be spelled as a constant — and the revision that spelled one out landed
#     green, because MEMENTO_ROOT was pinned in the tests and by hand in the controls. A
#     real install changed nothing: the constant named a directory OF version directories,
#     `lib/ceiling_config.py` was not under it, and memento read as absent forever. So these
#     asserts run with MEMENTO_ROOT UNSET, against Claude Code's own installed_plugins.json,
#     which is where that path is actually decided.
# A fixture HOME, separate from the fixture project, so the user and project enablement
# layers are distinguishable AND hermetic: USER_SETTINGS takes no env override, so an
# unpinned HOME would read the operator's real ~/.claude/settings.json and the suite
# would pass or fail by machine state.
FHOME="$REPO/home"; mkdir -p "$FHOME/.claude/plugins" "$REPO/.claude"
enable_at() { printf '{"enabledPlugins":{"memento@memento":%s}}' "$2" > "$1"; }
PROJECT_SETTINGS="$REPO/.claude/settings.json"
USER_SETTINGS_F="$FHOME/.claude/settings.json"
enable_at "$PROJECT_SETTINGS" true
MANIFEST="$REPO/installed_plugins.json"
# `env -u` and not a subshell unset: MEMENTO_ROOT is exported at the top of this file for
# every other section, and it must stay exported for them.
found_verdict() { printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$OVER" "$REPO" \
  | env -u MEMENTO_ROOT HOME="$FHOME" FIXTURE_WRITE_MARKER="$MARKER" \
      HARNESS_PLUGIN_MANIFEST="$1" /usr/bin/python3 "$READER"; }

manifest_naming() { python3 -c "
import json, sys
json.dump({'plugins': {'memento@memento': [
    {'installPath': p, 'installedAt': t} for p, t in zip(sys.argv[2::2], sys.argv[3::2])]}},
    open(sys.argv[1], 'w'))
" "$MANIFEST" "$@"; }

manifest_naming "$FAKE" "2026-09-20T02:04:51.189Z"
V=$(found_verdict "$MANIFEST")
[ "$(echo "$V" | jq -r .ceiling)" = "400000" ] && ok "the manifest's installPath is found with MEMENTO_ROOT unset" || bad "discovery missed the installed plugin: $V"
echo "$V" | jq -r .close_out | grep -q "finalize-session --reset compact" && ok "a discovered install supplies the launcher too" || bad "discovered install gave no launcher: $V"

# A manifest that is not there at all is memento not installed, which is a legal value.
V=$(found_verdict "$REPO/no-such-manifest.json")
[ "$(echo "$V" | jq -r .ceiling)" = "250000" ] && ok "no manifest → the default ceiling" || bad "invented a ceiling with no manifest: $V"
echo "$V" | jq -r .close_out | grep -q "context-save-lean" && ok "no manifest → the workspace close-out" || bad "claimed a launcher with no manifest: $V"

# The manifest exists and names other plugins but not this one — the ordinary shape on a
# machine that has never installed memento, and distinct from having no manifest at all.
printf '{"version":1,"plugins":{"something-else@elsewhere":[{"installPath":"/x"}]}}' > "$REPO/other-plugins.json"
[ "$(found_verdict "$REPO/other-plugins.json" | jq -r .ceiling)" = "250000" ] && ok "a manifest without memento reads as not installed" || bad "a foreign manifest entry was taken for memento: $(found_verdict "$REPO/other-plugins.json")"

# A record carrying neither field. Both are read with .get, so the failure to design for
# would be a KeyError out of the search — the reading lost to a record that names nothing.
printf '{"plugins":{"memento@memento":[{"scope":"project"}]}}' > "$REPO/fieldless.json"
[ "$(found_verdict "$REPO/fieldless.json" | jq -r .ceiling)" = "250000" ] && ok "a record with no installPath is skipped, not fatal" || bad "a fieldless record broke the search: $(found_verdict "$REPO/fieldless.json" 2>&1)"

# The same, mixed with a good record: the fieldless one must not displace it, and an absent
# installedAt must not sort ABOVE a real one under newest-first.
manifest_naming "$FAKE" "2026-09-20T02:04:51.189Z"
python3 -c "
import json, sys
d = json.load(open(sys.argv[1])); d['plugins']['memento@memento'].insert(0, {'scope': 'user'})
json.dump(d, open(sys.argv[1], 'w'))
" "$MANIFEST"
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "400000" ] && ok "a fieldless record does not displace a good one" || bad "a fieldless record shadowed the install: $(found_verdict "$MANIFEST" 2>&1)"

# The manifest holds one record per install, so a plugin installed at two scopes or upgraded
# in place has several. Both of the next two asserts need a SECOND fixture that also stands
# and states a DIFFERENT ceiling: with only one standing path, ordering and the existence
# filter are both unobservable — whichever way either goes, the single good path is the
# answer. Two probes proved exactly that before this fixture existed.
export FAKE2="$REPO/memento-newer"
mkdir -p "$FAKE2/lib" "$FAKE2/skills/message-in-a-bottle/bin"
sed 's/400_000/500_000/' "$FAKE/lib/ceiling_config.py" > "$FAKE2/lib/ceiling_config.py"
: > "$FAKE2/skills/message-in-a-bottle/bin/finalize-session"

# Two installs that both stand: the newest answers, and 500,000 is only reachable through it.
manifest_naming "$FAKE2" "2026-09-21T00:00:00.000Z" "$FAKE" "2026-09-20T02:04:51.189Z"
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "500000" ] && ok "the newest of two standing installs answers" || bad "record ordering ignored: $(found_verdict "$MANIFEST")"

# The newest record no longer stands — an uninstall, or a pruned cache. That is not a failure
# and not the end of the search: the older install that IS there is the answer. Without the
# existence check the stale path is taken and nothing below it is ever reached.
manifest_naming "$REPO/gone-away" "2026-09-21T00:00:00.000Z" "$FAKE" "2026-09-20T02:04:51.189Z"
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "400000" ] && ok "a newest record that no longer stands is skipped for one that does" || bad "a stale manifest path stopped the search: $(found_verdict "$MANIFEST")"

# A manifest that exists and does not parse is a genuine failure. Reporting the default here
# would be a session reading as comfortably under a ceiling nobody could resolve.
printf 'not json at all' > "$REPO/broken-manifest.json"
found_verdict "$REPO/broken-manifest.json" >/dev/null 2>&1 \
  && bad "a corrupt manifest was swallowed and a ceiling reported anyway" \
  || ok "a corrupt manifest exits non-zero rather than reporting a ceiling"


# 11b) The manifest's own DEFAULT path. Every assert above pins HARNESS_PLUGIN_MANIFEST, so
#      the literal a real session actually resolves -- $HOME/.claude/plugins/installed_plugins.json
#      -- was written by hand and read by nothing. That is this arc's own bug one layer down:
#      a wrong segment in that literal makes is_file() false forever and every real session
#      degrades silently to "memento not installed", with the suite still green. So this
#      assert sets HOME and leaves BOTH overrides off, which is the only way the default is
#      reached. (merge-gate witness lens, pass 1)
mkdir -p "$FHOME/.claude/plugins"
manifest_naming "$FAKE" "2026-09-20T02:04:51.189Z"
cp "$MANIFEST" "$FHOME/.claude/plugins/installed_plugins.json"
DEFAULTED=$(printf '{"transcript_path":"%s","session_id":"s1","cwd":"%s"}' "$OVER" "$REPO" \
  | env -u MEMENTO_ROOT -u HARNESS_PLUGIN_MANIFEST HOME="$FHOME" FIXTURE_WRITE_MARKER="$MARKER" \
      /usr/bin/python3 "$READER")
[ "$(echo "$DEFAULTED" | jq -r .ceiling)" = "400000" ] && ok "the manifest's default path is the one a real session resolves" || bad "the hand-written default path does not resolve: $DEFAULTED"
rm -f "$FHOME/.claude/plugins/installed_plugins.json"

# 11c) Enablement. The manifest says what is INSTALLED on this machine; it does not say what
#      runs in this project, and an install made from another workspace still has a standing
#      installPath in the shared cache. `enabledPlugins` is what Claude Code actually reports
#      as `Status: enabled`. The record's own projectPath is NOT usable for this: this repo's
#      lanes run at SIBLING paths, so a path test would read as "not installed" in every lane.
#      (codex pass 1)
manifest_naming "$FAKE" "2026-09-20T02:04:51.189Z"
rm -f "$PROJECT_SETTINGS" "$USER_SETTINGS_F"
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "250000" ] && ok "installed but enabled nowhere → not memento" || bad "an unenabled install was used: $(found_verdict "$MANIFEST")"

enable_at "$PROJECT_SETTINGS" false
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "250000" ] && ok "an explicit false disables it" || bad "an explicit false was ignored: $(found_verdict "$MANIFEST")"

# The user layer enables it on its own, which is what makes the fixture HOME load-bearing
# rather than decoration: read the operator's real settings here and the result is machine
# state, not a test.
rm -f "$PROJECT_SETTINGS"
enable_at "$USER_SETTINGS_F" true
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "400000" ] && ok "the user layer enables it with no project layer" || bad "user-layer enablement missed: $(found_verdict "$MANIFEST")"

# Both layers, disagreeing, BOTH WAYS ROUND. The precedence is Claude Code's own, probed
# rather than assumed (2026-09-19, `claude plugin list` under a synthetic HOME with
# deliberately disagreeing layers): the FIRST layer that mentions the plugin decides, in the
# order local, project, user -- the CLI even states it, "project settings enable it, which
# overrides your user setting". The second of these two asserts is the one that matters: it
# is the ONLY case separating that rule from the any-false-disables rule shipped at
# 746c20f0, under which a stale user-level false read as disabled HERE, where Claude Code
# loads the plugin. The first direction passes under both rules and discriminates nothing on
# its own. (codex, pass 2)
enable_at "$PROJECT_SETTINGS" false; enable_at "$USER_SETTINGS_F" true
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "250000" ] && ok "a project false beats a user true" || bad "project-over-user precedence missed: $(found_verdict "$MANIFEST")"

enable_at "$PROJECT_SETTINGS" true; enable_at "$USER_SETTINGS_F" false
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "400000" ] && ok "a project true beats a user false — a stale user-level false does not disable it here" || bad "a user-level false wrongly disabled an enabled project: $(found_verdict "$MANIFEST")"

# The LOCAL layer, which the precedence fix makes the highest of the three and which no
# assert reached until now. It is not hypothetical: .claude/settings.local.json is a real,
# live, gitignored file in this repo. (merge-gate witness lens, pass 2)
LOCAL_SETTINGS="$REPO/.claude/settings.local.json"
enable_at "$LOCAL_SETTINGS" false; enable_at "$PROJECT_SETTINGS" true; rm -f "$USER_SETTINGS_F"
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "250000" ] && ok "a local false beats a project true" || bad "the local layer was not read: $(found_verdict "$MANIFEST")"

enable_at "$LOCAL_SETTINGS" true; enable_at "$PROJECT_SETTINGS" false
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "400000" ] && ok "a local true beats a project false" || bad "local-over-project precedence missed: $(found_verdict "$MANIFEST")"
rm -f "$LOCAL_SETTINGS"
enable_at "$PROJECT_SETTINGS" true; rm -f "$USER_SETTINGS_F"

# 11c-2) WHICH record answers, once enablement has said yes. The manifest holds one record
#        per install, so an upgrade made from another workspace sits beside this project's
#        own with a newer installedAt and a DIFFERENT version's installPath. Newest-wins
#        alone would hand this session that other workspace's version. (codex, pass 2)
record_naming() { python3 -c "
import json, sys
json.dump({'plugins': {'memento@memento': [
    {'installPath': p, 'installedAt': t, 'scope': sc, 'projectPath': pp}
    for p, t, sc, pp in zip(sys.argv[2::4], sys.argv[3::4], sys.argv[4::4], sys.argv[5::4])]}},
    open(sys.argv[1], 'w'))
" "$MANIFEST" "$@"; }

# A NEWER record bound to some other workspace, beside an OLDER one bound to this project.
# This project's own record answers, so the ceiling is 400,000 and not the newer 500,000.
record_naming "$FAKE2" "2026-09-21T00:00:00.000Z" project /somewhere/else \
              "$FAKE"  "2026-09-20T02:04:51.189Z" project "$REPO"
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "400000" ] && ok "this project's own record beats a newer one bound elsewhere" || bad "another workspace's install displaced this project's: $(found_verdict "$MANIFEST")"

# A user-scope record applies everywhere, so it is bound here even with no projectPath match.
record_naming "$FAKE2" "2026-09-21T00:00:00.000Z" user "" \
              "$FAKE"  "2026-09-20T02:04:51.189Z" project "$REPO"
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "500000" ] && ok "a newer user-scope record applies here too" || bad "a user-scope record was treated as foreign: $(found_verdict "$MANIFEST")"

# NOTHING bound here -- the lane shape, since a lane runs at a sibling path and matches no
# record. The set must NOT be filtered to empty: falling back to the newest standing install
# is what keeps the ceiling alive in a lane, and reading as "not installed" there is the
# failure this whole arc exists to remove.
record_naming "$FAKE2" "2026-09-21T00:00:00.000Z" project /somewhere/else \
              "$FAKE"  "2026-09-20T02:04:51.189Z" project /elsewhere/again
[ "$(found_verdict "$MANIFEST" | jq -r .ceiling)" = "500000" ] && ok "no record bound here → the newest standing install, not nothing" || bad "an unbound set was filtered to empty (the lane failure): $(found_verdict "$MANIFEST")"
manifest_naming "$FAKE" "2026-09-20T02:04:51.189Z"

# 11d) The reader writes no session record. `shared_at_start` and `shared_unrecorded` resolve
#      the same ceiling and differ only in that the first WRITES; memento's own Stop hook owns
#      that write. Asserting the ceiling cannot see the difference, so the fixture's
#      shared_at_start leaves a marker and this asserts the marker is absent -- a revert of
#      the call site then reds on the property, not on a symbol name.
#      Positive control first: the marker mechanism has to be able to fire, or "absent" proves
#      only that nothing was ever watching.
CONTROL=$(FIXTURE_WRITE_MARKER="$MARKER" /usr/bin/python3 -c "
import importlib.util, os, pathlib
spec = importlib.util.spec_from_file_location('c', os.environ['FIXTURE'])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.shared_at_start(pathlib.Path('/tmp/x'), '/tmp')
print(pathlib.Path(os.environ['FIXTURE_WRITE_MARKER']).is_file())
" 2>&1)
[ "$CONTROL" = "True" ] && ok "positive control: the fixture's shared_at_start does leave a marker" || bad "the marker mechanism cannot fire, so its absence proves nothing: $CONTROL"
rm -f "$MARKER"

fake_verdict "$OVER" >/dev/null
[ ! -f "$MARKER" ] && ok "resolving the ceiling writes no session record" || bad "the reader wrote the record memento's hook owns"

# 11e) Two roots in ONE process. Every other assert here is its own subprocess, so none of
#      them can see how the ceiling_config module is loaded -- and `from ceiling_config import`
#      caches by module NAME, so a second call with a different root would silently be served
#      the first root's module. That was harmless while the root was a frozen constant and
#      stopped being harmless when memento_root() made it vary. This is the only shape that
#      observes it: resolve twice, two roots, two different ceilings.
#      (merge-gate concurrency lens, pass 1)
ISOLATION=$(FIXTURE_WRITE_MARKER="$MARKER" /usr/bin/python3 -c "
import importlib.util, os, pathlib, sys
spec = importlib.util.spec_from_file_location('ct', os.environ['READER'])
ct = importlib.util.module_from_spec(spec); spec.loader.exec_module(ct)
first = ct.resolve_ceiling(pathlib.Path(os.environ['FAKE']), 's1', os.environ['REPO'])
second = ct.resolve_ceiling(pathlib.Path(os.environ['FAKE2']), 's1', os.environ['REPO'])
print(first, second, 'ceiling_config' in sys.modules)
" 2>&1)
[ "$ISOLATION" = "400000 500000 False" ] && ok "two roots in one process resolve to their own ceilings, and neither is cached by name" || bad "the second root was served the first root's module: $ISOLATION"

echo "----"
echo "stop_loop: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

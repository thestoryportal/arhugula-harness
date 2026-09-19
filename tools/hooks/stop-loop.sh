#!/usr/bin/env bash
# In-session Stop-continue loop (U-HK-14). Stop matcher "*".
#
# In loop mode, keeps the roadmap arc going across turns without an operator round-trip:
# at turn end it injects the next-action and `decision:block`s to continue. It STOPS
# (allows the turn to end) only at a TRUE stand-down or a bound:
#   - INERT unless loop mode on (exit 0).
#   - HALT MARKER (.harness/.loop-halt) present → a TRUE stand-down was signalled. Three
#     things raise it: the forward menu is exhausted (every forward item deferred) or the
#     operator stopped it (both written from outside this hook), the iteration cap below,
#     and the context ceiling's attended arm. A single gated item does NOT raise it — it is
#     deferred + worked around (see below).
#   - ITERATION CAP (HARNESS_LOOP_MAX, default 25) → hard bound on auto-continued turns
#     (the claudefa.st turn-counter guard); log + reset + allow stop.
#   - CONTEXT CEILING (U-HE-58) → headless, allow the stop and let the runner relaunch;
#     attended, block ONCE for the close-out and raise the halt marker.
#   - otherwise → increment the counter + block with the next-action + the run-scoped
#     SKIP-SET so the loop ADVANCES past already-deferred items (never re-attempts one).
#
# Design (operator-ratified): on a gated item (paid call / secret / vendor / missing cred /
# infra) the loop builds whatever slice does NOT need the gated input, logs a clearly-stated
# DEFERRED-HIL row via `loop_defer <item-id> ...`, and ADVANCES to the next forward item —
# it does NOT halt the whole run. The persistent ledger's DEFERRED-HIL rows are the
# cross-turn/cross-headless-child skip-set (loop_skip_set); injecting it is the mechanical
# guard against a fresh `claude -p` re-attempting the same gated item off the static
# dashboard pointer. `.loop-halt` is raised ONLY when EVERY forward item is deferred.
#
# Composition: runs on Stop alongside U-HK-10 stop-gate (lint) + U-HK-16 git-arc-guard.
# All Stop hooks run; if any blocks, the turn continues — so the lint gate's block is
# addressed in the same continued turn before this loop's next-action is acted on.
#
# Bounding is the iteration COUNTER (a genuine hard cap), not stop_hook_active alone —
# a sustained loop must survive past the first continuation, which stop_hook_active
# would forbid. The cap guarantees termination regardless.
#
# Trigger: Stop "*". Test: tools/hooks/test_stop_loop.sh.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"
hook_review_isolated && exit 0
# shellcheck source=loop_lib.sh
. "$(dirname "${BASH_SOURCE[0]}")/loop_lib.sh"

# The Stop payload, read once. Only the ceiling reading (step 4) consumes it, but stdin is
# a stream with one reader, so it is taken here rather than mid-script where an added caller
# above would silently starve it.
PAYLOAD=$(hook_read_stdin)

# 1) INERT unless loop mode on.
loop_mode_active || exit 0

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

HALT=$(loop_halt_path)
ITERF=$(loop_iter_path)
MAX=${HARNESS_LOOP_MAX:-25}
# Validate the cap: a non-numeric HARNESS_LOOP_MAX would make the `-ge` test below error
# out (→ false), so the loop would never hit the cap. Fall back to the safe default.
[[ "$MAX" =~ ^[0-9]+$ ]] || MAX=25

# 2) Genuine-gate halt marker → stand down. LEAVE the marker in place: under the headless
#    runner (U-HK-15), .loop-halt is created inside a `claude -p` child and the OUTER
#    runner only observes it at its next iteration top. If this in-session hook deleted
#    it, the runner would never see the gate and would keep launching sessions. The
#    runner (or /loop-stop / the next /loop-start) clears it; here we only reset the
#    turn counter and allow the stop.
if [ -n "$HALT" ] && [ -f "$HALT" ]; then
  loop_log STOP "halt marker present — standing down at a genuine gate (marker left for the runner)"
  rm -f "$ITERF" 2>/dev/null
  exit 0
fi

# 3) Iteration cap → hard bound reached, stop.
ITER=$(cat "$ITERF" 2>/dev/null || echo 0)
[[ "$ITER" =~ ^[0-9]+$ ]] || ITER=0
if [ "$ITER" -ge "$MAX" ]; then
  loop_log STOP "iteration cap ${MAX} reached — loop stopping (run /loop-start to resume)"
  # Raise the halt marker so the cap is a REAL boundary: without it the next Stop would
  # start a fresh counter (marker-based mode) and the headless runner, seeing no halt,
  # would launch another claude -p. The halt makes both stand down. /loop-start clears it.
  [ -n "$HALT" ] && : > "$HALT" 2>/dev/null
  rm -f "$ITERF" 2>/dev/null
  exit 0
fi

NEXT=$(hook_roadmap_next "$PROJECT_DIR/.harness/roadmap_status.md")
NEXT=${NEXT:-"(derive per CLAUDE.md §4 from the dashboard)"}

# 4) Context ceiling (U-HE-58, plan §9 B4 / decision 7). memento's own ceiling hook stands
#    down whenever stop_hook_active is set (context-ceiling.py:220), and every continued loop
#    turn sets it — so inside loop mode the ceiling has no enforcer but this one. The reading
#    and the ceiling come back from context_tokens.py as a single stamped verdict; nothing is
#    re-derived here.
# Bounded like every other shell-out in this family: the transcript it scans is being
# appended to by the live session, and an attended session has no outer bound of its own, so
# an unbounded read here would hang the turn with no recovery. Exceeding the bound is a
# non-zero exit, which lands in the loud arm below.
#
# 6s is not invented: it is the bound loop_lib.sh already uses for its own shell-outs
# (`hook_bounded 6 gh pr list`, loop_lib.sh:803 and :819), and those are NETWORK calls. This
# one is a local file read, measured at 0.03s against the largest real transcript on this
# machine, so the family's existing constant is already ~200x the observed cost.
if ! VERDICT_JSON=$(printf '%s' "$PAYLOAD" \
  | hook_bounded "${HARNESS_LOOP_CEILING_TIMEOUT:-6}" \
      /usr/bin/python3 "$(dirname "${BASH_SOURCE[0]}")/context_tokens.py" \
      ${HARNESS_LOOP_HEADLESS:+--headless} 2>&1); then
  # The ceiling is instrumentation over the loop, not a gate the loop may not run without,
  # so a broken reading does not strand the run — but it is never swallowed either: the
  # ledger is where the difference between "under the ceiling" and "never measured" lives.
  loop_log STOP "context ceiling unreadable — continuing unmeasured: ${VERDICT_JSON}"
else
  VERDICT=$(printf '%s' "$VERDICT_JSON" | jq -r '.verdict')
  TOKENS=$(printf '%s' "$VERDICT_JSON" | jq -r '.tokens')
  CEILING=$(printf '%s' "$VERDICT_JSON" | jq -r '.ceiling')
  case "$VERDICT" in
    relaunch)
      # Headless: tools/04-loop/run.sh starts the next iteration itself, and blocking here
      # would put a second session on one worktree. The counter is the RUN's, so it stands.
      loop_log STOP "context ceiling ${TOKENS}/${CEILING} — headless, allowing the stop so the runner relaunches"
      exit 0
      ;;
    close-out)
      # Attended: nothing will relaunch this session, so it is told to close out. The halt
      # marker is what bounds it to ONE such block — the next Stop stands down at step 2
      # rather than spending more context on the problem that IS too much context. Context
      # exhaustion is a genuine stand-down, which is the condition that marker already means.
      # Blocked once, never twice — but the "once" is per SESSION, not per lane. The halt
      # marker would have been the obvious bound and is the wrong one: it is per-worktree
      # (loop_halt_path reads only the project dir), every writer of it so far meant a
      # RUN-wide stand-down, and being over the ceiling is a fact about one session's own
      # transcript. An attended session opened beside a running `just loop` shares the lane,
      # so raising it there would stand the unrelated headless run down over a context
      # reading that says nothing about it. So the spent-ness is keyed by session id: this
      # file holds the id of the session last told to close out, and a session that does not
      # find its own id there gets its one block.
      SPENT="$PROJECT_DIR/.harness/.loop-ceiling-spent"
      SESSION=$(hook_json "$PAYLOAD" '.session_id')
      if [ -n "$SESSION" ] && [ "$(cat "$SPENT" 2>/dev/null)" = "$SESSION" ]; then
        loop_log STOP "context ceiling ${TOKENS}/${CEILING} — attended, close-out already asked of this session; allowing the stop"
        exit 0
      fi
      CLOSE_OUT=$(printf '%s' "$VERDICT_JSON" | jq -r '.close_out')
      loop_log STOP "context ceiling ${TOKENS}/${CEILING} — attended, blocking once for the close-out"
      printf '%s' "$SESSION" > "$SPENT" 2>/dev/null
      # A close-out block is a turn the loop spent, so it counts as one. That is also the
      # SECOND bound: the marker above is the primary one, but writing it is a best-effort
      # file write, and if it fails this arm would otherwise re-block every turn forever —
      # the counter carries the block to the cap regardless. Re-read immediately before the
      # write so the value written is not the one read back before the ceiling subprocess.
      ITER=$(cat "$ITERF" 2>/dev/null || echo 0); [[ "$ITER" =~ ^[0-9]+$ ]] || ITER=0
      ITER=$((ITER + 1)); printf '%s' "$ITER" > "$ITERF" 2>/dev/null
      jq -nc --arg r "[stop-loop] CONTEXT CEILING: this session is at ~${TOKENS} tokens, past the ${CEILING} ceiling, and no runner will relaunch it. Do not start new work.
1. Commit or push everything outstanding — a handoff across a reset loses whatever is not committed.
2. Close out: ${CLOSE_OUT}
The handoff is the only thing the next session wakes up with, so it says what you were doing, exactly where you stopped, and the next concrete step. The dashboard next-action to carry across is: ${NEXT}." '{"decision":"block","reason":$r}'
      exit 0
      ;;
  esac
fi

# 5) Continue: increment counter + inject next-action + the run-scoped skip-set.
# Re-read first: the counter is per-lane, and step 4's subprocess sits between the read at
# step 3 and this write, so incrementing the pre-ceiling value would drop a concurrent
# session's turn. (The cap DECISION at step 3 still rests on the earlier read; that window
# is pre-existing and is now bounded by step 4's timeout.)
ITER=$(cat "$ITERF" 2>/dev/null || echo 0); [[ "$ITER" =~ ^[0-9]+$ ]] || ITER=0
ITER=$((ITER + 1)); printf '%s' "$ITER" > "$ITERF" 2>/dev/null
SKIP=$(loop_skip_set)
SKIP=${SKIP:-none}

REASON="[stop-loop] autonomous loop continuing (turn ${ITER}/${MAX}). Dashboard next-action: ${NEXT}.
ALREADY DEFERRED this run — do NOT re-attempt these (build elsewhere): ${SKIP}.
Pick the highest-priority forward item per CLAUDE.md §12.4.1 that is NOT in the deferred set, and drive it: ground empirically → build the slice that does NOT need any gated input → tests → PR → CI-green → merge → fixed-point refresh (CLAUDE.md §12). Use /resolve for reversible in-repo forks.
If the item is GATED (needs a paid call / secret / vendor selection / missing credential / infra you cannot provide): do NOT force it and do NOT raise .loop-halt. Build whatever slice is possible WITHOUT the gated input, then record the deferral with the allowlisted wrapper — \`tools/04-loop/defer.sh <ITEM-ID> 'what operator input is needed (plain text, no shell metacharacters) — built without it: slice or none'\` — and ADVANCE to the next forward item. (Run it as a single command; do NOT chain it or source the libs yourself — the wrapper does that and is the only guard-allowed path.) The hard-stop deny-list still blocks the dangerous TOOL; this is the item-level disposition.
ONLY when EVERY forward item per §12.4.1 is already in the deferred set (no buildable slice remains anywhere) do you stand the run down with \`tools/04-loop/halt.sh 'forward menu exhausted — N items awaiting operator input'\`. Then the run ends for operator review."

jq -nc --arg r "$REASON" '{"decision":"block","reason":$r}'
exit 0

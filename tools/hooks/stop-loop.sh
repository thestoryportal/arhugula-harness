#!/usr/bin/env bash
# In-session Stop-continue loop (U-HK-14). Stop matcher "*".
#
# In loop mode, keeps the roadmap arc going across turns without an operator round-trip:
# at turn end it injects the next-action and `decision:block`s to continue. It STOPS
# (allows the turn to end) only at a TRUE stand-down or a bound:
#   - INERT unless loop mode on (exit 0).
#   - HALT MARKER (.harness/.loop-halt) present → a TRUE stand-down was signalled: the
#     forward menu is exhausted (every forward item deferred) OR the operator stopped it.
#     A single gated item does NOT raise this — it is deferred + worked around (see below).
#   - ITERATION CAP (HARNESS_LOOP_MAX, default 25) → hard bound on auto-continued turns
#     (the claudefa.st turn-counter guard); log + reset + allow stop.
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

# 4) Continue: increment counter + inject next-action + the run-scoped skip-set.
ITER=$((ITER + 1)); printf '%s' "$ITER" > "$ITERF" 2>/dev/null
NEXT=$(hook_roadmap_next "$PROJECT_DIR/.harness/roadmap_status.md")
NEXT=${NEXT:-"(derive per CLAUDE.md §4 from the dashboard)"}
# Same reason as tools/04-loop/run.sh (merge-gate concurrency lens, #1426): the skip-set
# reads the SHARED venue, so an un-drained pre-U-HE-29 ledger contributes nothing to it. A
# session whose own SessionStart migration was incomplete (rc 2 — a live sibling held the
# claim) would otherwise stay blind to that worktree's legacy rows for its ENTIRE lifetime,
# because nothing retries within the session. Draining here makes every Stop-turn re-try it.
# Capture the drain's status (codex r19 P1). A FAILED drain (rc 1) leaves the skip-set
# incomplete by an unknown amount, and the next autonomous turn reads "not in the list" as
# "safe to attempt" — the unsafe direction. Blocking the turn outright would wedge the loop
# on a broken legacy file, so the incompleteness is stated IN the continuation reason.
_MIGRC=0
if command -v loop_status_migrate >/dev/null 2>&1; then
  loop_status_migrate >/dev/null 2>&1; _MIGRC=$?
fi
SKIP=$(loop_skip_set)
SKIP=${SKIP:-none}
case "$_MIGRC" in
  0) SKIPWARN="" ;;
  2|3)
    # A live sibling holds a claim. Self-healing, and the rows it holds were already open —
    # warn and continue.
    SKIPWARN=" WARNING: a concurrent migration still holds a legacy ledger, so this list may be INCOMPLETE — absence from it is NOT permission to attempt an item."
    ;;
  *)
    # A GENUINE failure: the skip-set is incomplete by an UNKNOWN amount. A warning is not
    # enforcement (codex r20 P2) — the same reason text tells the next turn to pick an item
    # ABSENT from the list, so a declined item can still be retried. Stand down instead and
    # let the operator look: a stopped loop is visible and recoverable, a silently
    # re-attempted gate is neither. The halt marker is raised so the OUTER headless runner
    # sees the gate too, exactly as a child-raised halt does.
    loop_log STOP "legacy loop_status ledger could not be drained (rc ${_MIGRC}) — skip-set unknowable; standing down for operator review"
    [ -n "$HALT" ] && : > "$HALT" 2>/dev/null
    rm -f "$ITERF" 2>/dev/null
    exit 0
    ;;
esac

REASON="[stop-loop] autonomous loop continuing (turn ${ITER}/${MAX}). Dashboard next-action: ${NEXT}.
ALREADY DEFERRED this run — do NOT re-attempt these (build elsewhere): ${SKIP}.${SKIPWARN}
Pick the highest-priority forward item per CLAUDE.md §12.4.1 that is NOT in the deferred set, and drive it: ground empirically → build the slice that does NOT need any gated input → tests → PR → CI-green → merge → fixed-point refresh (CLAUDE.md §12). Use /resolve for reversible in-repo forks.
If the item is GATED (needs a paid call / secret / vendor selection / missing credential / infra you cannot provide): do NOT force it and do NOT raise .loop-halt. Build whatever slice is possible WITHOUT the gated input, then record the deferral with the allowlisted wrapper — \`tools/04-loop/defer.sh <ITEM-ID> 'what operator input is needed (plain text, no shell metacharacters) — built without it: slice or none'\` — and ADVANCE to the next forward item. (Run it as a single command; do NOT chain it or source the libs yourself — the wrapper does that and is the only guard-allowed path.) The hard-stop deny-list still blocks the dangerous TOOL; this is the item-level disposition.
ONLY when EVERY forward item per §12.4.1 is already in the deferred set (no buildable slice remains anywhere) do you stand the run down with \`tools/04-loop/halt.sh 'forward menu exhausted — N items awaiting operator input'\`. Then the run ends for operator review."

jq -nc --arg r "$REASON" '{"decision":"block","reason":$r}'
exit 0

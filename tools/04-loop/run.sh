#!/usr/bin/env bash
# Headless overnight runner (U-HK-15). `just loop`.
#
# Drives the roadmap arc unattended: turns loop mode ON (so the U-HK-12 permission
# guard auto-approves safe tools + hard-stops dangerous ones, and the U-HK-14
# Stop-continue keeps each session going) and re-invokes `claude -p` in a BOUNDED bash
# loop until a genuine gate (halt marker) or the iteration cap. Every iteration is
# recorded to the shared loop_status.md (C-HE-09 §2); the run prints the ledger tail on exit.
#
# Safety:
#   - bounded by --max (default HARNESS_LOOP_MAX or 25) — never an unbounded run;
#   - stops when .harness/.loop-halt appears — raised ONLY on a TRUE stand-down (the
#     forward menu is exhausted: every forward item deferred) or an operator stop, NOT at
#     a single gated item. A gated item is DEFERRED + worked around (the loop advances to
#     the next forward item per §12.4.1); the persistent ledger skip-set survives across
#     these fresh `claude -p` children so no item is re-attempted;
#   - does NOT pass --dangerously-skip-permissions; approvals flow through the
#     permission guard (unknown tools fall through to deny in headless, the safe default);
#   - --dry-run prints the planned invocation + exercises the loop WITHOUT calling claude.
#
# Usage: tools/04-loop/run.sh [--dry-run] [--max N] [--prompt "..."]
# Test: tools/04-loop/test_run.sh.

set -uo pipefail

_HOOKS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../hooks" && pwd)"
# shellcheck source=../hooks/lib.sh
. "$_HOOKS/lib.sh"
# shellcheck source=../hooks/loop_lib.sh
. "$_HOOKS/loop_lib.sh"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && { echo "[loop] cannot resolve project dir" >&2; exit 1; }
cd "$PROJECT_DIR" || exit 1

DRY=0
MAX=${HARNESS_LOOP_MAX:-25}
# Default prompt; HARNESS_LOOP_PROMPT env overrides it (the robust path for multi-word
# prompts, since `just`'s variadic args don't preserve quoting — see the justfile note).
# NOTE: the runner computes the run-scoped skip-set itself (loop_skip_set) and appends it
# to the prompt PER ITERATION below — the fresh `claude -p` child cannot run loop_skip_set
# (it is a chained/sourced command the permission guard denies in headless). The child
# records new deferrals + stand-down ONLY via the allowlisted wrappers tools/04-loop/defer.sh
# and tools/04-loop/halt.sh (a raw `source … && loop_defer …` is denied + malformed).
PROMPT="${HARNESS_LOOP_PROMPT:-Continue the roadmap. Run the §12.1 audit, then pick the highest-priority forward item per CLAUDE.md §12.4.1 that is NOT in the 'already deferred this run' list below. Drive it: ground empirically → build the slice that does NOT need any gated input → implement with tests → PR → CI-green → merge → fixed-point refresh. Use /resolve for reversible forks. If the item is GATED (paid call / secret / vendor selection / missing credential / infra): do NOT force it and do NOT raise the halt marker — build whatever slice is possible without the gated input, then run the single command 'tools/04-loop/defer.sh <ITEM-ID> \"what operator input is needed (plain text) — built without it: slice or none\"' and ADVANCE to the next forward item. ONLY when EVERY forward item per §12.4.1 is already deferred (nothing buildable remains) run 'tools/04-loop/halt.sh \"forward menu exhausted — N awaiting operator input\"' to stand the run down.}"

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    --max) [ $# -ge 2 ] || { echo "[loop] --max needs a value" >&2; exit 2; }; MAX="$2"; shift 2 ;;
    --prompt) [ $# -ge 2 ] || { echo "[loop] --prompt needs a value" >&2; exit 2; }; PROMPT="$2"; shift 2 ;;
    *) echo "[loop] unknown arg: $1" >&2; exit 2 ;;
  esac
done
[[ "$MAX" =~ ^[0-9]+$ ]] || { echo "[loop] --max must be an integer" >&2; exit 2; }

loop_activate "headless runner (just loop), max ${MAX}${DRY:+ (dry-run)}"
# Clear loop mode on EVERY exit path (normal, error, Ctrl-C, SIGTERM) so an interrupted
# run never leaks the .loop-active marker into the next interactive session — which would
# silently leave the auto-approve hooks armed. Run-once (idempotent). On INT/TERM we must
# also EXIT: a bare signal trap returns to the while loop and would launch more children.
# Recursively SIGTERM a process and all its descendants. On a signal we MUST tear down
# the in-flight `claude -p` child (launched with HARNESS_LOOP=1) and its subtree —
# otherwise it keeps running unattended with auto-approval armed until its own timeout.
_kill_tree() {  # $1=pid $2=signal(default TERM)
  local p="$1" sig="${2:-TERM}" c
  [ -n "$p" ] || return 0
  for c in $(pgrep -P "$p" 2>/dev/null); do _kill_tree "$c" "$sig"; done
  kill -"$sig" "$p" 2>/dev/null
}
_CLEANED=0
CHILD=""
_loop_cleanup() {
  [ "$_CLEANED" = 1 ] && return 0; _CLEANED=1
  # TERM the child subtree, then escalate to KILL for any TERM-ignoring descendant so no
  # loop-enabled (HARNESS_LOOP=1) process is left orphaned.
  if [ -n "$CHILD" ]; then _kill_tree "$CHILD" TERM; sleep 1; _kill_tree "$CHILD" KILL; fi
  loop_deactivate "headless runner exit"
  echo "[loop] loop mode OFF."
}
trap _loop_cleanup EXIT
trap '_loop_cleanup; exit 130' INT
trap '_loop_cleanup; exit 143' TERM
echo "[loop] loop mode ON; max ${MAX} iterations; dry-run=${DRY}"

i=0
while [ "$i" -lt "$MAX" ]; do
  i=$((i + 1))
  if [ -f "$(loop_halt_path)" ]; then
    loop_log STOP "headless: halt marker present — standing down at a genuine gate (iter ${i})"
    echo "[loop] halt marker — standing down at iteration ${i}"
    rm -f "$(loop_halt_path)" 2>/dev/null
    break
  fi
  if [ "$DRY" = "1" ]; then
    echo "[loop][dry-run] iter ${i}/${MAX}: claude -p <prompt> --permission-mode default"
    loop_log COMPLETED "dry-run iteration ${i}"
    [ "$i" -ge "${DRY_ITERS:-1}" ] && break
    continue
  fi
  # DRAIN ANY PRE-U-HE-29 LEDGER FIRST (merge-gate concurrency lens, #1426). The skip-set
  # now reads the SHARED venue, so a worktree whose legacy per-worktree ledger has not been
  # drained yet contributes NOTHING to it — and this runner computes SKIP before the child it
  # spawns has ever run its own SessionStart migration. On iteration 1 that is deterministic,
  # not racy: a genuinely still-open DEFERRED-HIL would be omitted and the loop would
  # re-attempt an item the operator already declined, which is the exact under-skip C-HE-09's
  # ledger exists to prevent. Before this venue move `loop_skip_set` read that same
  # per-worktree file directly, so leaving this unwired would be a REGRESSION, not a gap.
  # NOT best-effort-and-silent (codex r19 P1): a FAILED drain (rc 1) means we could not read
  # a legacy ledger at all, so the skip-set below is incomplete by an UNKNOWN amount — and
  # "not in the list" is exactly what the child reads as "safe to attempt". Halting the whole
  # run on a broken legacy file would be worse (it wedges every forward item), so the
  # incompleteness is carried INTO the prompt instead: the child is told not to treat absence
  # from the list as permission. rc 2 (a live sibling holds a claim) is the milder form.
  _MIGRC=0
  if command -v loop_status_migrate >/dev/null 2>&1; then
    loop_status_migrate >/dev/null 2>&1; _MIGRC=$?
  fi
  _SKIPWARN=""
  case "$_MIGRC" in
    0) ;;
    2) _SKIPWARN=" [WARNING: a concurrent migration still holds a legacy ledger, so this list may be INCOMPLETE — do NOT treat absence from it as permission to attempt an item]" ;;
    *) _SKIPWARN=" [WARNING: a legacy loop_status ledger could NOT be drained (rc ${_MIGRC}), so this list is INCOMPLETE by an unknown amount — do NOT treat absence from it as permission to attempt an item; surface this to the operator]" ;;
  esac
  [ -n "$_SKIPWARN" ] && echo "[loop] migration rc=${_MIGRC}: skip-set may be incomplete" >&2
  # Compute the run-scoped skip-set HERE (the fresh child cannot — loop_skip_set is a
  # chained/sourced command the guard denies) and append it to the prompt so the child
  # advances past already-deferred items instead of re-attempting the static next-action.
  SKIP=$(loop_skip_set); SKIP=${SKIP:-none}
  ITER_PROMPT="${PROMPT} [already deferred this run — do NOT re-attempt: ${SKIP}]${_SKIPWARN}"
  echo "[loop] iteration ${i}/${MAX} → claude -p (deferred so far: ${SKIP})"
  # Loop mode on for the child so the in-session hooks fire; bounded per turn. NOTE: no
  # --allowedTools — every tool flows through the U-HK-12 permission guard (allow safe /
  # deny dangerous / ask→deny-in-headless unknown). Passing bare `Bash` here would
  # pre-approve EVERY command and bypass the guard. NO --dangerously-skip-permissions.
  # Run in the background + record the PID so a signal can kill the whole subtree
  # (see _loop_cleanup / _kill_tree). `wait` is interruptible: a SIGINT/SIGTERM during
  # the turn fires the trap, which kills CHILD and exits.
  # Pass the cap to the child too, so the in-session Stop-continue (stop-loop.sh) honors
  # the same --max instead of defaulting to 25 in-session turns.
  HARNESS_LOOP=1 HARNESS_LOOP_MAX="$MAX" hook_bounded "${HARNESS_LOOP_TURN_TIMEOUT:-1800}" \
    claude -p "$ITER_PROMPT" --permission-mode default &
  CHILD=$!
  wait "$CHILD" || loop_log COMPLETED "iteration ${i} claude exited nonzero/bounded"
  CHILD=""
done

# Loop mode is cleared by the EXIT trap (_loop_cleanup) on every path; print the ledger
# tail first so the operator sees what the run did.
echo "[loop] run finished after ${i} iteration(s). Ledger tail:"
[ -f "$(loop_status_path)" ] && tail -n 15 "$(loop_status_path)"

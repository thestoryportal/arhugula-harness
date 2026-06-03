#!/usr/bin/env bash
# Headless overnight runner (U-HK-15). `just loop`.
#
# Drives the roadmap arc unattended: turns loop mode ON (so the U-HK-12 permission
# guard auto-approves safe tools + hard-stops dangerous ones, and the U-HK-14
# Stop-continue keeps each session going) and re-invokes `claude -p` in a BOUNDED bash
# loop until a genuine gate (halt marker) or the iteration cap. Every iteration is
# recorded to .harness/loop_status.md; the run prints the ledger tail on exit.
#
# Safety:
#   - bounded by --max (default HARNESS_LOOP_MAX or 25) — never an unbounded run;
#   - stops immediately when .harness/.loop-halt appears (a genuine gate: paid call /
#     secret / destructive / missing cred — written by the loop when it defers);
#   - does NOT pass --dangerously-skip-permissions; approvals flow through the
#     permission guard (unknown tools fall through to deny in headless, the safe default);
#   - --dry-run prints the planned invocation + exercises the loop WITHOUT calling claude.
#
# Usage: tools/loop/run.sh [--dry-run] [--max N] [--prompt "..."]
# Test: tools/loop/test_run.sh.

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
PROMPT='Continue the roadmap. Run the §12.1 audit, derive the next-action per CLAUDE.md §4, then drive it: ground empirically → implement with tests → PR → CI-green → merge → fixed-point refresh. Use /resolve for reversible forks. At a genuine gate (paid call / secret / destructive / missing cred) create .harness/.loop-halt, log a DEFERRED-HIL row, and stop.'
ALLOWED="Bash Edit Write Read Grep Glob Task TodoWrite NotebookEdit"

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    --max) MAX="${2:-$MAX}"; shift 2 ;;
    --prompt) PROMPT="${2:-$PROMPT}"; shift 2 ;;
    *) echo "[loop] unknown arg: $1" >&2; exit 2 ;;
  esac
done
[[ "$MAX" =~ ^[0-9]+$ ]] || { echo "[loop] --max must be an integer" >&2; exit 2; }

loop_activate "headless runner (just loop), max ${MAX}${DRY:+ (dry-run)}"
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
    echo "[loop][dry-run] iter ${i}/${MAX}: claude -p <prompt> --permission-mode default --allowedTools ${ALLOWED}"
    loop_log COMPLETED "dry-run iteration ${i}"
    [ "$i" -ge "${DRY_ITERS:-1}" ] && break
    continue
  fi
  echo "[loop] iteration ${i}/${MAX} → claude -p"
  # Loop mode on for the child so the in-session hooks fire; bounded per turn.
  HARNESS_LOOP=1 hook_bounded "${HARNESS_LOOP_TURN_TIMEOUT:-1800}" \
    claude -p "$PROMPT" --permission-mode default --allowedTools "$ALLOWED" || \
    loop_log COMPLETED "iteration ${i} claude exited nonzero/bounded"
done

loop_deactivate "headless runner exit after ${i} iteration(s)"
echo "[loop] loop mode OFF. Ledger tail:"
[ -f "$(loop_status_path)" ] && tail -n 15 "$(loop_status_path)"

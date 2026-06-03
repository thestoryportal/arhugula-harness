#!/usr/bin/env bash
# In-session Stop-continue loop (U-HK-14). Stop matcher "*".
#
# In loop mode, keeps the roadmap arc going across turns without an operator round-trip:
# at turn end it injects the next-action and `decision:block`s to continue. It STOPS
# (allows the turn to end) at a genuine gate or a bound:
#   - INERT unless loop mode on (exit 0).
#   - HALT MARKER (.harness/.loop-halt) present → a genuine gate was hit (paid call /
#     secret / destructive / missing cred); log + clear it + allow stop.
#   - ITERATION CAP (HARNESS_LOOP_MAX, default 25) → hard bound on auto-continued turns
#     (the claudefa.st turn-counter guard); log + reset + allow stop.
#   - otherwise → increment the counter + block with the next-action.
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

# 2) Genuine-gate halt marker → stand down (clear it so the next /loop-start is clean).
if [ -n "$HALT" ] && [ -f "$HALT" ]; then
  loop_log STOP "halt marker present — loop standing down at a genuine gate"
  rm -f "$HALT" "$ITERF" 2>/dev/null
  exit 0
fi

# 3) Iteration cap → hard bound reached, stop.
ITER=$(cat "$ITERF" 2>/dev/null || echo 0)
[[ "$ITER" =~ ^[0-9]+$ ]] || ITER=0
if [ "$ITER" -ge "$MAX" ]; then
  loop_log STOP "iteration cap ${MAX} reached — loop stopping (run /loop-start to resume)"
  rm -f "$ITERF" 2>/dev/null
  exit 0
fi

# 4) Continue: increment counter + inject next-action.
ITER=$((ITER + 1)); printf '%s' "$ITER" > "$ITERF" 2>/dev/null
NEXT=$(hook_roadmap_next "$PROJECT_DIR/.harness/roadmap_status.md")
NEXT=${NEXT:-"(derive per CLAUDE.md §4 from the dashboard)"}

REASON="[stop-loop] autonomous loop continuing (turn ${ITER}/${MAX}). Next action: ${NEXT}.
Drive the arc: ground empirically → implement with tests → PR → CI-green → merge → fixed-point refresh (CLAUDE.md §12).
At a GENUINE gate (paid call / secret relocation / destructive-irreversible op / missing credential): do NOT force it — create .harness/.loop-halt, log a DEFERRED-HIL row, and let the turn end. Use /resolve for reversible in-repo forks."

jq -nc --arg r "$REASON" '{"decision":"block","reason":$r}'
exit 0

#!/usr/bin/env bash
# Stop completion gate (U-HK-10). When Claude finishes a turn with uncommitted .py
# changes, run a FAST ruff lint on just those files; if it fails, `decision: block`
# so Claude fixes the lint before stopping (goal #9 — lint-before-stop).
#
# Loop safety: the stop_hook_active flag is checked FIRST — if we're already inside
# a stop-hook-induced continuation, the gate does nothing (blocks at most once per
# chain; the claudefa.st infinite-loop guard).
#
# Scope rationale: a full `just check` (lint+typecheck+test, minutes) on EVERY turn
# end would be unusable. The Stop gate is the fast lint tier; the heavy test/typecheck
# gate stays in CI (the hard gate) + the Wave-2 loop's pre-merge full check.
#
# Trigger: Stop, matcher "*".

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

PAYLOAD=$(hook_read_stdin)

# Loop guard FIRST: never re-block inside a stop-hook continuation.
ACTIVE=$(hook_json "$PAYLOAD" '.stop_hook_active')
[ "$ACTIVE" = "true" ] && exit 0

# Changed .py files vs HEAD: tracked (staged + unstaged, exclude deletions) PLUS
# untracked-but-not-ignored. A new .py Claude just wrote isn't in `git diff HEAD`
# until staged, so without the ls-files arm the most common edit path (create a
# fresh module) would bypass the lint-before-stop gate entirely. Collect into an
# ARRAY (read line-by-line) so paths with spaces / glob chars survive intact — the
# subsequent ruff invocation passes "${CHANGED[@]}", never an unquoted word-split.
declare -a CHANGED=()
while IFS= read -r _f; do [ -n "$_f" ] && CHANGED+=("$_f"); done < <(
  {
    git diff --name-only --diff-filter=d HEAD 2>/dev/null
    git ls-files --others --exclude-standard 2>/dev/null
  } | grep -E '\.py$' | sort -u
)
[ "${#CHANGED[@]}" -eq 0 ] && exit 0   # no python changes → allow stop

# Lint just the changed files (fast). Bounded. Prefer ruff on PATH, else uv run ruff.
# Capture stderr + exit status so a runner that CANNOT run (ruff+uv both absent, or
# ruff exits on an internal error / timeout) is surfaced as a VISIBLE block rather
# than a silent fall-through that disables the gate on a fresh/unsynced machine.
ERRF=$(mktemp 2>/dev/null) || ERRF=""
LINT=$(hook_bounded 30 bash -c '
  if command -v ruff >/dev/null 2>&1; then
    ruff check --quiet --output-format=concise "$@"
  else
    uv run --quiet ruff check --output-format=concise "$@"
  fi
' _ "${CHANGED[@]}" 2>"${ERRF:-/dev/null}")
RC=$?
ERR=""; [ -n "$ERRF" ] && { ERR=$(cat "$ERRF" 2>/dev/null); rm -f "$ERRF"; }

if [ -n "$LINT" ]; then
  # Findings present (any exit code) → block so Claude fixes the lint before stopping.
  REASON="[stop-gate] ruff lint failed on changed files — fix before stopping:
${LINT}"
elif [ "${RC:-0}" -ne 0 ]; then
  # No findings but the runner failed to execute → surface it (don't fail open: the
  # gate silently vanishing on a machine without ruff/uv is the failure mode here).
  REASON="[stop-gate] could not run the lint gate (exit ${RC}; ruff/uv may be unavailable or the run timed out). Install ruff or run \`uv sync\` so lint-before-stop is active.${ERR:+ stderr: ${ERR}}"
else
  exit 0   # clean (ran, zero exit, no findings) → allow stop
fi

# Block the stop (continues the turn so Claude resolves the lint / runner issue).
jq -nc --arg r "$REASON" '{"decision":"block","reason":$r}'
exit 0

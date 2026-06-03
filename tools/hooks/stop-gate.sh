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

# Changed .py files vs HEAD (staged + unstaged; exclude deletions).
CHANGED=$(git diff --name-only --diff-filter=d HEAD 2>/dev/null | grep -E '\.py$' || true)
[ -z "$CHANGED" ] && exit 0   # no python changes → allow stop

# Lint just the changed files (fast). Bounded. Prefer ruff on PATH, else uv run ruff.
# shellcheck disable=SC2086
LINT=$(hook_bounded 30 bash -c '
  if command -v ruff >/dev/null 2>&1; then
    ruff check --quiet --output-format=concise "$@"
  else
    uv run --quiet ruff check --output-format=concise "$@"
  fi
' _ $CHANGED 2>/dev/null)

[ -z "$LINT" ] && exit 0   # clean → allow stop

# Block the stop so Claude fixes the lint before finishing (continues the turn).
jq -nc --arg r "[stop-gate] ruff lint failed on changed files — fix before stopping:
${LINT}" '{"decision":"block","reason":$r}'
exit 0

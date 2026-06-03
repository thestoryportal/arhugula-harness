#!/usr/bin/env bash
# PostToolUse(Edit|Write) lint-on-edit. After Claude edits a .py file, run ruff on
# JUST that file and inject any findings as additionalContext. NON-BLOCKING by
# design (PostToolUse cannot undo — it only informs; the Stop gate / CI ruff job is
# the hard enforcement). Silent when the file is clean. Bounded so it can't hang.
#
# Trigger: PostToolUse, matcher "Edit|Write|MultiEdit". Early-exits for non-.py
# files. Prefers a `ruff` on PATH; falls back to `uv run ruff`.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

PAYLOAD=$(hook_read_stdin)
FILE=$(hook_json "$PAYLOAD" '.tool_input.file_path')
[ -z "$FILE" ] && exit 0
case "$FILE" in *.py) ;; *) exit 0 ;; esac
[ -f "$FILE" ] || exit 0

# Lint the single file (concise). Bounded; prefer a direct ruff, else uv run ruff.
RUFF_OUT=$(hook_bounded 20 bash -c '
  if command -v ruff >/dev/null 2>&1; then
    ruff check --quiet --output-format=concise "$1"
  else
    uv run --quiet ruff check --output-format=concise "$1"
  fi
' _ "$FILE" 2>/dev/null)

[ -z "$RUFF_OUT" ] && exit 0   # clean → stay silent (no noise on good edits)

hook_emit "PostToolUse" "[lint] ruff findings on ${FILE}:
${RUFF_OUT}
(advisory — fix before the Stop gate / CI ruff job)"

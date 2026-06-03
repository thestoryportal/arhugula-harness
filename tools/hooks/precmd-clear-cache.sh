#!/usr/bin/env bash
# PreToolUse(Bash) stale-cache guard. Before a Python test/build command runs,
# clear the project's OWN bytecode caches so a stale .pyc can't produce misleading
# no-output results — the trap that nearly drove a wrong fork conclusion (CLAUDE.md
# §14.3 + the 2026-06-02 insights report). Advisory + NON-BLOCKING: it clears, then
# lets the command proceed (exit 0, no permission decision). Scoped to repo source
# (excludes .venv / .git / node_modules / worktrees so deps aren't needlessly
# recompiled) and bounded so it can never hang the tool call.
#
# Trigger: PreToolUse, matcher "Bash". Fires on every Bash call; early-exits unless
# the command is a pytest/pyright/uv-run/just-test command.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0

PAYLOAD=$(hook_read_stdin)
CMD=$(hook_json "$PAYLOAD" '.tool_input.command')

# Only fire for Python test/build commands (where a stale .pyc actually bites).
printf '%s' "$CMD" | grep -qE 'pytest|pyright|uv run|just (test|check|mech|mvp|retire)' || exit 0

# Delete the project's own __pycache__ dirs + .pyc files (regenerable). Pruned dirs
# keep deps/git/worktrees untouched. Whole find+delete is bounded as one unit.
hook_bounded 10 bash -c '
  find "$1" \
    \( -path "*/.venv" -o -path "*/.git" -o -path "*/node_modules" -o -path "*/.claude/worktrees" \) -prune -o \
    \( -type d -name __pycache__ -o -type f -name "*.pyc" \) -exec rm -rf {} + 2>/dev/null
' _ "$PROJECT_DIR" >/dev/null 2>&1 || true

exit 0

#!/usr/bin/env bash
# Race-safe worktree removal entrypoint for agent-issued cleanup.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 2
# shellcheck source=lib.sh
. "$_LIB"

[ "$#" -eq 1 ] || { echo "usage: safe-worktree-remove.sh <worktree>" >&2; exit 2; }
PROJECT_DIR=$(hook_project_dir)
[ -n "$PROJECT_DIR" ] || { echo "safe-worktree-remove: project root unavailable" >&2; exit 2; }

hook_safe_worktree_remove "$PROJECT_DIR" "$1"
rc=$?
case "$rc" in
  0) exit 0 ;;
  3) echo "safe-worktree-remove: target has a live Claude/Codex session" >&2 ;;
  2) echo "safe-worktree-remove: session/removal mutex unavailable" >&2 ;;
  *) echo "safe-worktree-remove: git refused removal" >&2 ;;
esac
exit "$rc"

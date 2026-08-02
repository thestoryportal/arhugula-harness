#!/usr/bin/env bash
# Race-safe worktree status/removal entrypoint for GC and agent-issued cleanup.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 2
# shellcheck source=lib.sh
. "$_LIB"

MODE=remove
if [ "$#" -eq 2 ] && [ "$1" = "--status" ]; then
  MODE=status
  shift
fi
[ "$#" -eq 1 ] || { echo "usage: safe-worktree-remove.sh [--status] <worktree>" >&2; exit 2; }
TARGET="$1"

if [ "$MODE" = "status" ]; then
  [ "$(git -C "$TARGET" rev-parse --is-inside-work-tree 2>/dev/null)" = "true" ] \
    || { echo "safe-worktree-remove: target is not a registered worktree" >&2; exit 2; }
  worktree_has_live_session "$TARGET"
  exit $?
fi

PROJECT_DIR=$(hook_project_dir)
[ -n "$PROJECT_DIR" ] || { echo "safe-worktree-remove: project root unavailable" >&2; exit 2; }

hook_safe_worktree_remove "$PROJECT_DIR" "$TARGET"
rc=$?
case "$rc" in
  0) exit 0 ;;
  3) echo "safe-worktree-remove: target has a live Claude/Codex session" >&2 ;;
  2) echo "safe-worktree-remove: session/removal mutex unavailable" >&2 ;;
  4) echo "safe-worktree-remove: target has local state" >&2 ;;
  5) echo "safe-worktree-remove: target local state unavailable" >&2 ;;
  6) echo "safe-worktree-remove: quarantined worktree could not be restored" >&2 ;;
  7) echo "safe-worktree-remove: target has retained process references" >&2 ;;
  8) echo "safe-worktree-remove: restored an interrupted quarantine; retry later" >&2 ;;
  9) echo "safe-worktree-remove: target process-reference state unavailable" >&2 ;;
  *) echo "safe-worktree-remove: git refused removal" >&2 ;;
esac
exit "$rc"

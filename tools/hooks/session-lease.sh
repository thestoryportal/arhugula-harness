#!/usr/bin/env bash
# Register or release the Codex session lease that orders worktree removal against
# SessionStart. The lease is session-scoped and stored under the shared git common dir.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

ACTION="${1:-}"
PAYLOAD=$(hook_read_stdin)
SESSION_ID=$(hook_json "$PAYLOAD" '.session_id')
WORKTREE=$(hook_json "$PAYLOAD" '.cwd')
[ -n "$WORKTREE" ] || WORKTREE=$(hook_project_dir)
[ -n "$SESSION_ID" ] && [ -n "$WORKTREE" ] || exit 0

case "$ACTION" in
  start) hook_register_session_lease "$WORKTREE" "$SESSION_ID" ;;
  end) hook_release_session_lease "$WORKTREE" "$SESSION_ID" ;;
  *) exit 2 ;;
esac

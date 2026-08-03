#!/usr/bin/env bash
# Release the Codex worktree lease before running bounded local SessionEnd cleanup.

set -uo pipefail

_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD=$(cat 2>/dev/null || true)

printf '%s' "$PAYLOAD" \
  | HARNESS_WORKTREE_LOCK_TIMEOUT_SECONDS=1 /bin/bash "$_DIR/session-lease.sh" end || exit 2

printf '%s' "$PAYLOAD" | /bin/bash "$_DIR/session-end-cleanup.sh"

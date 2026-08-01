#!/usr/bin/env bash
# Register the Codex worktree lease before running the longer SessionStart posture guard.

set -uo pipefail

_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD=$(cat 2>/dev/null || true)

if ! printf '%s' "$PAYLOAD" | /bin/bash "$_DIR/session-lease.sh" start; then
  echo "codex-session-start: could not register the worktree session lease" >&2
  exit 2
fi

printf '%s' "$PAYLOAD" | /usr/bin/python3 "$_DIR/../../.codex/hooks/session_start.py"

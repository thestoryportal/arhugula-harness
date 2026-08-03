#!/usr/bin/env bash
# Register the Codex worktree lease before running the longer SessionStart posture guard.

set -uo pipefail

_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_LIB="$_DIR/lib.sh"
[ -f "$_LIB" ] || exit 2
# shellcheck source=lib.sh
. "$_LIB"
PAYLOAD=$(cat 2>/dev/null || true)
LEASE_STARTING_OWNED=0
LEASE_ACTIVATED=0

lease_action() {
  printf '%s' "$PAYLOAD" \
    | HARNESS_CODEX_SESSION_OWNER_PID="$PPID" /bin/bash "$_DIR/session-lease.sh" "$1"
}

cleanup_starting_lease() {
  local rc=$?
  trap - EXIT
  if [ "$LEASE_STARTING_OWNED" -eq 1 ] && [ "$LEASE_ACTIVATED" -eq 0 ]; then
    lease_action end || true
  fi
  exit "$rc"
}

trap cleanup_starting_lease EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

lease_action start
lease_rc=$?
case "$lease_rc" in
  0) LEASE_STARTING_OWNED=1 ;;
  10) LEASE_ACTIVATED=1 ;;
  *)
    echo "codex-session-start: could not register the worktree session lease" >&2
    exit 2
    ;;
esac

if hook_review_isolated; then
  if ! lease_action activate; then
    echo "codex-session-start: could not activate the worktree session lease" >&2
    exit 2
  fi
  LEASE_ACTIVATED=1
  exit 0
fi

POSTURE=$(printf '%s' "$PAYLOAD" | /usr/bin/python3 "$_DIR/../../.codex/hooks/session_start.py") || exit $?
# SessionStart has a 105-second host budget and posture may consume 75 seconds. Keep
# both advisory companions inside explicit aggregate slices so worktree cardinality or
# a slow remote cannot make the wrapper exceed the host deadline.
ROADMAP=$(printf '%s' "$PAYLOAD" \
  | hook_bounded "${HARNESS_SESSION_START_ROADMAP_SECONDS:-8}" \
      /bin/bash "$_DIR/../roadmap-audit/session-start.sh") || true
HYGIENE=$(printf '%s' "$PAYLOAD" \
  | hook_bounded "${HARNESS_SESSION_START_HYGIENE_SECONDS:-8}" \
      /bin/bash "$_DIR/loop-gc.sh") || true

context_from_hook() {
  printf '%s' "$1" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null
}

ROADMAP_CONTEXT=$(context_from_hook "$ROADMAP")
HYGIENE_CONTEXT=$(context_from_hook "$HYGIENE")
CONTEXT="$POSTURE"
[ -z "$ROADMAP_CONTEXT" ] || CONTEXT="${CONTEXT}
${ROADMAP_CONTEXT}"
[ -z "$HYGIENE_CONTEXT" ] || CONTEXT="${CONTEXT}
${HYGIENE_CONTEXT}"
if ! lease_action activate; then
  echo "codex-session-start: could not activate the worktree session lease" >&2
  exit 2
fi
LEASE_ACTIVATED=1
hook_emit SessionStart "$CONTEXT"

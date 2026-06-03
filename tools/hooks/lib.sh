#!/usr/bin/env bash
# Shared library for Claude Code hook scripts in this workspace.
#
# Sourced by tools/roadmap-audit/*.sh and tools/hooks/*.sh so every hook reuses
# ONE tested helper set instead of re-implementing the conventions — the
# anti-drift keystone of the U-HK-* autonomy-infrastructure plan. The functions
# are side-effect-free EXCEPT `hook_emit` (prints JSON + exits 0).
#
# Conventions preserved verbatim from the two original hooks (session-start.sh +
# post-merge-refresh.sh): the additionalContext JSON shape, the §12.1
# workspace_state_hash recipe, the portable bounded-run watchdog (stock-macOS
# safe), and the always-exit-0 / encode-failure-as-context discipline.
#
# Pure function library — do NOT `set -e` here (it would surprise the sourcing
# script). Test with tools/hooks/test_lib.sh.

# Resolve the workspace root: $CLAUDE_PROJECT_DIR (set by Claude Code) or the git
# toplevel. Echoes the path, empty if neither resolves.
# Usage: PROJECT_DIR=$(hook_project_dir); [ -z "$PROJECT_DIR" ] && exit 0
hook_project_dir() {
  local d="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
  printf '%s' "$d"
}

# Emit additionalContext JSON for a hook event and exit 0. Mirrors the original
# hooks' shape. Usage: hook_emit <hookEventName> <context-string>
hook_emit() {
  jq -nc --arg ev "$1" --arg ctx "$2" \
    '{"hookSpecificOutput":{"hookEventName":$ev,"additionalContext":$ctx}}'
  exit 0
}

# Read all of stdin (the hook payload JSON). Echoes it; empty on none.
hook_read_stdin() { cat 2>/dev/null || true; }

# Extract a jq path from a JSON payload with an empty-string default.
# Usage: CMD=$(hook_json "$PAYLOAD" '.tool_input.command')
hook_json() { printf '%s' "$1" | jq -r "$2 // empty" 2>/dev/null || true; }

# Default branch name (origin/HEAD symref), falling back to "main".
hook_default_branch() {
  local b
  b=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
  printf '%s' "${b:-main}"
}

# Portable bounded runner: run a command, kill it if it outlives SECS — even on a
# stock macOS that ships neither GNU `timeout` nor `gtimeout`. Prefers the native
# binary when present; otherwise a pure-bash watchdog that ESCALATES SIGTERM →
# SIGKILL after a short grace, so a child stuck in an SSH / credential-helper path
# that ignores TERM is still force-killed (SIGKILL is uncatchable). `wait` then
# returns within SECS + grace — a genuine hard bound, never an indefinite hang.
# Returns the command's exit code (or the kill's). Usage: hook_bounded SECS cmd...
hook_bounded() {
  local secs="$1"; shift
  # `-k 2`: GNU timeout sends SIGTERM at SECS, then SIGKILL 2s later if the child
  # ignored TERM (without -k, `timeout` only sends TERM and WAITS — a TERM-ignoring
  # git-over-SSH would hang the hook). Both native paths and the pure-bash fallback
  # escalate to KILL, so this is a genuine hard bound everywhere. Invoke the binary
  # EXPLICITLY (not via an unquoted "$prefix $@" that relies on word-splitting — zsh
  # does not split unquoted vars, which would turn the prefix into one bogus argv0).
  if command -v timeout >/dev/null 2>&1; then
    timeout -k 2 "$secs" "$@"
    return $?
  fi
  if command -v gtimeout >/dev/null 2>&1; then
    gtimeout -k 2 "$secs" "$@"
    return $?
  fi
  "$@" & local p=$!
  (
    sleep "$secs"
    kill -0 "$p" 2>/dev/null || exit 0
    kill -TERM "$p" 2>/dev/null
    sleep 2
    kill -0 "$p" 2>/dev/null && kill -KILL "$p" 2>/dev/null
  ) >/dev/null 2>&1 & local w=$!
  wait "$p" 2>/dev/null; local rc=$?
  kill "$w" 2>/dev/null; wait "$w" 2>/dev/null
  return "$rc"
}

# The §12.1 step-2 workspace_state_hash recipe: sha256(head|prs|forks|batch)[:12].
# Usage: hook_state_hash <head8> <prs_csv> <forks_count> <batch_path>
hook_state_hash() {
  printf '%s|%s|%s|%s' "$1" "$2" "$3" "$4" | shasum -a 256 | head -c 12
}

# Extract the CURRENT roadmap next-action R-id from the dashboard. Scopes to the
# `## Next action` section (from that heading to the next `---` horizontal rule)
# and returns the FIRST backticked `R-NNN` token there. Scoping is the fix for the
# old whole-file `head -1` bug: the dashboard carries historical + narrative `R-*`
# references that precede the live pointer in document order (e.g. an `**`R-010`**`
# deep in the R-700 banner), so an unscoped match surfaced a stale item. Echoes the
# R-id (may contain `.` / `-`, e.g. `R-410..R-440`), empty if absent (callers
# default). Usage: NEXT=$(hook_roadmap_next "$DASHBOARD")
hook_roadmap_next() {
  local dash="$1"
  [ -f "$dash" ] || return 0
  awk '/^## Next action/{f=1; next} f && /^---$/{exit} f' "$dash" 2>/dev/null \
    | grep -oE '`R-[A-Za-z0-9._-]+`' 2>/dev/null | head -1 | tr -d '`'
}

# Loop-mode detection (Wave 2 autonomy gate). Returns 0 (true) when the autonomous
# loop is active. OFF by default — the autonomy hooks (auto-approve permissions,
# Stop-continue) MUST be inert unless this returns true, so normal interactive
# sessions are never auto-driven. Gate = HARNESS_LOOP=1 env OR a
# .harness/.loop-active marker file at the workspace root.
loop_mode_active() {
  [ "${HARNESS_LOOP:-}" = "1" ] && return 0
  local d; d=$(hook_project_dir)
  [ -n "$d" ] && [ -f "$d/.harness/.loop-active" ]
}

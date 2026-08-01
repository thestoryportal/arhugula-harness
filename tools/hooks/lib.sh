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

# True only for fresh merge-gate reviewer subprocesses launched through the exact
# permission-guarded command shape. These reviewers inspect the same worktree but must
# not mutate controller checkpoints, loop counters, or cleanup state.
hook_review_isolated() {
  [ "${HARNESS_CODEX_REVIEW_ISOLATED:-}" = "1" ]
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

# True iff the changed-file set of a commit is a §12.2.1 roadmap-status-only
# terminating refresh. §12.2.1 defines the allowed set as EXACTLY
# {.harness/roadmap_status.md} — no other file may change in the same commit.
#
# Closed-set (NOT "is-among") semantics are load-bearing: a substantive commit
# mis-titled with the reserved refresh prefix carries files outside the allowed
# single file, so it must NOT pass here (it correctly halts as DRIFT / emits
# "refresh owed"). Input is the caller's `git show --name-only … | sort -u`
# output (sorted-unique, trailing-newline-stripped by command substitution).
# Usage: hook_is_roadmap_status_only_set "$CHANGED_FILES_SORTED_UNIQUE"
hook_is_roadmap_status_only_set() {
  local set="$1"
  local status=".harness/roadmap_status.md"
  [ "$set" = "$status" ] && return 0
  return 1
}

# Extract the CURRENT roadmap next-action R-id from roadmap_status.md. Scopes to
# the `## Next action` section (from that heading to the next `---` horizontal
# rule OR the next `## ` heading, whichever comes first) and returns the FIRST
# backticked `R-NNN` token there. Scoping is the fix for the old whole-file
# `head -1` bug: the file carries historical + narrative `R-*` references that
# precede the live pointer in document order (e.g. an `**`R-010`**` deep in the
# R-700 banner), so an unscoped match surfaced a stale item. The `## ` exit
# condition (2026-07-23) is a second-order fix: `## Next action` is not always
# followed by a `---` before the NEXT `## ` section (e.g. `## Remaining forward
# work` can immediately follow with no `---` between them) — without it, the
# scoped section bled into that next section's own prose and could surface an
# already-RESOLVED R-id mentioned there instead of correctly finding no token
# in the actual Next action prose (which may use non-`R-`/`U-` tokens like
# `B-*`). Range tokens such as `R-410..R-440` are menus, not actionable units,
# so they are ignored. Echoes the R-id, empty if absent (callers default).
# Usage: NEXT=$(hook_roadmap_next "$ROADMAP_STATUS")
hook_roadmap_next() {
  local dash="$1"
  [ -f "$dash" ] || return 0
  local section current token
  section=$(awk '/^## Next action/{f=1; next} f && (/^---$/ || /^## /){exit} f' "$dash" 2>/dev/null)
  current=$(printf '%s\n' "$section" | grep -m1 'Current next action' 2>/dev/null || true)
  token=$(printf '%s\n' "$current" \
    | sed -nE 's/.*next implementable unit is `?((U|R)-[A-Za-z0-9._-]+)`?.*/\1/p' \
    | grep -v '\.\.' \
    | head -1)
  if [ -n "$token" ]; then
    printf '%s' "$token"
    return 0
  fi
  printf '%s\n' "$section" \
    | grep -oE '`(U|R)-[A-Za-z0-9._-]+`' 2>/dev/null \
    | tr -d '`' \
    | grep -v '\.\.' \
    | head -1
}

# Normalize a hook session id for use in a checkpoint filename.
hook_session_key() {
  local raw="${1:-shared}" key
  key=$(printf '%s' "$raw" | tr -c 'A-Za-z0-9_.-' '-' | cut -c1-80)
  printf '%s' "${key:-shared}"
}

# Write a lightweight state snapshot to a collision-free timestamped file plus an atomic,
# session-specific `precompact-latest-<session>.md` pointer. Shared by the compaction hook
# and context-recovery statusline. Args: <label> [skip_gh] [session_id]. With skip_gh
# non-empty the open-PRs call is omitted because the statusline is a hot path.
hook_write_checkpoint() {
  local label="$1" skip_gh="${2:-}" session
  session=$(hook_session_key "${3:-shared}")
  local d; d=$(hook_project_dir); [ -n "$d" ] || return 0
  local ckdir="$d/.harness/.checkpoints"
  mkdir -p "$ckdir" 2>/dev/null || return 0
  local ts head branch next prs dirty
  ts=$(date -u +%Y%m%d-%H%M%S 2>/dev/null || echo now)
  head=$(git -C "$d" rev-parse --short HEAD 2>/dev/null || echo "?")
  branch=$(git -C "$d" symbolic-ref --quiet --short HEAD 2>/dev/null || echo "?")
  next=$(hook_roadmap_next "$d/.harness/roadmap_status.md")
  if [ -z "$skip_gh" ]; then
    prs=$(hook_bounded 5 gh pr list --state open --json number,title --jq '.[]|"#\(.number) \(.title)"' 2>/dev/null | head -10)
  else
    prs="(skipped — fast path)"
  fi
  dirty=$(git -C "$d" status --short 2>/dev/null | head -30)
  local out="$ckdir/precompact-${ts}-${session}-$$.md"
  local out_tmp="${out}.tmp-$$"
  local latest="$ckdir/precompact-latest-${session}.md"
  local latest_tmp="${latest}.tmp-$$"
  {
    echo "# ${label} ${ts}"
    echo
    echo "- HEAD: \`${head}\` on \`${branch}\`"
    echo "- roadmap next-action: ${next:-?}"
    echo "- open PRs:"
    printf '%s\n' "${prs:-  (none)}" | sed 's/^/  - /'
    echo "- uncommitted:"
    printf '%s\n' "${dirty:-  (clean)}" | sed 's/^/  /'
  } > "$out_tmp" 2>/dev/null || { rm -f "$out_tmp" 2>/dev/null; return 0; }
  mv "$out_tmp" "$out" 2>/dev/null || { rm -f "$out_tmp" 2>/dev/null; return 0; }
  cp "$out" "$latest_tmp" 2>/dev/null || { rm -f "$latest_tmp" 2>/dev/null; return 0; }
  mv "$latest_tmp" "$latest" 2>/dev/null || rm -f "$latest_tmp" 2>/dev/null
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

_WORKTREE_SESSION_WINDOW_MIN="${HARNESS_WORKTREE_SESSION_WINDOW_MIN:-30}"

_hook_canonical_worktree() {
  local wt="$1"
  (cd "$wt" 2>/dev/null && pwd -P) || printf '%s' "$wt"
}

_hook_worktree_session_dir() {
  local wt abs common key
  wt="$1"; abs=$(_hook_canonical_worktree "$wt")
  common=$(git -C "$abs" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) \
    || return 1
  key=$(printf '%s' "$abs" | shasum -a 256 2>/dev/null | cut -d' ' -f1)
  [ -n "$key" ] || return 1
  printf '%s/codex-worktree-sessions/%s' "$common" "$key"
}

# A single per-worktree mutex orders SessionStart lease registration against removal.
# Empty lock directories older than two minutes are abandoned-process residue and can be
# reclaimed. Callers must pair a successful acquire with release.
hook_worktree_lock_acquire() {
  local wt="$1" session_dir lock tries=0
  session_dir=$(_hook_worktree_session_dir "$wt") || return 1
  mkdir -p "$session_dir" 2>/dev/null || return 1
  lock="$session_dir/remove.lock"
  while ! mkdir "$lock" 2>/dev/null; do
    if [ -d "$lock" ] \
      && [ -n "$(find "$lock" -maxdepth 0 -mmin +2 2>/dev/null | head -n1)" ]; then
      rmdir "$lock" 2>/dev/null || true
    fi
    tries=$((tries + 1)); [ "$tries" -lt 50 ] || return 1
    sleep 0.1
  done
  HOOK_WORKTREE_LOCK_DIR="$lock"
  return 0
}

hook_worktree_lock_release() {
  [ -n "${HOOK_WORKTREE_LOCK_DIR:-}" ] || return 0
  rmdir "$HOOK_WORKTREE_LOCK_DIR" 2>/dev/null
  HOOK_WORKTREE_LOCK_DIR=""
}

_hook_session_pointer_file() {
  local session base
  session=$(hook_session_key "$1")
  base="${TMPDIR:-/tmp}/arhugula-codex-session-leases-${UID:-user}"
  mkdir -p "$base" 2>/dev/null || return 1
  chmod 700 "$base" 2>/dev/null || return 1
  printf '%s/session-%s.pointer' "$base" "$session"
}

hook_register_session_lease() {
  local wt="$1" session session_dir lease tmp pointer pointer_tmp
  session=$(hook_session_key "$2")
  session_dir=$(_hook_worktree_session_dir "$wt") || return 1
  pointer=$(_hook_session_pointer_file "$session") || return 1
  hook_worktree_lock_acquire "$wt" || return 1
  lease="$session_dir/session-${session}.lease"; tmp="${lease}.tmp-$$"
  printf '%s\n' "$(_hook_canonical_worktree "$wt")" > "$tmp" 2>/dev/null \
    && mv "$tmp" "$lease" 2>/dev/null
  local rc=$?
  [ "$rc" -eq 0 ] || rm -f "$tmp" 2>/dev/null
  if [ "$rc" -eq 0 ]; then
    pointer_tmp="${pointer}.tmp-$$"
    printf '%s\n' "$lease" > "$pointer_tmp" 2>/dev/null \
      && mv "$pointer_tmp" "$pointer" 2>/dev/null
    rc=$?
    [ "$rc" -eq 0 ] || rm -f "$pointer_tmp" 2>/dev/null
  fi
  hook_worktree_lock_release || true
  return "$rc"
}

hook_release_session_lease() {
  local wt="$1" session session_dir lease pointer locked=0
  session=$(hook_session_key "$2")
  pointer=$(_hook_session_pointer_file "$session") || return 1
  session_dir=$(_hook_worktree_session_dir "$wt" 2>/dev/null || true)
  if [ -n "$session_dir" ]; then
    hook_worktree_lock_acquire "$wt" || return 1
    locked=1
    lease="$session_dir/session-${session}.lease"
  elif [ -f "$pointer" ]; then
    lease=$(head -n1 "$pointer" 2>/dev/null)
    case "$lease" in
      *..*|*$'\n'*) return 1 ;;
      */codex-worktree-sessions/*/session-"${session}".lease) ;;
      *) return 1 ;;
    esac
  else
    return 0
  fi
  rm -f "$lease" "$pointer" 2>/dev/null
  local rc=$?
  [ "$locked" -eq 0 ] || hook_worktree_lock_release || true
  return "$rc"
}

# Remove a registered worktree only while holding the same mutex used by SessionStart
# lease registration. Return 3 when a live session wins the race, 2 when the mutex cannot
# be acquired, otherwise return git's status.
hook_safe_worktree_remove() {
  local root="$1" wt="$2" rc
  hook_worktree_lock_acquire "$wt" || return 2
  if worktree_has_live_session "$wt"; then
    hook_worktree_lock_release || true
    return 3
  fi
  git -C "$root" worktree remove "$wt"
  rc=$?
  hook_worktree_lock_release || true
  return "$rc"
}

# Live-session detection covers both runners: Claude's encoded project transcripts,
# Codex's date-partitioned rollout transcripts (`session_meta.payload.cwd`), and the
# short-lived SessionStart/SessionEnd lease used to close the transcript check/remove
# race. A recent artifact within the configurable window marks the worktree live.
worktree_has_live_session() {
  local wt="$1"
  [ -n "$wt" ] || return 1
  command -v find >/dev/null 2>&1 || return 1
  local abs; abs=$(cd "$wt" 2>/dev/null && pwd -P) || abs="$wt"
  local session_dir
  session_dir=$(_hook_worktree_session_dir "$abs" 2>/dev/null || true)
  if [ -n "$session_dir" ] && [ -n "$(find "$session_dir" -maxdepth 1 -name 'session-*.lease' -mmin "-${_WORKTREE_SESSION_WINDOW_MIN}" 2>/dev/null | head -n1)" ]; then
    return 0
  fi

  local enc; enc=$(printf '%s' "$abs" | tr -c '[:alnum:]' '-')
  local claude_dir="$HOME/.claude/projects/$enc"
  if [ -d "$claude_dir" ] \
    && [ -n "$(find "$claude_dir" -maxdepth 1 -name '*.jsonl' -mmin "-${_WORKTREE_SESSION_WINDOW_MIN}" 2>/dev/null | head -n1)" ]; then
    return 0
  fi

  local codex_dir="$HOME/.codex/sessions" match
  if [ -d "$codex_dir" ]; then
    match=$(find "$codex_dir" -type f -name 'rollout-*.jsonl' -mmin "-${_WORKTREE_SESSION_WINDOW_MIN}" -print0 2>/dev/null \
      | while IFS= read -r -d '' transcript; do
          local transcript_cwd
          transcript_cwd=$(head -n1 "$transcript" 2>/dev/null | jq -r '.payload.cwd // empty' 2>/dev/null)
          [ -n "$transcript_cwd" ] || continue
          transcript_cwd=$(_hook_canonical_worktree "$transcript_cwd")
          if [ "$transcript_cwd" = "$abs" ]; then printf 'live'; break; fi
        done)
    [ -n "$match" ] && return 0
  fi
  return 1
}

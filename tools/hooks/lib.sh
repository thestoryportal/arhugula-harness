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

# True when git's stderr describes LOCAL lock contention. git serialises index, ref
# and config writes through a `<target>.lock` sidecar created with O_EXCL, so two
# lanes touching one repo collide transiently and the loser aborts before doing any
# work. Two shapes, both measured against git 2.39:
#
#   fatal: Unable to create '…/index.lock': File exists.          (index, and ref —
#     a ref collision prints `cannot lock ref '…':` in FRONT of this same clause)
#   error: could not lock config file .git/config: File exists    (config)
#
# The config wording is matched on its own because it names no `.lock` file at all,
# and a pattern written from the index/ref messages alone silently misses the
# `gc.auto 0` write of C-HE-11 §2 — the one B-201 is about.
#
# `File exists` is required, not incidental: it is what separates a lock another
# process is holding from a lock git refuses on the merits. `cannot lock ref 'x': is
# at <a> but expected <b>` is a stale-expectation conflict that no amount of waiting
# resolves, so matching the bare phrase would burn the whole budget on it and then
# file a `lock_contention` NOTIFY naming a cause that never happened.
_hook_git_lock_contention() {
  printf '%s' "$1" | grep -Eq \
    "(Unable to create .*\.lock|could not lock config file [^:]*): File exists|Another git process seems to be running"
}

# Run a git command, retrying ONLY local lock contention, on the C-HE-11 §3 budget:
# full jitter over {base 100 ms, factor 2, cap 5 s, max 8 attempts}. Exhaustion FAILS
# the git operation (git's own exit code and stderr survive) and emits a NOTIFY.
#
# This is LOCAL-git retry, deliberately unrelated to the merge-door lease, which
# stays fail-fast (C-HE-06 §2). Hence the `git-ref-lock:` cause: a lock collision is
# environmental, and must never be read as merge-door budget spend (C-HE-13 §3).
#
# stdout is the CALLER's, byte for byte — only stderr is captured, because that is
# where git puts the text the retry decision reads. Merging the two streams would
# hand `hook_git_retry rev-parse HEAD` a stdout git never wrote. The cost of the
# capture is that stderr arrives when the command ends rather than streaming; every
# caller here runs a short, quiet plumbing op, so nothing is waiting on progress.
#
# stderr goes to a FILE rather than a `$(…)` capture, and that choice is load-bearing:
# a command substitution runs git in a subshell, which resets this shell's traps to
# default. `hook_safe_worktree_remove` arms HUP/INT/TERM handlers around exactly the
# `worktree move` this wraps, so the subshell form silently disarmed its interrupt
# recovery — caught as three timed-out signal witnesses in test_lib.sh. Run as a plain
# foreground child, git keeps the trap semantics the callsite had before the retry.
#
# The NOTIFY writer lives in loop_lib.sh, one layer ABOVE this file, and lib.sh must
# not source it (loop_lib.sh depends on lib.sh; the reverse would close a cycle). So
# a caller that sourced only lib.sh has no ledger — reported on stderr through the
# SAME arm as a ledger that refuses the write, because an unrecorded NOTIFY is a lost
# operator signal either way and must never be a silent one.
# Usage: hook_git_retry [-C dir] <git args...>
hook_git_retry() {
  local attempt=0 delay_ms=100 errfile err rc
  errfile=$(mktemp) || { echo "hook_git_retry: could not create a stderr capture" >&2; return 1; }
  while :; do
    git "$@" 2>"$errfile"; rc=$?
    err=$(cat "$errfile")
    { [ "$rc" -eq 0 ] || ! _hook_git_lock_contention "$err"; } && break
    attempt=$((attempt + 1))
    [ -n "${HOOK_GIT_RETRY_TRACE:-}" ] && echo "$attempt" >> "$HOOK_GIT_RETRY_TRACE"
    if [ "$attempt" -ge 8 ]; then
      if ! command -v loop_log_structured >/dev/null 2>&1 \
        || ! loop_log_structured NOTIFY "${HARNESS_LANE_ID:--}" \
               "git-ref-lock:transient-retry:lock_contention" \
               "git $* failed after $attempt lock retries"; then
        echo "hook_git_retry: git $* exhausted $attempt lock retries, and the NOTIFY row could NOT be written" >&2
      fi
      break
    fi
    sleep "$(awk -v d="$delay_ms" -v r="$RANDOM" 'BEGIN { printf "%.3f", (d * (r / 32767)) / 1000 }')"
    delay_ms=$((delay_ms * 2))
    [ "$delay_ms" -gt 5000 ] && delay_ms=5000
  done
  rm -f "$errfile"
  [ -n "$err" ] && printf '%s\n' "$err" >&2
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

hook_checkpoint_generation() {
  local ckdir="$1" lock_timeout="${2:-5}"
  /usr/bin/python3 - "$ckdir/.checkpoint-generation" "$lock_timeout" <<'PY'
import fcntl
import os
import sys
import time
from pathlib import Path

counter = Path(sys.argv[1])
lock = counter.with_name(counter.name + ".lock")
deadline = time.monotonic() + float(sys.argv[2])
counter.parent.mkdir(parents=True, exist_ok=True)
with lock.open("a+") as stream:
    while True:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.monotonic() >= deadline:
                raise SystemExit(75)
            time.sleep(0.01)
    try:
        current = int(counter.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, OSError, ValueError):
        current = 0
    generation = current + 1
    temporary = counter.with_name(f"{counter.name}.tmp-{os.getpid()}")
    temporary.write_text(f"{generation}\n", encoding="utf-8")
    os.replace(temporary, counter)
    print(generation)
PY
}

# Publish a completed checkpoint only when it is not older than the current
# session-specific pointer. The generation travels inside the atomically renamed file,
# so a process death cannot split pointer content from ordering metadata.
hook_publish_checkpoint() {
  local latest="$1" source="$2" generation="$3" lock_timeout="${4:-5}" lock current latest_tmp rc=0
  lock="${latest}.lock"
  exec 8>> "$lock" || return 1
  # The helper and Bash share fd 8's inherited open-file description. The lock
  # therefore remains held by Bash until the explicit close below.
  if ! /usr/bin/python3 - 8 "$lock_timeout" <<'PY'
import fcntl
import sys
import time

fd = int(sys.argv[1])
deadline = time.monotonic() + float(sys.argv[2])
while True:
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        break
    except BlockingIOError:
        if time.monotonic() >= deadline:
            raise SystemExit(75)
        time.sleep(0.01)
PY
  then
    exec 8>&-
    return 1
  fi
  current=$(sed -nE '1s/^<!-- checkpoint-generation: ([0-9]+) -->$/\1/p' "$latest" 2>/dev/null)
  if [ -n "$current" ] && [ "$current" -gt "$generation" ] 2>/dev/null; then
    exec 8>&-
    return 0
  fi
  latest_tmp="${latest}.tmp-$$-${generation}"
  cp "$source" "$latest_tmp" 2>/dev/null \
    && mv "$latest_tmp" "$latest" 2>/dev/null || rc=$?
  [ "$rc" -eq 0 ] || rm -f "$latest_tmp" 2>/dev/null
  exec 8>&-
  return "$rc"
}

# Write a lightweight state snapshot to a collision-free timestamped file plus an atomic,
# session-specific `precompact-latest-<session>.md` pointer. Shared by the compaction hook
# and context-recovery statusline. Args: <label> [skip_gh] [session_id] [publish_timeout].
# With skip_gh non-empty the open-PRs call is omitted because the statusline is a hot path.
hook_write_checkpoint() {
  local label="$1" skip_gh="${2:-}" session publish_timeout="${4:-5}" generation
  session=$(hook_session_key "${3:-shared}")
  local d; d=$(hook_project_dir); [ -n "$d" ] || return 0
  local ckdir="$d/.harness/.checkpoints"
  mkdir -p "$ckdir" 2>/dev/null || return 0
  generation=$(hook_checkpoint_generation "$ckdir" "$publish_timeout") || return 0
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
  local out="$ckdir/precompact-${ts}-${session}-${generation}.md"
  local out_tmp="${out}.tmp-$$"
  local latest="$ckdir/precompact-latest-${session}.md"
  {
    echo "<!-- checkpoint-generation: ${generation} -->"
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
  hook_publish_checkpoint "$latest" "$out" "$generation" "$publish_timeout" || true
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
_WORKTREE_STARTING_LEASE_WINDOW_MIN="${HARNESS_WORKTREE_STARTING_LEASE_WINDOW_MIN:-3}"

_hook_canonical_worktree() {
  local wt="$1" parent base
  (cd "$wt" 2>/dev/null && pwd -P) && return 0
  parent=$(dirname "$wt")
  base=$(basename "$wt")
  parent=$(cd "$parent" 2>/dev/null && pwd -P) || { printf '%s' "$wt"; return 0; }
  printf '%s/%s' "$parent" "$base"
}

_hook_worktree_session_dir() {
  local wt abs common git_dir key
  wt="$1"; abs=$(_hook_canonical_worktree "$wt")
  common=$(git -C "$abs" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) \
    || return 1
  git_dir=$(git -C "$abs" rev-parse --path-format=absolute --absolute-git-dir 2>/dev/null) \
    || return 1
  key=$(printf '%s' "$git_dir" | shasum -a 256 2>/dev/null | cut -d' ' -f1)
  [ -n "$key" ] || return 1
  printf '%s/codex-worktree-sessions/%s' "$common" "$key"
}

# A kernel-owned per-worktree mutex orders SessionStart lease registration against
# removal. The persistent file is only an inode; fcntl releases ownership on process
# death, so no age-based pathname reclamation can steal a live remover's lock.
hook_worktree_lock_acquire() {
  local wt="$1" session_dir
  [ -z "${HOOK_WORKTREE_LOCK_FD:-}" ] || return 1
  session_dir=$(_hook_worktree_session_dir "$wt") || return 1
  _hook_worktree_lock_acquire_session_dir "$session_dir"
}

_hook_worktree_lock_acquire_session_dir() {
  local session_dir="$1" lock timeout
  [ -z "${HOOK_WORKTREE_LOCK_FD:-}" ] || return 1
  mkdir -p "$session_dir" 2>/dev/null || return 1
  lock="$session_dir/remove.lock"
  timeout="${HARNESS_WORKTREE_LOCK_TIMEOUT_SECONDS:-30}"
  exec 9>> "$lock" || return 1
  # The helper and Bash share fd 9's inherited open-file description. The lock
  # therefore remains held by Bash until hook_worktree_lock_release closes it.
  if ! /usr/bin/python3 - 9 "$timeout" <<'PY'
import fcntl
import sys
import time

fd = int(sys.argv[1])
deadline = time.monotonic() + float(sys.argv[2])
while True:
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        break
    except BlockingIOError:
        if time.monotonic() >= deadline:
            raise SystemExit(1)
        time.sleep(0.05)
PY
  then
    exec 9>&-
    return 1
  fi
  HOOK_WORKTREE_LOCK_FD=9
  return 0
}

hook_worktree_lock_release() {
  [ -n "${HOOK_WORKTREE_LOCK_FD:-}" ] || return 0
  exec 9>&-
  HOOK_WORKTREE_LOCK_FD=""
}

_hook_active_lease_live() {
  local lease="$1" owner_pid
  owner_pid=$(sed -n '3p' "$lease" 2>/dev/null || true)
  # Legacy active leases did not record an owner and remain fail-closed.
  [ -n "$owner_pid" ] || return 0
  case "$owner_pid" in *[!0-9]*) return 0 ;; esac
  # PID reuse is conservative: it can retain a stale lease longer, never make a live
  # session reapable. Once the recorded process is absent, the lease is inactive.
  kill -0 "$owner_pid" 2>/dev/null
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
  local wt="$1" session session_dir registered_dir lease tmp pointer pointer_tmp
  local canonical phase registered_worktree rc=0
  session=$(hook_session_key "$2")
  session_dir=$(_hook_worktree_session_dir "$wt") || return 1
  pointer=$(_hook_session_pointer_file "$session") || return 1
  hook_worktree_lock_acquire "$wt" || return 1
  registered_dir=$(_hook_worktree_session_dir "$wt" 2>/dev/null || true)
  if [ -z "$registered_dir" ] || [ "$registered_dir" != "$session_dir" ] \
    || [ "$(git -C "$wt" rev-parse --is-inside-work-tree 2>/dev/null)" != "true" ]; then
    hook_worktree_lock_release || true
    return 1
  fi
  canonical=$(_hook_canonical_worktree "$wt")
  lease="$session_dir/session-${session}.lease"; tmp="${lease}.tmp-$$"
  phase=$(head -n1 "$lease" 2>/dev/null || true)
  registered_worktree=$(sed -n '2p' "$lease" 2>/dev/null || true)
  if [ "$phase" = "active" ] && [ "$registered_worktree" = "$canonical" ] \
    && _hook_active_lease_live "$lease"; then
    # SessionStart fires again after compact for the same root session. Preserve the
    # already-active lease and tell the wrapper it does not own startup cleanup.
    rc=10
  else
    printf 'starting\n%s\n' "$canonical" > "$tmp" 2>/dev/null \
      && mv "$tmp" "$lease" 2>/dev/null || rc=$?
    [ "$rc" -eq 0 ] || rm -f "$tmp" 2>/dev/null
  fi
  if [ "$rc" -eq 0 ] || [ "$rc" -eq 10 ]; then
    pointer_tmp="${pointer}.tmp-$$"
    printf '%s\n' "$lease" > "$pointer_tmp" 2>/dev/null \
      && mv "$pointer_tmp" "$pointer" 2>/dev/null || {
        rc=1
        rm -f "$pointer_tmp" 2>/dev/null
      }
  fi
  hook_worktree_lock_release || true
  return "$rc"
}

hook_activate_session_lease() {
  local wt="$1" session session_dir registered_dir lease tmp phase rc=0
  local owner_pid
  session=$(hook_session_key "$2")
  session_dir=$(_hook_worktree_session_dir "$wt") || return 1
  hook_worktree_lock_acquire "$wt" || return 1
  registered_dir=$(_hook_worktree_session_dir "$wt" 2>/dev/null || true)
  if [ -z "$registered_dir" ] || [ "$registered_dir" != "$session_dir" ] \
    || [ "$(git -C "$wt" rev-parse --is-inside-work-tree 2>/dev/null)" != "true" ]; then
    hook_worktree_lock_release || true
    return 1
  fi
  lease="$session_dir/session-${session}.lease"
  [ -f "$lease" ] || { hook_worktree_lock_release || true; return 1; }
  phase=$(head -n1 "$lease" 2>/dev/null)
  case "$phase" in
    active) ;;
    starting)
      owner_pid="${HARNESS_CODEX_SESSION_OWNER_PID:-}"
      case "$owner_pid" in ''|*[!0-9]*) rc=1 ;; esac
      tmp="${lease}.tmp-$$"
      if [ "$rc" -eq 0 ]; then
        printf 'active\n%s\n%s\n' \
          "$(_hook_canonical_worktree "$wt")" "$owner_pid" \
          > "$tmp" 2>/dev/null && mv "$tmp" "$lease" 2>/dev/null || rc=$?
      fi
      [ "$rc" -eq 0 ] || rm -f "$tmp" 2>/dev/null
      ;;
    *) rc=1 ;;
  esac
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

# Ignored entries matching this regenerable allowlist are safe to discard with a completed
# worktree. Everything else is local state because `git worktree remove` deletes ignored
# files without requiring --force. This is the single filter used before and under the
# removal mutex.
_HOOK_REGEN_IGNORED='^!! (.*/)?(\.harness/|__pycache__/|.*\.py[co]|.*\.egg-info/|\.pytest_cache/|\.ruff_cache/|\.pyright/|\.mypy_cache/|\.venv/|venv/|env/|dist/|build/|htmlcov/|coverage\.xml|\.coverage|\.DS_Store|.*\.swp|\.vscode/|\.idea/|node_modules/)|^!! (\.claude/(skills/|settings\.local\.json|scheduled_tasks\.lock)|\.impeccable/)'

# Print reap-blocking local state. Return 0 when residue exists, 1 when clean, and 2 when
# status cannot be established. Callers must treat 2 as fail-closed.
hook_worktree_local_state() {
  local wt="$1" raw line residue=""
  raw=$(git -C "$wt" status --porcelain --ignored 2>/dev/null) || return 2
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    if printf '%s\n' "$line" | grep -Eq "$_HOOK_REGEN_IGNORED"; then
      continue
    fi
    residue="${residue}${residue:+
}${line}"
  done <<EOF
$raw
EOF
  # C-HE-04 §6: committed-but-unpushed commits are capture that a later branch
  # prune could lose -- with an upstream, ahead-of-@{u} is refusal residue. A
  # worktree with NO upstream keeps today's behavior (the spec scopes this check
  # to `rev-list @{u}..HEAD`; the never-pushed-branch composition is a registered
  # residual -- refusing it would refuse every local-only scratch worktree; plan
  # U-HE-15 Step 4b rev 2026-08-19). An upstream that RESOLVES but whose ahead
  # count cannot be computed is fail-closed residue, never a clean verdict.
  # A DETACHED HEAD is refusal residue outright: no branch ref survives the
  # worktree, so disposal would drop the commits' only reference -- the branch-
  # survives rationale above does not cover it.
  if ! git -C "$wt" symbolic-ref -q HEAD >/dev/null 2>&1; then
    residue="${residue}${residue:+
}detached HEAD (commits would lose their only ref)"
  fi
  # The presence gate is the CONFIG (branch.<name>.merge), never @{u} resolution:
  # the remote-tracking ref is pruned by this repo's own post-merge branch-prune
  # flow while the config persists, and a resolution-gated check would then fail
  # OPEN on genuinely unpushed commits (merge-gate L1, PR #1403).
  local ahead branch upstream_cfg
  branch=$(git -C "$wt" symbolic-ref --short -q HEAD) || branch=""
  upstream_cfg=""
  [ -n "$branch" ] && upstream_cfg=$(git -C "$wt" config --get "branch.${branch}.merge" 2>/dev/null) || true
  if [ -n "$upstream_cfg" ]; then
    if ahead=$(git -C "$wt" rev-list --count '@{u}..HEAD' 2>/dev/null); then
      if [ "${ahead:-0}" -gt 0 ]; then
        residue="${residue}${residue:+
}ahead-of-upstream: ${ahead} commit(s)"
      fi
    else
      residue="${residue}${residue:+
}upstream configured but unresolvable (cannot verify pushed; fail-closed)"
    fi
  fi
  [ -n "$residue" ] || return 1
  printf '%s\n' "$residue"
  return 0
}

# Choose an unpublished sibling path on the same filesystem. Moving the registered
# worktree here closes new lookups through the original pathname before the authoritative
# scan. Pre-resolved process references are checked separately before deletion.
_hook_worktree_quarantine_path() {
  local wt="$1" parent base candidate attempt=0
  parent=$(dirname "$wt")
  base=$(basename "$wt")
  while [ "$attempt" -lt 100 ]; do
    candidate="${parent}/.harness-removing-${base}-$$-${attempt}"
    if [ ! -e "$candidate" ]; then
      printf '%s' "$candidate"
      return 0
    fi
    attempt=$((attempt + 1))
  done
  return 1
}

# Return 0 when a same-user process retains a cwd/root/fd/mapping inside the quarantined tree,
# 1 when none do, and 2 when the observation cannot be completed. Namespace closure
# means every writer that can still reach the moved tree must retain such a kernel
# reference. Linux exposes those references through procfs; macOS uses its system lsof.
_hook_worktree_open_references() {
  local wt="$1" abs output rc lsof_bin=""
  abs=$(_hook_canonical_worktree "$wt")
  if [ -d /proc/self/fd ]; then
    /usr/bin/python3 - "$abs" <<'PY'
import os
import sys
from pathlib import Path

target = os.path.realpath(sys.argv[1])
uid = os.geteuid()
unknown = False


def inside_target(candidate: str) -> bool:
    if candidate.endswith(" (deleted)"):
        candidate = candidate[: -len(" (deleted)")]
    if not os.path.isabs(candidate):
        return False
    candidate = os.path.normpath(candidate)
    try:
        return os.path.commonpath((target, candidate)) == target
    except ValueError:
        return False

for process in Path("/proc").iterdir():
    if not process.name.isdigit():
        continue
    try:
        if process.stat().st_uid != uid:
            continue
    except FileNotFoundError:
        continue
    except OSError:
        unknown = True
        continue
    links = [process / "cwd", process / "root"]
    try:
        links.extend((process / "fd").iterdir())
    except FileNotFoundError:
        continue
    except OSError:
        unknown = True
    for link in links:
        try:
            candidate = os.readlink(link)
        except FileNotFoundError:
            continue
        except OSError:
            unknown = True
            continue
        if inside_target(candidate):
            print(process.name)
            raise SystemExit(0)
    try:
        maps = (process / "maps").read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        continue
    except OSError:
        unknown = True
        continue
    for mapping in maps:
        fields = mapping.split(maxsplit=5)
        if len(fields) == 6 and inside_target(fields[5]):
            print(process.name)
            raise SystemExit(0)

raise SystemExit(20 if unknown else 10)
PY
    rc=$?
    case "$rc" in
      0) return 0 ;;
      10) return 1 ;;
      *) return 2 ;;
    esac
  fi
  if [ -x /usr/sbin/lsof ]; then
    lsof_bin=/usr/sbin/lsof
  elif command -v lsof >/dev/null 2>&1; then
    lsof_bin=$(command -v lsof)
  else
    return 2
  fi
  _hook_worktree_lsof_references "$abs" "$lsof_bin"
  return $?
}

_hook_worktree_lsof_references() {
  local abs="$1" lsof_bin="$2" output rc
  output=$(hook_bounded "${HARNESS_WORKTREE_REFERENCE_SCAN_TIMEOUT_SECONDS:-5}" \
    "$lsof_bin" -w -nP -t +D "$abs" 2>&1)
  rc=$?
  if [ -n "$output" ]; then
    printf '%s\n' "$output" | grep -Eqv '^[0-9]+$' && return 2
    return 0
  fi
  case "$rc" in
    0|1) return 1 ;;
    *) return 2 ;;
  esac
}

_hook_worktree_transaction_file() {
  local session_dir
  session_dir=$(_hook_worktree_session_dir "$1") || return 1
  printf '%s/remove.transaction' "$session_dir"
}

_hook_worktree_transaction_for_original() {
  local root="$1" original="$2" common transaction recorded
  common=$(git -C "$root" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) \
    || return 1
  for transaction in "$common"/codex-worktree-sessions/*/remove.transaction; do
    [ -f "$transaction" ] || continue
    recorded=$(sed -n '1p' "$transaction" 2>/dev/null)
    if [ "$recorded" = "$original" ]; then
      printf '%s' "$transaction"
      return 0
    fi
  done
  return 1
}

_hook_worktree_registered_path() {
  local root="$1" wanted="$2" line raw
  raw=$(git -C "$root" worktree list --porcelain 2>/dev/null) || return 2
  while IFS= read -r line; do
    [ "$line" = "worktree $wanted" ] && return 0
  done <<EOF
$raw
EOF
  return 1
}

_hook_worktree_write_transaction() {
  local transaction="$1" original="$2" quarantine="$3" tmp
  case "${original}${quarantine}" in *$'\n'*) return 1 ;; esac
  tmp="${transaction}.tmp-$$"
  printf '%s\n%s\n' "$original" "$quarantine" > "$tmp" 2>/dev/null \
    && mv "$tmp" "$transaction" 2>/dev/null || {
      rm -f "$tmp" 2>/dev/null
      return 1
    }
}

# Restore a process-death-recoverable in-flight transaction. Return 0 after restoring a moved worktree,
# 1 when a pre-move marker was merely cleared, and 2 when recovery is unsafe.
_hook_worktree_restore_transaction() {
  local root="$1" transaction="$2" original quarantine third original_rc quarantine_rc
  [ -f "$transaction" ] || return 1
  original=$(sed -n '1p' "$transaction" 2>/dev/null)
  quarantine=$(sed -n '2p' "$transaction" 2>/dev/null)
  third=$(sed -n '3p' "$transaction" 2>/dev/null)
  [ -n "$original" ] && [ -n "$quarantine" ] && [ -z "$third" ] || return 2
  case "$original" in /*) ;; *) return 2 ;; esac
  case "$quarantine" in
    "$(dirname "$original")"/.harness-removing-*) ;;
    *) return 2 ;;
  esac
  [ "$original" != "$quarantine" ] || return 2

  _hook_worktree_registered_path "$root" "$quarantine"
  quarantine_rc=$?
  _hook_worktree_registered_path "$root" "$original"
  original_rc=$?
  [ "$quarantine_rc" -ne 2 ] && [ "$original_rc" -ne 2 ] || return 2

  if [ "$quarantine_rc" -eq 0 ]; then
    [ ! -e "$original" ] || return 2
    git -C "$root" worktree move "$quarantine" "$original" >/dev/null 2>&1 || return 2
    rm -f "$transaction" 2>/dev/null || return 2
    printf '%s' "$original"
    return 0
  fi
  if [ "$original_rc" -eq 0 ] && [ "$quarantine_rc" -eq 1 ] \
    && [ ! -e "$original" ] && [ -d "$quarantine" ]; then
    # Git may die after its filesystem rename but before updating the worktree admin
    # path. Restore the physical tree to the still-registered original path directly;
    # `git worktree move` cannot address this split-brain state.
    /bin/mv "$quarantine" "$original" 2>/dev/null || return 2
    _hook_worktree_registered_path "$root" "$original" || return 2
    rm -f "$transaction" 2>/dev/null || return 2
    printf '%s' "$original"
    return 0
  fi
  if [ "$original_rc" -eq 0 ] && [ ! -e "$quarantine" ]; then
    rm -f "$transaction" 2>/dev/null || return 2
    return 1
  fi
  if [ "$original_rc" -eq 1 ] && [ "$quarantine_rc" -eq 1 ] \
    && [ ! -e "$original" ] && [ ! -e "$quarantine" ]; then
    rm -f "$transaction" 2>/dev/null || return 2
    return 1
  fi
  return 2
}

_hook_worktree_interrupted() {
  local rc="$1"
  trap - HUP INT TERM
  _hook_worktree_restore_transaction "$_HOOK_REMOVE_ROOT" \
    "$_HOOK_REMOVE_TRANSACTION" >/dev/null 2>&1 || rc=6
  hook_worktree_lock_release || true
  exit "$rc"
}

_hook_worktree_matches_expected_identity() {
  local wt="$1" expected_branch="$2" expected_head="$3" branch head
  [ -n "$expected_branch" ] && [ -n "$expected_head" ] || return 0
  branch=$(git -C "$wt" symbolic-ref --quiet --short HEAD 2>/dev/null) || return 2
  head=$(git -C "$wt" rev-parse HEAD 2>/dev/null) || return 2
  [ "$branch" = "$expected_branch" ] && [ "$head" = "$expected_head" ]
}

# Release the lane-index claim (C-HE-11 §1) a worktree holds at QUEUE_DIR/lanes/<k>,
# matching on the PHYSICAL path recorded by tools/hooks/lane-init.sh. Called after a
# successful worktree removal: an unreleased entry burns an index forever, and the next
# lane silently starts one higher until the 350 ceiling refuses to open a lane at all.
# EVERY matching entry goes, not the first: a crash between the exclusive create and the
# reuse scan can leave one path holding two, and a release that stops at the first would
# strand the other. Never fails the caller — teardown already succeeded.
# BOUND: this frees the INDEX, it does not stop that lane's Docker stack — reaping a
# worktree whose stack is still up leaves containers holding the ports and volumes the
# freed index hands to the next lane, whose `up` then fails on a port bind. Bringing Docker
# down from a removal hook would make teardown depend on a daemon that is usually absent,
# so the stack-down is a documented step of the reaping recipe instead
# (.claude/skills/two-lane/SKILL.md), and the failure it guards against is loud, not silent.
# The "it would fail loudly" argument for leaving containers alone is FALSE: `docker compose
# up -d` under an existing project ADOPTS its containers rather than refusing, so a lane
# handed a recycled index would silently inherit a dead lane's containers, volumes and
# state. So the release takes the stack down first — but only in the one condition where
# containers can actually exist (a reachable daemon), and always bounded, so a teardown on
# a machine with no Docker, or with the daemon down, costs nothing and cannot hang.
# Usage: hook_release_lane_index /physical/path/to/worktree
hook_release_lane_index() {
  local wt="${1:-}" q f id path _rc _now_id _now_path
  [ -n "$wt" ] || return 0
  q="${ARC_METRICS_QUEUE_DIR:-$HOME/.gstack/projects/arhugula-v2/arc-metrics-queue}/lanes"
  [ -d "$q" ] || return 0
  for f in "$q"/*; do
    [ -f "$f" ] || continue
    IFS=' ' read -r id path < "$f"
    if [ "${path:-}" = "$wt" ]; then
      # The claim is freed ONLY when the stack is known not to be in the way. A cleanup
      # that was ATTEMPTED and failed leaves containers holding this project's ports and
      # volumes, so recycling the index would hand them to the next lane; the claim is kept
      # instead — a visible, retryable state rather than a silent cross-lane adoption.
      # Ownership is checked BEFORE the destructive cleanup as well as after. `down --volumes`
      # can run for minutes, and a worktree recreated at this path may have already rebound
      # the claim and started its own stack — the post-check protects its CLAIM but cannot
      # un-destroy its containers. Re-reading first shrinks that window to the gap between
      # this read and the compose call; the remainder is a registered residual (B-202).
      IFS=' ' read -r _now_id _now_path < "$f" 2>/dev/null
      if [ "${_now_path:-}" != "$wt" ] || [ "${_now_id:-}" != "${id:-}" ]; then
        echo "hook_release_lane_index: claim $(basename "$f") was rebound before cleanup — leaving the new owner's stack and record alone" >&2
        continue
      fi
      _hook_lane_stack_down "$(basename "$f")" >/dev/null 2>&1
      _rc=$?
      # Docker cleanup can take minutes. RE-READ the claim before removing it: a worktree
      # recreated at this path during that window rebinds the claim to itself, and deleting
      # it then would strip the NEW lane's ownership record and free its index to a peer.
      IFS=' ' read -r _now_id _now_path < "$f" 2>/dev/null
      if [ "${_now_path:-}" != "$wt" ] || [ "${_now_id:-}" != "${id:-}" ]; then
        echo "hook_release_lane_index: claim $(basename "$f") was rebound during cleanup — leaving the new owner's record alone" >&2
        continue
      fi
      case "$_rc" in
        0) # Verified clean. A release that cannot REMOVE the claim has not released
           # anything: the index stays consumed after its worktree is gone, with no marker
           # and no retry path, so it is burned permanently. Say so rather than returning
           # success on a stale claim.
           if ! rm -f "$f" 2>/dev/null || [ -e "$f" ]; then
             echo "hook_release_lane_index: lane $(basename "$f") cleaned, but its claim could NOT be removed — the index stays consumed until $f is deleted by hand" >&2
           fi ;;
        *) # NOT verified clean — whether the cleanup failed outright or could not be
           # attempted. Either way the index must not be handed on unfenced: a claim can be
           # inherited by a new worktree created at the SAME path (reuse is by path), which
           # would adopt the surviving containers along with the index. So the obligation is
           # recorded first, and the claim is released ONLY if that record actually landed —
           # an unwritable marker leaves the claim in place rather than removing both fences.
           if printf '%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ) reaped $wt" \
                > "$q/.orphaned-$(basename "$f")" 2>/dev/null; then
             rm -f "$f" 2>/dev/null
           else
             echo "hook_release_lane_index: lane $(basename "$f") stack is unverified AND its orphan marker could not be written — index kept claimed" >&2
           fi ;;
      esac
    fi
  done
  return 0
}

# Bring lane <k>'s Compose stack down before its index is recycled.
#   0 = verified clean (nothing could exist, or `down --volumes` succeeded)
#   1 = attempted and FAILED — containers may survive; the caller must keep the claim
#   2 = could not VERIFY (no reachable daemon) — the caller records a deferred obligation
# Only the total absence of a docker binary counts as "nothing can exist". A daemon that
# answers non-zero is NOT proof: a stopped daemon still retains this project's containers
# and named volumes, which a later `up` would adopt. The project NAME is resolved by
# tools/lane_ports.py — the one authority for it — never re-spelled here, because a second
# spelling would silently stop targeting the real project the day the formula changes.
_hook_lane_stack_down() {
  local k="${1:-}" root project compose
  case "$k" in ''|*[!0-9]*) return 0 ;; esac
  # A missing docker EXECUTABLE is not proof that no docker STATE exists: hooks often run
  # with a reduced PATH, and a client can be removed while its containers and volumes remain.
  # Unverifiable, therefore fenced — on a machine that genuinely has no Docker the fence
  # costs nothing, because there is no stack for the next lane to bring up either.
  command -v docker >/dev/null 2>&1 || return 2
  root=$(hook_project_dir); [ -n "$root" ] || return 2
  compose="$root/deploy/self-hosted-local/compose.yaml"
  { [ -f "$compose" ] && [ -f "$root/tools/lane_ports.py" ]; } || return 2
  # A daemon that answers "unreachable" quickly is proof no container of this project is
  # running, and skipping is free. A probe that TIMES OUT proves nothing — the daemon may be
  # alive and slow, still holding this lane's containers — so it is a cleanup FAILURE, which
  # keeps the claim rather than recycling an index under live containers.
  hook_bounded 15 docker info >/dev/null 2>&1
  case $? in
    0) ;;         # daemon up: proceed to bring the project down
    *) return 2 ;;  # unreachable / slow / permission-denied: unverifiable, not proof of clean
  esac
  project=$(HARNESS_LANE_INDEX="$k" python3 "$root/tools/lane_ports.py" --project 2>/dev/null)
  [ -n "$project" ] || return 2
  # --volumes as well as the containers: grafana-data / tempo-data are declared named
  # volumes, so a plain `down` leaves them under the project name and the next lane handed
  # that index inherits the previous lane's persistent dashboards and traces. The lane is
  # gone for good at this point — its state is not something to preserve.
  if ! hook_bounded 180 docker compose -p "$project" -f "$compose" down --volumes >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

# Remove a registered worktree only while holding the same mutex used by SessionStart
# lease registration. The worktree is moved to an unpublished sibling quarantine before
# the final status and open-reference scans. Return 2 when the mutex is unavailable, 3
# for a live session, 4 for local state, 5 when status is unavailable, 6 when quarantine
# restoration fails, 7 for a retained process reference, 8 after recovering an interrupted
# quarantine, 9 when open-reference status is unavailable, 10 when the branch or HEAD
# changed after candidate classification, otherwise return git's status.
hook_safe_worktree_remove() {
  local root="$1" wt="$2" expected_branch="${3:-}" expected_head="${4:-}"
  local rc state_rc quarantine restore_rc transaction reference_rc session_dir identity_rc
  root=$(_hook_canonical_worktree "$root")
  wt=$(_hook_canonical_worktree "$wt")
  if [ ! -e "$wt" ]; then
    transaction=$(_hook_worktree_transaction_for_original "$root" "$wt") || return 2
    session_dir=$(dirname "$transaction")
    _hook_worktree_lock_acquire_session_dir "$session_dir" || return 2
    _hook_worktree_restore_transaction "$root" "$transaction" >/dev/null
    rc=$?
    hook_worktree_lock_release || true
    case "$rc" in
      0|1) return 8 ;;
      *) return 6 ;;
    esac
  fi
  hook_worktree_lock_acquire "$wt" || return 2
  transaction=$(_hook_worktree_transaction_file "$wt") || {
    hook_worktree_lock_release || true
    return 2
  }
  if [ -f "$transaction" ]; then
    _hook_worktree_restore_transaction "$root" "$transaction" >/dev/null
    rc=$?
    hook_worktree_lock_release || true
    case "$rc" in
      0) return 8 ;;
      1) return 8 ;;
      *) return 6 ;;
    esac
  fi
  _hook_worktree_matches_expected_identity "$wt" "$expected_branch" "$expected_head"
  identity_rc=$?
  if [ "$identity_rc" -ne 0 ]; then
    hook_worktree_lock_release || true
    [ "$identity_rc" -eq 1 ] && return 10
    return 5
  fi
  hook_prune_stale_starting_leases "$wt"
  if worktree_has_live_session "$wt"; then
    hook_worktree_lock_release || true
    return 3
  fi
  hook_worktree_local_state "$wt" >/dev/null
  state_rc=$?
  case "$state_rc" in
    0)
      hook_worktree_lock_release || true
      return 4
      ;;
    1) ;;
    *)
      hook_worktree_lock_release || true
      return 5
      ;;
  esac
  quarantine=$(_hook_worktree_quarantine_path "$wt") || {
    hook_worktree_lock_release || true
    return 6
  }
  _hook_worktree_write_transaction "$transaction" "$wt" "$quarantine" || {
    hook_worktree_lock_release || true
    return 6
  }
  _HOOK_REMOVE_ROOT="$root"
  _HOOK_REMOVE_TRANSACTION="$transaction"
  trap '_hook_worktree_interrupted 129' HUP
  trap '_hook_worktree_interrupted 130' INT
  trap '_hook_worktree_interrupted 143' TERM
  hook_git_retry -C "$root" worktree move "$wt" "$quarantine"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    rm -f "$transaction" 2>/dev/null
    trap - HUP INT TERM
    hook_worktree_lock_release || true
    return "$rc"
  fi
  _hook_worktree_open_references "$quarantine" >/dev/null
  reference_rc=$?
  case "$reference_rc" in
    0) rc=7 ;;
    1)
      hook_worktree_local_state "$quarantine" >/dev/null
      state_rc=$?
      case "$state_rc" in
        0) rc=4 ;;
        1)
          _hook_worktree_matches_expected_identity "$quarantine" "$expected_branch" "$expected_head"
          identity_rc=$?
          case "$identity_rc" in
            0)
              hook_git_retry -C "$root" worktree remove "$quarantine"
              rc=$?
              ;;
            1) rc=10 ;;
            *) rc=5 ;;
          esac
          ;;
        *) rc=5 ;;
      esac
      ;;
    *) rc=9 ;;
  esac
  if [ "$rc" -eq 0 ]; then
    # The lane-index release lives HERE, not in the safe-worktree-remove.sh wrapper:
    # loop_gc_worktrees calls this function directly, and a release attached to the wrapper
    # alone would let every GC-reaped lane leak its index permanently.
    hook_release_lane_index "$wt"
    rm -f "$transaction" 2>/dev/null || rc=6
  elif [ -d "$quarantine" ]; then
    _hook_worktree_restore_transaction "$root" "$transaction" >/dev/null
    restore_rc=$?
    [ "$restore_rc" -eq 0 ] || rc=6
  fi
  trap - HUP INT TERM
  hook_worktree_lock_release || true
  return "$rc"
}

hook_prune_stale_starting_leases() {
  local wt="$1" session_dir lease phase session pointer
  session_dir=$(_hook_worktree_session_dir "$wt" 2>/dev/null || true)
  [ -n "$session_dir" ] || return 0
  for lease in "$session_dir"/session-*.lease; do
    [ -f "$lease" ] || continue
    phase=$(head -n1 "$lease" 2>/dev/null)
    [ "$phase" = "starting" ] || continue
    find "$lease" -maxdepth 0 -mmin "-${_WORKTREE_STARTING_LEASE_WINDOW_MIN}" -print -quit \
      2>/dev/null | grep -q . && continue
    session=${lease##*/session-}; session=${session%.lease}
    pointer=$(_hook_session_pointer_file "$session" 2>/dev/null || true)
    rm -f "$lease" "$pointer" 2>/dev/null
  done
}

# Live-session detection covers both runners: Claude's encoded project transcripts,
# Codex's date-partitioned rollout transcripts (`session_meta.payload.cwd`), and the
# SessionStart/SessionEnd lease used to close the transcript check/remove race. Active
# leases remain authoritative while their recorded Codex owner process identity is live;
# abnormal owner exit makes a new-format active lease inactive. A starting lease uses a
# bounded grace window longer than the host's SessionStart timeout, so a killed startup
# cannot strand the worktree forever; only the lock holder prunes an abandoned start.
worktree_has_live_session() {
  local wt="$1"
  [ -n "$wt" ] || return 1
  command -v find >/dev/null 2>&1 || return 1
  local abs; abs=$(cd "$wt" 2>/dev/null && pwd -P) || abs="$wt"
  local session_dir lease phase
  session_dir=$(_hook_worktree_session_dir "$abs" 2>/dev/null || true)
  if [ -n "$session_dir" ]; then
    for lease in "$session_dir"/session-*.lease; do
      [ -f "$lease" ] || continue
      phase=$(head -n1 "$lease" 2>/dev/null)
      case "$phase" in
        starting)
          find "$lease" -maxdepth 0 -mmin "-${_WORKTREE_STARTING_LEASE_WINDOW_MIN}" \
            -print -quit 2>/dev/null | grep -q . && return 0
          ;;
        active) _hook_active_lease_live "$lease" && return 0 ;;
        *) return 0 ;; # pre-phase lease files are active for backward compatibility
      esac
    done
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

#!/usr/bin/env bash
# Unit tests for tools/hooks/lib.sh. Hermetic (no network; temp git repo for the
# branch/loop-marker cases). Exits non-zero on any failed assertion (CI-friendly).

set -uo pipefail
# This suite exercises production behavior even when a merge-gate reviewer launches it.
unset HARNESS_CODEX_REVIEW_ISOLATED
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/lib.sh"

# Safe-removal tests exercise the transaction, mutex, identity, and quarantine
# paths with a deterministic clean reference scan. The dedicated retained-cwd,
# mmap, unavailable-observer, and lsof-timeout witnesses below exercise the real
# production observer separately. This keeps the suite portable to Linux CI
# runners whose ptrace policy makes unrelated same-user /proc entries unreadable.
eval "$(declare -f _hook_worktree_open_references | \
  sed '1s/_hook_worktree_open_references/_hook_worktree_open_references_production/')"
_hook_worktree_open_references() { return 1; }

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
eq()  { [ "$2" = "$3" ] && ok "$1 ($2)" || bad "$1: got '$2' want '$3'"; }
wait_bounded() {
  local pid="$1" seconds="$2" watchdog rc
  ( sleep "$seconds"; kill -KILL "$pid" 2>/dev/null ) &
  watchdog=$!
  wait "$pid" 2>/dev/null
  rc=$?
  kill "$watchdog" 2>/dev/null || true
  wait "$watchdog" 2>/dev/null || true
  [ "$rc" -eq 137 ] && return 124
  return "$rc"
}

# hook_state_hash — deterministic 12-hex, matches the raw recipe.
WANT=$(printf '%s|%s|%s|%s' a b c d | shasum -a 256 | head -c 12)
eq "hook_state_hash matches recipe" "$(hook_state_hash a b c d)" "$WANT"
[ "$(hook_state_hash a b c d | wc -c | tr -d ' ')" = "12" ] && ok "hash is 12 chars" || bad "hash not 12 chars"

# hook_is_roadmap_status_only_set — §12.2.1 closed-set: EXACTLY {roadmap_status.md}.
# Inputs mirror the callers' `sort -u` output.
_STATUS=".harness/roadmap_status.md"
is_set()  { hook_is_roadmap_status_only_set "$1" && ok "status-only: $2" || bad "expected status-only ($2): '$1'"; }
not_set() { hook_is_roadmap_status_only_set "$1" && bad "expected NOT status-only ($2): '$1'" || ok "not status-only: $2"; }
is_set  "$_STATUS"                                  "status-only refresh"
not_set "$(printf '%s\n%s' "$_STATUS" "other.txt")" "status + a foreign file (mis-titled substantive)"
not_set ""                                          "empty set"
not_set "$(printf '%s\n%s' "$_STATUS" "src/x.py")"  "status + extra → closed-set rejects"

# hook_json — extracts a path; empty default on miss.
eq "hook_json extracts command" "$(hook_json '{"tool_input":{"command":"echo hi"}}' '.tool_input.command')" "echo hi"
eq "hook_json empty on miss"    "$(hook_json '{"a":1}' '.tool_input.command')" ""
eq "hook_json empty on junk"    "$(hook_json 'not json' '.x')" ""

# hook_read_stdin — round-trips stdin.
eq "hook_read_stdin round-trips" "$(printf 'payload-x' | hook_read_stdin)" "payload-x"

# hook_emit — emits the additionalContext JSON and exits 0 (captured in a subshell).
OUT=$(hook_emit "SessionStart" "hello world")
echo "$OUT" | jq -e '.hookSpecificOutput.hookEventName=="SessionStart" and .hookSpecificOutput.additionalContext=="hello world"' >/dev/null \
  && ok "hook_emit JSON shape" || bad "hook_emit bad JSON: $OUT"

# hook_bounded — a fast command returns 0; a slow command is killed within the bound.
hook_bounded 5 true && ok "hook_bounded fast cmd rc=0" || bad "hook_bounded fast cmd nonzero"
SECONDS=0
hook_bounded 1 sleep 10 >/dev/null 2>&1; RC=$?
EL=$SECONDS
{ [ "$EL" -lt 5 ] && [ "$RC" -ne 0 ]; } && ok "hook_bounded kills slow cmd (~${EL}s, rc=$RC)" \
  || bad "hook_bounded did not bound: elapsed=${EL}s rc=$RC"

# hook_project_dir — honors CLAUDE_PROJECT_DIR override.
eq "hook_project_dir honors env" "$(CLAUDE_PROJECT_DIR=/tmp/xyz hook_project_dir)" "/tmp/xyz"

# hook_bounded — force-kills a TERM-ignoring command within the bound (escalation).
SECONDS=0
hook_bounded 1 bash -c 'trap "" TERM; sleep 30' >/dev/null 2>&1; RC2=$?
EL2=$SECONDS
{ [ "$EL2" -lt 8 ] && [ "$RC2" -ne 0 ]; } && ok "hook_bounded escalates TERM->KILL (~${EL2}s, rc=$RC2)" \
  || bad "hook_bounded did not force-kill TERM-ignorer: elapsed=${EL2}s rc=$RC2"

# Temp repo for default-branch + loop-mode marker tests.
REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
git -C "$REPO" init -q -b main; git -C "$REPO" config user.email t@t.t; git -C "$REPO" config user.name t
( cd "$REPO" && echo x > f && git add -A && git commit -qm base )

# The macOS lsof observation must have a hard bound and fail closed on timeout.
SLOW_LSOF="$REPO/slow-lsof"
LSOF_READY="$REPO/slow-lsof.ready"
cat > "$SLOW_LSOF" <<'EOF'
#!/usr/bin/env bash
trap '' TERM
: > "$LSOF_READY"
sleep 30
EOF
chmod +x "$SLOW_LSOF"
export LSOF_READY
LSOF_STARTED=$(/usr/bin/python3 -c 'import time; print(time.monotonic_ns())')
_hook_worktree_lsof_references "$REPO" "$SLOW_LSOF" >/dev/null 2>&1 &
LSOF_PID=$!
for _ in $(seq 1 100); do
  [ -f "$LSOF_READY" ] && break
  sleep 0.01
done
if [ ! -f "$LSOF_READY" ]; then
  kill -KILL "$LSOF_PID" 2>/dev/null || true
  wait "$LSOF_PID" 2>/dev/null || true
  bad "lsof timeout fixture did not reach its TERM-resistant state"
  LSOF_RC=1
else
  wait_bounded "$LSOF_PID" 12
  LSOF_RC=$?
fi
LSOF_FINISHED=$(/usr/bin/python3 -c 'import time; print(time.monotonic_ns())')
LSOF_ELAPSED_MS=$(( (LSOF_FINISHED - LSOF_STARTED) / 1000000 ))
{ [ "$LSOF_RC" -eq 2 ] && [ "$LSOF_ELAPSED_MS" -lt 11000 ]; } \
  && ok "lsof reference observation is bounded and fails closed" \
  || bad "lsof reference observation was not bounded: elapsed=${LSOF_ELAPSED_MS}ms rc=$LSOF_RC"

# hook_default_branch — falls back to main when no origin/HEAD symref.
eq "hook_default_branch fallback main" "$(cd "$REPO" && hook_default_branch)" "main"

# hook_roadmap_next — scopes to the `## Next action` section, so a STALE bolded R-id
# in a later narrative section does NOT shadow the live pointer (the whole-file
# head -1 bug). It also ignores range/banner tokens like `R-410..R-440`; those are
# menus, not actionable roadmap units. Fixture mirrors the real dashboard: a
# backticked range banner + a backticked concrete pointer in the section + a strict
# `**`R-OLD`**` token AFTER the `---` rule.
DASHF="$REPO/dash.md"
cat > "$DASHF" <<'EOF'
# dash
| `git_head` | `abc12345` (main) |
## Next action
> directive prose; pick the highest-value item `R-410..R-440` then `R-300-x`.
---
## Recently completed
**`R-OLD-stale-narrative`** was closed earlier (must NOT be picked).
EOF
eq "hook_roadmap_next skips range token and picks concrete pointer" "$(hook_roadmap_next "$DASHF")" "R-300-x"
cat > "$DASHF" <<'EOF'
# dash
## Next action
**Current next action.** Continue the memory substrate build. U-MEM-09 is merged; the next implementable unit is U-MEM-10, the Information-substrate derived retrieval indexes unit.

**Recurring lanes** continue on cadence: `R-600-pattern-bake-in-sweep` and `R-IF-roadmap-refresh`.
---
EOF
eq "hook_roadmap_next picks U-MEM frontier before recurring R lane" "$(hook_roadmap_next "$DASHF")" "U-MEM-10"
# 2026-07-23 regression: `## Next action` immediately followed by the NEXT `## `
# heading (no `---` between them, the real `roadmap_status.md` shape) must not
# bleed into that next section's own prose — a RESOLVED R-id mentioned there
# (e.g. a "R-CL-Q1 ... is RESOLVED" narrative aside) must NOT be picked up as
# the live next-action when the actual Next action prose uses non-R/U tokens.
cat > "$DASHF" <<'EOF'
# dash
## Next action
**Frontier.** No auto-`ACTIVE` queue item; ground and drive the highest-value `B-*` forward-register row.
## Remaining forward work
`R-CL-Q1`, `R-CL-Q2` are RESOLVED. `R-FS-1` has no forward build arcs remaining.
EOF
eq "hook_roadmap_next stops at next ## heading, no --- present" "$(hook_roadmap_next "$DASHF")" ""
# Absent section / file → empty (callers default to '?').
eq "hook_roadmap_next empty on missing file" "$(hook_roadmap_next "$REPO/nope.md")" ""
printf '# d\nno next-action heading here\n' > "$DASHF"
eq "hook_roadmap_next empty when no section" "$(hook_roadmap_next "$DASHF")" ""

# loop_mode_active — off by default; on via env; on via marker file.
( cd "$REPO"; unset HARNESS_LOOP; CLAUDE_PROJECT_DIR="$REPO" loop_mode_active ) \
  && bad "loop_mode_active true with no gate" || ok "loop_mode_active off by default"
( cd "$REPO"; HARNESS_LOOP=1 loop_mode_active ) && ok "loop_mode_active on via env" || bad "loop_mode_active env ignored"
mkdir -p "$REPO/.harness"; : > "$REPO/.harness/.loop-active"
( cd "$REPO"; unset HARNESS_LOOP; CLAUDE_PROJECT_DIR="$REPO" loop_mode_active ) \
  && ok "loop_mode_active on via marker file" || bad "loop_mode_active marker ignored"

# Merge-gate review isolation is an exact, opt-in environment contract.
( HARNESS_CODEX_REVIEW_ISOLATED=1 hook_review_isolated ) \
  && ok "review isolation marker recognized" || bad "review isolation marker ignored"
( HARNESS_CODEX_REVIEW_ISOLATED=0 hook_review_isolated ) \
  && bad "non-exact review isolation marker accepted" || ok "review isolation requires exact marker"

# Codex stores transcripts in date-partitioned ~/.codex/sessions trees and records cwd
# in session_meta. A recent transcript for this exact worktree must block removal.
FAKE_HOME="$REPO/fake-home"
CODEX_SESSION_DIR="$FAKE_HOME/.codex/sessions/2026/08/01"
mkdir -p "$CODEX_SESSION_DIR"
printf '%s\n' "{\"type\":\"session_meta\",\"payload\":{\"cwd\":\"$REPO\"}}" \
  > "$CODEX_SESSION_DIR/rollout-live.jsonl"
( HOME="$FAKE_HOME" worktree_has_live_session "$REPO" ) \
  && ok "recent Codex transcript marks worktree live" || bad "Codex transcript liveness missed"
touch -t 202001010000 "$CODEX_SESSION_DIR/rollout-live.jsonl"
( HOME="$FAKE_HOME" worktree_has_live_session "$REPO" ) \
  && bad "stale Codex transcript marked live" || ok "stale Codex transcript does not block"

# SessionStart leases share the worktree-removal lock. Fresh starting leases block during
# the host timeout; activation makes them authoritative until SessionEnd releases them.
HOME="$FAKE_HOME" CLAUDE_PROJECT_DIR="$REPO" hook_register_session_lease "$REPO" "session-a"
( HOME="$FAKE_HOME" worktree_has_live_session "$REPO" ) \
  && ok "fresh starting Codex lease marks worktree live" || bad "starting lease missed"
HOME="$FAKE_HOME" CLAUDE_PROJECT_DIR="$REPO" HARNESS_CODEX_SESSION_OWNER_PID="$$" \
  hook_activate_session_lease "$REPO" "session-a"
( HOME="$FAKE_HOME" worktree_has_live_session "$REPO" ) \
  && ok "active Codex session lease marks worktree live" || bad "active lease missed"
LEASE_A=$(find "$REPO/.git/codex-worktree-sessions" -name 'session-session-a.lease' -print -quit)
touch -t 202001010000 "$LEASE_A"
( HOME="$FAKE_HOME" worktree_has_live_session "$REPO" ) \
  && ok "active Codex session lease does not expire" || bad "aged active lease stopped blocking removal"
HOME="$FAKE_HOME" CLAUDE_PROJECT_DIR="$REPO" hook_release_session_lease "$REPO" "session-a"
( HOME="$FAKE_HOME" worktree_has_live_session "$REPO" ) \
  && bad "released Codex session lease stayed live" || ok "SessionEnd releases Codex lease"
DEAD_LEASE="$REPO/.git/codex-worktree-sessions/dead-owner/session-dead.lease"
mkdir -p "$(dirname "$DEAD_LEASE")"
printf 'active\n%s\n99999999\n' "$REPO" > "$DEAD_LEASE"
( HOME="$FAKE_HOME" worktree_has_live_session "$REPO" ) \
  && bad "dead owner active lease stayed live" || ok "abnormal owner exit retires active lease"
rm -f "$DEAD_LEASE"
rmdir "$(dirname "$DEAD_LEASE")"

# If an external actor already removed a linked worktree, SessionEnd can no longer run
# git -C there. Its session pointer must still locate and remove the lease in the shared
# common directory.
LINKED="$REPO-linked"
git -C "$REPO" worktree add -q -b lease-linked "$LINKED"
HOME="$FAKE_HOME" CLAUDE_PROJECT_DIR="$LINKED" hook_register_session_lease "$LINKED" "session-deleted"
git -C "$REPO" worktree remove "$LINKED"
HOME="$FAKE_HOME" CLAUDE_PROJECT_DIR="$LINKED" hook_release_session_lease "$LINKED" "session-deleted"
LEASE_RESIDUE=$(find "$REPO/.git/codex-worktree-sessions" -name 'session-session-deleted.lease' 2>/dev/null | head -n1)
[ -z "$LEASE_RESIDUE" ] && ok "SessionEnd releases lease after worktree deletion" || bad "deleted-worktree lease leaked: $LEASE_RESIDUE"

# The worktree mutex is kernel-owned: aging its persistent lock file cannot steal it
# from a live holder, and process exit releases it without pathname reclamation.
LOCKED="$REPO-lock-held"
git -C "$REPO" worktree add -q -b lock-held "$LOCKED"
READY="$REPO/lock-ready"
(
  . "$SCRIPT_DIR/lib.sh"
  HARNESS_WORKTREE_LOCK_TIMEOUT_SECONDS=1 hook_worktree_lock_acquire "$LOCKED" || exit 1
  : > "$READY"
  sleep 3
  hook_worktree_lock_release
) &
LOCK_PID=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$READY" ] && break; sleep 0.1; done
LOCK_FILE=$(find "$REPO/.git/codex-worktree-sessions" -name remove.lock -print -quit)
touch -t 202001010000 "$LOCK_FILE"
if HARNESS_WORKTREE_LOCK_TIMEOUT_SECONDS=1 hook_worktree_lock_acquire "$LOCKED"; then
  hook_worktree_lock_release
  bad "aged live worktree lock was stolen"
else
  ok "aged live worktree lock remains owned"
fi
wait "$LOCK_PID"

# A registration that queued behind removal must revalidate the worktree after acquiring.
LATE="$REPO-late-register"
git -C "$REPO" worktree add -q -b late-register "$LATE"
READY="$REPO/remove-ready"
(
  . "$SCRIPT_DIR/lib.sh"
  hook_worktree_lock_acquire "$LATE" || exit 1
  : > "$READY"
  sleep 1
  git -C "$REPO" worktree remove "$LATE"
  hook_worktree_lock_release
) &
REMOVE_PID=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$READY" ] && break; sleep 0.1; done
if HOME="$FAKE_HOME" CLAUDE_PROJECT_DIR="$LATE" hook_register_session_lease "$LATE" "late"; then
  bad "late SessionStart registered after worktree removal"
else
  ok "late SessionStart fails closed after worktree removal"
fi
wait "$REMOVE_PID"

# A precious ignored file can appear after an outer candidate check. Hold the mutex so
# removal queues, create the file, then prove the under-lock check preserves both.
LOCAL_RACE="$REPO-local-state-race"
git -C "$REPO" worktree add -q -b local-state-race "$LOCAL_RACE"
printf '.env\n' >> "$REPO/.git/info/exclude"
READY="$REPO/local-state-lock-ready"
RESULT="$REPO/local-state-remove-result"
(
  . "$SCRIPT_DIR/lib.sh"
  hook_worktree_lock_acquire "$LOCAL_RACE" || exit 1
  : > "$READY"
  sleep 2
  hook_worktree_lock_release
) &
LOCAL_LOCK_PID=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$READY" ] && break; sleep 0.1; done
(
  . "$SCRIPT_DIR/lib.sh"
  hook_safe_worktree_remove "$REPO" "$LOCAL_RACE"
  printf '%s' "$?" > "$RESULT"
) &
LOCAL_REMOVE_PID=$!
printf 'SECRET\n' > "$LOCAL_RACE/.env"
wait "$LOCAL_LOCK_PID"
wait "$LOCAL_REMOVE_PID"
eq "under-lock local-state recheck refuses removal" "$(cat "$RESULT")" "4"
[ -f "$LOCAL_RACE/.env" ] && ok "under-lock local-state recheck preserves ignored file" \
  || bad "under-lock local-state recheck deleted ignored file"

# Candidate merge proof names an exact branch and HEAD. Advancing that branch after
# classification but before the mutex is acquired must refuse removal.
IDENTITY_RACE="$REPO-identity-race"
git -C "$REPO" worktree add -q -b identity-race "$IDENTITY_RACE"
IDENTITY_EXPECTED=$(git -C "$IDENTITY_RACE" rev-parse HEAD)
git -C "$IDENTITY_RACE" commit -q --allow-empty -m "late unmerged work"
hook_safe_worktree_remove "$REPO" "$IDENTITY_RACE" identity-race "$IDENTITY_EXPECTED"
IDENTITY_RC=$?
eq "under-lock identity recheck refuses advanced HEAD" "$IDENTITY_RC" "10"
[ -d "$IDENTITY_RACE" ] && ok "advanced worktree is preserved" \
  || bad "advanced worktree was removed"

# A pathname writer that runs after the authoritative status scan must not be able to
# place ignored state inside the directory being deleted. The remover must quarantine
# the registered worktree first, so a recreated original path remains untouched.
POST_SCAN="$REPO-post-scan-race"
git -C "$REPO" worktree add -q -b post-scan-race "$POST_SCAN"
POST_SCAN_RESULT="$REPO/post-scan-remove-result"
(
  . "$SCRIPT_DIR/lib.sh"
  _hook_worktree_open_references() { return 1; }
  git() {
    if [ "${1:-}" = "-C" ] && [ "${3:-}" = "worktree" ] && [ "${4:-}" = "remove" ]; then
      mkdir -p "$POST_SCAN"
      printf 'SECRET\n' > "$POST_SCAN/.env"
    fi
    command git "$@"
  }
  hook_safe_worktree_remove "$REPO" "$POST_SCAN"
  printf '%s' "$?" > "$POST_SCAN_RESULT"
)
eq "quarantine removal succeeds despite late original-path writer" "$(cat "$POST_SCAN_RESULT")" "0"
[ -f "$POST_SCAN/.env" ] && ok "quarantine preserves post-scan original-path state" \
  || bad "quarantine deleted post-scan original-path state"

# State appearing inside the quarantine before its scan must abort removal and restore
# both the registered worktree and its local state at the original path.
QUARANTINE_RACE="$REPO-quarantine-race"
git -C "$REPO" worktree add -q -b quarantine-race "$QUARANTINE_RACE"
QUARANTINE_RESULT="$REPO/quarantine-remove-result"
(
  . "$SCRIPT_DIR/lib.sh"
  _hook_worktree_open_references() { return 1; }
  git() {
    if [ "${1:-}" = "-C" ] && [ "${3:-}" = "worktree" ] && [ "${4:-}" = "move" ]; then
      command git "$@"
      local move_rc=$?
      [ "$move_rc" -eq 0 ] && printf 'SECRET\n' > "$6/.env"
      return "$move_rc"
    fi
    command git "$@"
  }
  hook_safe_worktree_remove "$REPO" "$QUARANTINE_RACE"
  printf '%s' "$?" > "$QUARANTINE_RESULT"
)
eq "quarantine scan refuses newly appeared state" "$(cat "$QUARANTINE_RESULT")" "4"
[ -f "$QUARANTINE_RACE/.env" ] && ok "quarantine restores newly appeared state" \
  || bad "quarantine failed to restore newly appeared state"

# A pre-resolved writer can write and exit after reference observation. Reference
# observation must therefore precede the final state scan so that write is preserved.
LATE_IGNORED="$REPO-late-ignored-write"
LATE_IGNORED_RESULT="$REPO/late-ignored-write-result"
git -C "$REPO" worktree add -q -b late-ignored-write "$LATE_IGNORED"
(
  . "$SCRIPT_DIR/lib.sh"
  _hook_worktree_open_references() {
    printf 'SECRET\n' > "$1/.env"
    return 1
  }
  hook_safe_worktree_remove "$REPO" "$LATE_IGNORED"
  printf '%s' "$?" > "$LATE_IGNORED_RESULT"
)
eq "post-reference late write refuses deletion" "$(cat "$LATE_IGNORED_RESULT")" "4"
[ -f "$LATE_IGNORED/.env" ] && ok "post-reference late write is restored" \
  || bad "post-reference late write was deleted"

# Moving a registered worktree must not change its mutex/lease namespace. A SessionStart
# launched from a process already inside the moved tree must queue on the remover's lock,
# not create an unseen lease under a second pathname-derived key.
STABLE_ID="$REPO-stable-worktree-identity"
STABLE_QUARANTINE="$REPO-stable-worktree-identity-moved"
STABLE_RESULT="$REPO/stable-worktree-register-result"
git -C "$REPO" worktree add -q -b stable-worktree-identity "$STABLE_ID"
STABLE_BEFORE=$(_hook_worktree_session_dir "$STABLE_ID")
hook_worktree_lock_acquire "$STABLE_ID"
git -C "$REPO" worktree move "$STABLE_ID" "$STABLE_QUARANTINE"
STABLE_AFTER=$(_hook_worktree_session_dir "$STABLE_QUARANTINE")
eq "quarantine move preserves worktree session identity" "$STABLE_AFTER" "$STABLE_BEFORE"
HOME="$FAKE_HOME" HARNESS_WORKTREE_LOCK_TIMEOUT_SECONDS=1 /bin/bash -c '
  . "$1"
  hook_register_session_lease "$2" "moved-start"
  printf "%s" "$?" > "$3"
' _ "$SCRIPT_DIR/lib.sh" "$STABLE_QUARANTINE" "$STABLE_RESULT"
eq "moved-path SessionStart cannot acquire a distinct mutex" "$(cat "$STABLE_RESULT")" "1"
git -C "$REPO" worktree move "$STABLE_QUARANTINE" "$STABLE_ID"
hook_worktree_lock_release

# A writer can retain the original worktree as its cwd across the quarantine rename.
# Removal must detect that pre-resolved kernel reference and restore/refuse before Git
# can delete an ignored file written after the authoritative status scan.
HELD_CWD="$REPO-held-cwd-race"
HELD_READY="$REPO/held-cwd-ready"
HELD_WRITE="$REPO/held-cwd-write"
HELD_WROTE="$REPO/held-cwd-wrote"
HELD_RELEASE="$REPO/held-cwd-release"
HELD_RESULT="$REPO/held-cwd-remove-result"
git -C "$REPO" worktree add -q -b held-cwd-race "$HELD_CWD"
(
  cd "$HELD_CWD" || exit 1
  : > "$HELD_READY"
  while [ ! -f "$HELD_WRITE" ]; do sleep 0.05; done
  printf 'SECRET\n' > .env
  : > "$HELD_WROTE"
  while [ ! -f "$HELD_RELEASE" ]; do sleep 0.05; done
) &
HELD_WRITER_PID=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$HELD_READY" ] && break; sleep 0.1; done
(
  . "$SCRIPT_DIR/lib.sh"
  git() {
    if [ "${1:-}" = "-C" ] && [ "${3:-}" = "worktree" ] && [ "${4:-}" = "remove" ]; then
      : > "$HELD_WRITE"
      while [ ! -f "$HELD_WROTE" ]; do sleep 0.05; done
    fi
    command git "$@"
  }
  hook_safe_worktree_remove "$REPO" "$HELD_CWD"
  printf '%s' "$?" > "$HELD_RESULT"
)
: > "$HELD_WRITE"
: > "$HELD_RELEASE"
wait "$HELD_WRITER_PID"
eq "pre-resolved cwd refuses quarantine deletion" "$(cat "$HELD_RESULT")" "7"
[ -f "$HELD_CWD/.env" ] && ok "pre-resolved cwd state is preserved" \
  || bad "pre-resolved cwd state was deleted"

# Linux: a writable shared mapping remains a kernel reference after its fd closes.
# The procfs observer must detect it before deletion.
if [ -d /proc/self/fd ]; then
  MMAP_TARGET="$REPO/mmap-target"
  MMAP_READY="$REPO/mmap-ready"
  MMAP_RELEASE="$REPO/mmap-release"
  mkdir -p "$MMAP_TARGET"
  printf '0123456789abcdef\n' > "$MMAP_TARGET/data.bin"
  /usr/bin/python3 - "$MMAP_TARGET/data.bin" "$MMAP_READY" "$MMAP_RELEASE" <<'PY' &
import mmap
import sys
import time
from pathlib import Path

with Path(sys.argv[1]).open("r+b") as stream:
    mapped = mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_WRITE)
Path(sys.argv[2]).touch()
while not Path(sys.argv[3]).exists():
    time.sleep(0.05)
mapped[0:1] = b"X"
mapped.close()
PY
  MMAP_PID=$!
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
    [ -f "$MMAP_READY" ] && break
    sleep 0.1
  done
  _hook_worktree_open_references_production "$MMAP_TARGET" >/dev/null
  MMAP_RC=$?
  : > "$MMAP_RELEASE"
  wait "$MMAP_PID"
  eq "writable mmap is a retained worktree reference" "$MMAP_RC" "0"
fi

# HUP, INT, and TERM after the move must each restore the path and preserve the
# signal-specific shell status promised by the public remover.
for SIGNAL_CASE in HUP:129 INT:130 TERM:143; do
  CANCEL_SIGNAL=${SIGNAL_CASE%%:*}
  CANCEL_EXPECTED=${SIGNAL_CASE##*:}
  CANCEL_BRANCH=$(printf '%s' "$CANCEL_SIGNAL" | tr '[:upper:]' '[:lower:]')
  CANCELLED="$REPO-cancelled-${CANCEL_BRANCH}-quarantine"
  CANCEL_READY="$REPO/cancelled-${CANCEL_BRANCH}-ready"
  git -C "$REPO" worktree add -q -b "cancelled-${CANCEL_BRANCH}-quarantine" "$CANCELLED"
  (
    trap - EXIT
    . "$SCRIPT_DIR/lib.sh"
    git() {
      command git "$@"
      local git_rc=$?
      if [ "$git_rc" -eq 0 ] && [ "${1:-}" = "-C" ] && [ "${3:-}" = "worktree" ] \
        && [ "${4:-}" = "move" ] && [ ! -f "$CANCEL_READY" ]; then
        : > "$CANCEL_READY"
        while :; do sleep 1; done
      fi
      return "$git_rc"
    }
    hook_safe_worktree_remove "$REPO" "$CANCELLED"
  ) &
  CANCEL_PID=$!
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
    [ -f "$CANCEL_READY" ] && break
    sleep 0.1
  done
  kill "-$CANCEL_SIGNAL" "$CANCEL_PID"
  wait_bounded "$CANCEL_PID" 10
  CANCEL_RC=$?
  eq "$CANCEL_SIGNAL recovery preserves signal status" "$CANCEL_RC" "$CANCEL_EXPECTED"
  [ -d "$CANCELLED" ] && ok "$CANCEL_SIGNAL restores quarantined worktree" \
    || bad "$CANCEL_SIGNAL stranded quarantined worktree"
  CANCEL_HIDDEN=$(git -C "$REPO" worktree list --porcelain | sed -n 's/^worktree //p' \
    | grep '/\.harness-removing-' | head -n1)
  [ -z "$CANCEL_HIDDEN" ] && ok "$CANCEL_SIGNAL leaves no registered quarantine" \
    || bad "$CANCEL_SIGNAL left registered quarantine: $CANCEL_HIDDEN"
done

# A commit that lands after quarantine but before the final deletion check must also
# restore the worktree and preserve the new commit.
POST_IDENTITY="$REPO-post-quarantine-identity"
POST_IDENTITY_RESULT="$REPO/post-quarantine-identity-result"
POST_IDENTITY_COMMITTED="$REPO/post-quarantine-identity-committed"
git -C "$REPO" worktree add -q -b post-quarantine-identity "$POST_IDENTITY"
POST_IDENTITY_EXPECTED=$(git -C "$POST_IDENTITY" rev-parse HEAD)
(
  trap - EXIT
  . "$SCRIPT_DIR/lib.sh"
  _hook_worktree_open_references() { return 1; }
  git() {
    command git "$@"
    local git_rc=$?
    if [ "$git_rc" -eq 0 ] && [ "${1:-}" = "-C" ] && [ "${3:-}" = "worktree" ] \
      && [ "${4:-}" = "move" ] && [ ! -f "$POST_IDENTITY_COMMITTED" ]; then
      command git -C "$6" commit -q --allow-empty -m "late quarantined work"
      : > "$POST_IDENTITY_COMMITTED"
    fi
    return "$git_rc"
  }
  hook_safe_worktree_remove "$REPO" "$POST_IDENTITY" \
    post-quarantine-identity "$POST_IDENTITY_EXPECTED"
  printf '%s' "$?" > "$POST_IDENTITY_RESULT"
)
eq "post-quarantine identity recheck refuses advanced HEAD" \
  "$(cat "$POST_IDENTITY_RESULT")" "10"
[ -d "$POST_IDENTITY" ] && ok "post-quarantine advanced worktree is restored" \
  || bad "post-quarantine advanced worktree was stranded"
[ "$(git -C "$POST_IDENTITY" rev-list --count "$POST_IDENTITY_EXPECTED"..HEAD)" = "1" ] \
  && ok "post-quarantine new commit is preserved" \
  || bad "post-quarantine new commit was lost"

# SIGKILL cannot run a shell trap. The process-death recovery transaction must let the next GC pass
# restore the hidden registered worktree instead of deleting or permanently stranding it.
KILLED="$REPO-killed-quarantine"
KILLED_READY="$REPO/killed-quarantine-ready"
KILLED_RESULT="$REPO/killed-quarantine-recovery-result"
git -C "$REPO" worktree add -q -b killed-quarantine "$KILLED"
(
  trap - EXIT
  . "$SCRIPT_DIR/lib.sh"
  git() {
    command git "$@"
    local git_rc=$?
    if [ "$git_rc" -eq 0 ] && [ "${1:-}" = "-C" ] && [ "${3:-}" = "worktree" ] \
      && [ "${4:-}" = "move" ]; then
      : > "$KILLED_READY"
      while :; do sleep 1; done
    fi
    return "$git_rc"
  }
  hook_safe_worktree_remove "$REPO" "$KILLED"
) &
KILLED_PID=$!
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  [ -f "$KILLED_READY" ] && break
  sleep 0.1
done
kill -KILL "$KILLED_PID"
wait "$KILLED_PID" 2>/dev/null
KILLED_HIDDEN=$(git -C "$REPO" worktree list --porcelain | sed -n 's/^worktree //p' \
  | grep '/\.harness-removing-' | head -n1)
(
  . "$SCRIPT_DIR/lib.sh"
  hook_safe_worktree_remove "$REPO" "$KILLED_HIDDEN"
  printf '%s' "$?" > "$KILLED_RESULT"
)
eq "next removal pass reports interrupted-quarantine recovery" \
  "$(cat "$KILLED_RESULT")" "8"
[ -d "$KILLED" ] && ok "next removal pass restores SIGKILL quarantine" \
  || bad "SIGKILL quarantine was not restored"
KILLED_STILL_HIDDEN=$(git -C "$REPO" worktree list --porcelain | sed -n 's/^worktree //p' \
  | grep '/\.harness-removing-' | head -n1)
[ -z "$KILLED_STILL_HIDDEN" ] && ok "SIGKILL recovery leaves no registered quarantine" \
  || bad "SIGKILL recovery left registered quarantine: $KILLED_STILL_HIDDEN"

# A kill after the recovery marker is written but before Git moves the worktree leaves a
# pre-move transaction. The next pass must clear/report recovery without deleting it.
PRE_MOVE="$REPO-pre-move-transaction"
PRE_MOVE_RESULT="$REPO/pre-move-transaction-result"
git -C "$REPO" worktree add -q -b pre-move-transaction "$PRE_MOVE"
PRE_MOVE=$(_hook_canonical_worktree "$PRE_MOVE")
PRE_MOVE_QUARANTINE=$(_hook_worktree_quarantine_path "$PRE_MOVE")
PRE_MOVE_TRANSACTION=$(_hook_worktree_transaction_file "$PRE_MOVE")
mkdir -p "$(dirname "$PRE_MOVE_TRANSACTION")"
_hook_worktree_write_transaction \
  "$PRE_MOVE_TRANSACTION" "$PRE_MOVE" "$PRE_MOVE_QUARANTINE"
(
  . "$SCRIPT_DIR/lib.sh"
  hook_safe_worktree_remove "$REPO" "$PRE_MOVE"
  printf '%s' "$?" > "$PRE_MOVE_RESULT"
)
eq "pre-move transaction recovery defers deletion" "$(cat "$PRE_MOVE_RESULT")" "8"
[ -d "$PRE_MOVE" ] && ok "pre-move transaction recovery preserves worktree" \
  || bad "pre-move transaction recovery deleted worktree"

# Git can die after the directory rename but before updating its administrative path.
# That leaves the original path registered while the physical tree is at quarantine.
# Recovery must move the tree back without pruning or losing it.
PARTIAL_MOVE="$REPO-partial-move-transaction"
PARTIAL_MOVE_RESULT="$REPO/partial-move-transaction-result"
git -C "$REPO" worktree add -q -b partial-move-transaction "$PARTIAL_MOVE"
PARTIAL_MOVE=$(_hook_canonical_worktree "$PARTIAL_MOVE")
PARTIAL_MOVE_QUARANTINE=$(_hook_worktree_quarantine_path "$PARTIAL_MOVE")
PARTIAL_MOVE_TRANSACTION=$(_hook_worktree_transaction_file "$PARTIAL_MOVE")
mkdir -p "$(dirname "$PARTIAL_MOVE_TRANSACTION")"
_hook_worktree_write_transaction \
  "$PARTIAL_MOVE_TRANSACTION" "$PARTIAL_MOVE" "$PARTIAL_MOVE_QUARANTINE"
/bin/mv "$PARTIAL_MOVE" "$PARTIAL_MOVE_QUARANTINE"
(
  . "$SCRIPT_DIR/lib.sh"
  hook_safe_worktree_remove "$REPO" "$PARTIAL_MOVE"
  printf '%s' "$?" > "$PARTIAL_MOVE_RESULT"
)
eq "partial move transaction recovery defers deletion" \
  "$(cat "$PARTIAL_MOVE_RESULT")" "8"
[ -d "$PARTIAL_MOVE" ] && ok "partial move recovery restores physical worktree" \
  || bad "partial move recovery stranded physical worktree"
[ ! -e "$PARTIAL_MOVE_QUARANTINE" ] \
  && ok "partial move recovery clears quarantine path" \
  || bad "partial move recovery left quarantine path"
PARTIAL_REGISTERED=$(git -C "$REPO" worktree list --porcelain \
  | sed -n 's/^worktree //p' | grep -Fx "$PARTIAL_MOVE" || true)
[ "$PARTIAL_REGISTERED" = "$PARTIAL_MOVE" ] \
  && ok "partial move recovery preserves registration" \
  || bad "partial move recovery lost registration"

# If the remover dies after Git deletes the worktree but before unlinking the recovery
# transaction, the public entrypoint must find and clear the both-paths-absent marker.
POST_DELETE="$REPO-post-delete-transaction"
POST_DELETE_READY="$REPO/post-delete-transaction-ready"
POST_DELETE_RESULT="$REPO/post-delete-transaction-result"
git -C "$REPO" worktree add -q -b post-delete-transaction "$POST_DELETE"
POST_DELETE_TRANSACTION=$(_hook_worktree_transaction_file "$POST_DELETE")
(
  trap - EXIT
  . "$SCRIPT_DIR/lib.sh"
  _hook_worktree_open_references() { return 1; }
  rm() {
    if [ "${1:-}" = "-f" ] && [ "${2:-}" = "$POST_DELETE_TRANSACTION" ]; then
      : > "$POST_DELETE_READY"
      while :; do sleep 1; done
    fi
    command rm "$@"
  }
  hook_safe_worktree_remove "$REPO" "$POST_DELETE"
) &
POST_DELETE_PID=$!
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  [ -f "$POST_DELETE_READY" ] && break
  sleep 0.1
done
kill -KILL "$POST_DELETE_PID"
wait "$POST_DELETE_PID" 2>/dev/null
[ ! -e "$POST_DELETE" ] && ok "post-delete interruption occurs after worktree removal" \
  || bad "post-delete interruption did not remove worktree"
[ -f "$POST_DELETE_TRANSACTION" ] && ok "post-delete interruption leaves recovery marker" \
  || bad "post-delete interruption did not leave transaction marker"
(
  . "$SCRIPT_DIR/lib.sh"
  hook_safe_worktree_remove "$REPO" "$POST_DELETE"
  printf '%s' "$?" > "$POST_DELETE_RESULT"
)
eq "public remover recovers post-delete transaction" "$(cat "$POST_DELETE_RESULT")" "8"
[ ! -f "$POST_DELETE_TRANSACTION" ] && ok "post-delete recovery clears transaction" \
  || bad "post-delete recovery left transaction residue"

OPEN_UNKNOWN="$REPO-open-reference-unknown"
OPEN_UNKNOWN_RESULT="$REPO/open-reference-unknown-result"
git -C "$REPO" worktree add -q -b open-reference-unknown "$OPEN_UNKNOWN"
(
  . "$SCRIPT_DIR/lib.sh"
  _hook_worktree_open_references() { return 2; }
  hook_safe_worktree_remove "$REPO" "$OPEN_UNKNOWN"
  printf '%s' "$?" > "$OPEN_UNKNOWN_RESULT"
)
eq "unavailable open-reference observation refuses deletion" \
  "$(cat "$OPEN_UNKNOWN_RESULT")" "9"
[ -d "$OPEN_UNKNOWN" ] && ok "unavailable open-reference observation restores worktree" \
  || bad "unavailable open-reference observation deleted worktree"

STATUS_FAIL="$REPO-status-failure"
git -C "$REPO" worktree add -q -b status-failure "$STATUS_FAIL"
STATUS_RESULT="$REPO/status-failure-result"
(
  . "$SCRIPT_DIR/lib.sh"
  hook_worktree_local_state() { return 2; }
  hook_safe_worktree_remove "$REPO" "$STATUS_FAIL"
  printf '%s' "$?" > "$STATUS_RESULT"
)
eq "under-lock status failure refuses removal" "$(cat "$STATUS_RESULT")" "5"
[ -d "$STATUS_FAIL" ] && ok "under-lock status failure preserves worktree" \
  || bad "under-lock status failure removed worktree"

# The executable public wrapper must preserve the three nonfailure refusal/recovery
# diagnostics instead of collapsing them into a generic error.
WRAPPER_FIXTURE="$REPO/wrapper-fixture"
mkdir -p "$WRAPPER_FIXTURE"
cp "$SCRIPT_DIR/safe-worktree-remove.sh" "$WRAPPER_FIXTURE/safe-worktree-remove.sh"
cat > "$WRAPPER_FIXTURE/lib.sh" <<'EOF'
hook_project_dir() { printf '/tmp'; }
hook_safe_worktree_remove() { return "${FAKE_REMOVE_RC:?}"; }
EOF
for WRAPPER_CASE in \
  '7:retained process references' \
  '8:restored an interrupted quarantine' \
  '9:process-reference state unavailable' \
  '10:branch or HEAD changed after classification'; do
  WRAPPER_RC=${WRAPPER_CASE%%:*}
  WRAPPER_MESSAGE=${WRAPPER_CASE#*:}
  WRAPPER_STDERR="$REPO/wrapper-${WRAPPER_RC}.stderr"
  FAKE_REMOVE_RC="$WRAPPER_RC" /bin/bash "$WRAPPER_FIXTURE/safe-worktree-remove.sh" \
    /tmp/candidate 2> "$WRAPPER_STDERR"
  WRAPPER_ACTUAL=$?
  eq "public wrapper preserves rc $WRAPPER_RC" "$WRAPPER_ACTUAL" "$WRAPPER_RC"
  grep -qF "$WRAPPER_MESSAGE" "$WRAPPER_STDERR" \
    && ok "public wrapper maps rc $WRAPPER_RC diagnostic" \
    || bad "public wrapper lost rc $WRAPPER_RC diagnostic"
done

# hook_write_checkpoint (U-HK-27 writer): writes an atomic session-specific latest pointer
# with the label; skip_gh omits the open-PRs gh lookup (fast path — no network in this test).
CLAUDE_PROJECT_DIR="$REPO" hook_write_checkpoint "Test snapshot" skip_gh session-a
LATEST="$REPO/.harness/.checkpoints/precompact-latest-session-a.md"
[ -f "$LATEST" ] && ok "hook_write_checkpoint wrote session-specific latest" || bad "no checkpoint file"
grep -q "Test snapshot" "$LATEST" 2>/dev/null && ok "checkpoint carries the label" || bad "label missing"
grep -q "skipped — fast path" "$LATEST" 2>/dev/null && ok "skip_gh omits gh PR lookup" || bad "skip_gh not honored"

# Generation numbers come from one persistent counter, not a wall clock that can move
# backward. The counter is the ordering authority across concurrent checkpoint writers.
GENERATION_DIR="$REPO/checkpoint-generation"
mkdir -p "$GENERATION_DIR"
eq "checkpoint generation starts at one" \
  "$(hook_checkpoint_generation "$GENERATION_DIR")" "1"
eq "checkpoint generation increments durably" \
  "$(hook_checkpoint_generation "$GENERATION_DIR")" "2"
printf '40\n' > "$GENERATION_DIR/.checkpoint-generation"
eq "checkpoint generation resumes above persisted state" \
  "$(hook_checkpoint_generation "$GENERATION_DIR")" "41"

# The Python flock helper exits before the critical section, but Bash retains the
# inherited open-file description. A deliberately slow older publish must therefore
# finish before a newer generation can enter and become the final pointer.
CHECKPOINT_RACE="$REPO/checkpoint-race"
SLOW_BIN="$CHECKPOINT_RACE/bin"
mkdir -p "$SLOW_BIN"
cat > "$SLOW_BIN/cp" <<'EOF'
#!/usr/bin/env bash
: > "$CHECKPOINT_READY"
sleep 2
exec /bin/cp "$@"
EOF
chmod +x "$SLOW_BIN/cp"
OLD_SOURCE="$CHECKPOINT_RACE/old.md"
NEW_SOURCE="$CHECKPOINT_RACE/new.md"
RACE_LATEST="$CHECKPOINT_RACE/latest.md"
CHECKPOINT_READY="$CHECKPOINT_RACE/copy-ready"
printf '<!-- checkpoint-generation: 1 -->\nold\n' > "$OLD_SOURCE"
printf '<!-- checkpoint-generation: 2 -->\nnew\n' > "$NEW_SOURCE"
(
  export CHECKPOINT_READY
  PATH="$SLOW_BIN:$PATH" hook_publish_checkpoint "$RACE_LATEST" "$OLD_SOURCE" 1
) &
OLD_PUBLISH_PID=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$CHECKPOINT_READY" ] && break; sleep 0.1; done
hook_publish_checkpoint "$RACE_LATEST" "$NEW_SOURCE" 2
wait "$OLD_PUBLISH_PID"
if grep -q '^new$' "$RACE_LATEST" 2>/dev/null; then
  ok "checkpoint lock survives helper exit and orders publishers"
else
  bad "checkpoint lock released with helper process"
fi

# A hot-path publisher must not wait indefinitely behind a suspended writer.
(
  exec 9>> "${RACE_LATEST}.lock"
  /usr/bin/python3 - 9 <<'PY'
import fcntl
import sys
import time

fcntl.flock(int(sys.argv[1]), fcntl.LOCK_EX)
time.sleep(3)
PY
) &
LOCK_HOLDER_PID=$!
sleep 0.1
SECONDS=0
hook_publish_checkpoint "$RACE_LATEST" "$NEW_SOURCE" 3 0.2
BOUNDED_PUBLISH_RC=$?
BOUNDED_PUBLISH_ELAPSED=$SECONDS
wait "$LOCK_HOLDER_PID"
{ [ "$BOUNDED_PUBLISH_RC" -ne 0 ] && [ "$BOUNDED_PUBLISH_ELAPSED" -lt 2 ]; } \
  && ok "checkpoint publisher lock wait is bounded" \
  || bad "checkpoint publisher blocked: elapsed=${BOUNDED_PUBLISH_ELAPSED}s rc=${BOUNDED_PUBLISH_RC}"

# C-HE-04 §6 (U-HE-15): committed-but-unpushed commits are capture that would be
# lost with the worktree's branch. With an upstream set, ahead-of-@{u} is refusal
# residue; pushed = clean; NO upstream keeps today's behavior (spec scopes the
# check to `rev-list @{u}..HEAD` -- refusing no-upstream would refuse every
# local-only scratch worktree; see the five rc-0/7/9/10 witnesses above).
AHEAD_ORIGIN="$REPO-ahead-origin.git"
git init -q --bare "$AHEAD_ORIGIN"
git -C "$REPO" remote add origin "$AHEAD_ORIGIN"
AHEAD_WT="$REPO-ahead-of-upstream"
git -C "$REPO" worktree add -q -b ahead-branch "$AHEAD_WT"
git -C "$AHEAD_WT" push -qu origin ahead-branch 2>/dev/null
git -C "$AHEAD_WT" commit -q --allow-empty -m "committed but unpushed"
AHEAD_OUT=$(hook_worktree_local_state "$AHEAD_WT")
AHEAD_RC=$?
eq "ahead-of-upstream worktree is refusal residue" "$AHEAD_RC" "0"
case "$AHEAD_OUT" in
  *"ahead-of-upstream: 1 commit(s)"*) ok "residue names the unpushed commit count" ;;
  *) bad "residue missing ahead-of-upstream line: '$AHEAD_OUT'" ;;
esac
hook_safe_worktree_remove "$REPO" "$AHEAD_WT" >/dev/null
eq "safe removal refuses a committed-but-unpushed worktree" "$?" "4"
[ -d "$AHEAD_WT" ] && ok "ahead-of-upstream worktree preserved" \
  || bad "ahead-of-upstream worktree was removed"
git -C "$AHEAD_WT" push -q origin ahead-branch 2>/dev/null
hook_worktree_local_state "$AHEAD_WT" >/dev/null
eq "pushed-to-upstream worktree is clean" "$?" "1"
NO_UPSTREAM_WT="$REPO-no-upstream"
git -C "$REPO" worktree add -q -b no-upstream-branch "$NO_UPSTREAM_WT"
hook_worktree_local_state "$NO_UPSTREAM_WT" >/dev/null
eq "no-upstream worktree keeps today's clean verdict" "$?" "1"
# Merge-gate L1 (PR #1403): a pruned remote-tracking ref must not fail OPEN --
# the branch CONFIG persists after `fetch --prune`, so an upstream-configured
# branch whose @{u} no longer resolves is fail-closed residue.
PRUNED_WT="$REPO-pruned-upstream"
git -C "$REPO" worktree add -q -b pruned-branch "$PRUNED_WT"
git -C "$PRUNED_WT" push -qu origin pruned-branch 2>/dev/null
git -C "$PRUNED_WT" commit -q --allow-empty -m "committed after last push"
git -C "$REPO" update-ref -d refs/remotes/origin/pruned-branch
PRUNED_OUT=$(hook_worktree_local_state "$PRUNED_WT")
PRUNED_RC=$?
eq "pruned-upstream worktree is fail-closed residue" "$PRUNED_RC" "0"
case "$PRUNED_OUT" in
  *"upstream configured but unresolvable"*) ok "residue names the unresolvable upstream" ;;
  *) bad "residue missing unresolvable-upstream line: '$PRUNED_OUT'" ;;
esac
DETACHED_WT="$REPO-detached"
git -C "$REPO" worktree add -q --detach "$DETACHED_WT"
DETACHED_OUT=$(hook_worktree_local_state "$DETACHED_WT")
DETACHED_RC=$?
eq "detached-HEAD worktree is refusal residue" "$DETACHED_RC" "0"
case "$DETACHED_OUT" in
  *"detached HEAD"*) ok "residue names the detached HEAD" ;;
  *) bad "residue missing detached-HEAD line: '$DETACHED_OUT'" ;;
esac


# ── hook_git_retry — C-HE-11 §3 bounded local-git lock retry (U-HE-32) ────────
# The ledger writer lives one layer ABOVE lib.sh (loop_lib.sh depends on lib.sh,
# never the reverse), so these assertions source it the way every real caller
# does — lib.sh first, then loop_lib.sh — instead of stubbing the writer.
. "$SCRIPT_DIR/loop_lib.sh"
export HARNESS_LOOP_STATUS_PATH="$REPO/shared/loop_status.md"
GR="$REPO/gitretry"
git init -q -b main "$GR"
git -C "$GR" config user.email t@t.t; git -C "$GR" config user.name t
( cd "$GR" && echo x > f && git add -A && git commit -qm base )
TRACE="$REPO/git-retry-trace"

# The lock is cleared on ATTEMPT COUNT, never on a wall-clock sleep. Full jitter
# means seven draws can in principle sum to almost nothing, so a `sleep 0.4`
# unlocker would let the budget exhaust before it fired — a flake whose rate
# depends on load. Watching the trace ties the clear to the thing under test.
gr_unlock_after_attempts() {
  local lock="$1" n="$2" _gr_i=0
  # BOUNDED. A regression that stops retrying never grows the trace, and an
  # unbounded poller would then spin forever -- CI would HANG rather than go red.
  # At the bound the lock is cleared regardless, so the op completes and the
  # attempt-count assertion below is what reports the failure.
  ( while [ "$(wc -l < "$TRACE" 2>/dev/null | tr -d ' ')" -lt "$n" ] && [ "$_gr_i" -lt 500 ]; do
      sleep 0.01; _gr_i=$((_gr_i + 1))
    done
    rm -f "$lock" ) &
}
gr_attempts() { wc -l < "$TRACE" | tr -d ' '; }
# Trace rows are `<attempt> <ceiling_ms> <slept_s>`; these read the two number columns.
gr_ceilings() { awk '{ printf "%s ", $2 }' "$TRACE"; }

# NOTE on what witnesses WHICH classifier branch. Cases (1), (2) and (9) below drive REAL
# git, and real git's index/ref-lock stderr always ALSO carries "Another git process seems
# to be running" -- a separate alternative in the matcher. So those three cannot, on their
# own, tell the `Unable to create ….lock': File exists` branch from the advice sentence, and
# a merge-gate lens correctly noticed that. The branch is nonetheless witnessed: the PATH
# shims used by the call-site cases emit ONLY the `Unable to create` line, so deleting that
# alternative reds 7 assertions (measured). Keep it that way -- if those shims ever grow the
# advice sentence, the branch silently loses its only independent witness.
#
# (1) A lock that clears mid-flight: the op succeeds, and it demonstrably retried.
: > "$TRACE"
: > "$GR/.git/index.lock"
gr_unlock_after_attempts "$GR/.git/index.lock" 2
GR_UNLOCKER=$!
HOOK_GIT_RETRY_TRACE="$TRACE" hook_git_retry -C "$GR" add -A
eq "transient index.lock clears -> op succeeds" "$?" "0"
wait "$GR_UNLOCKER" 2>/dev/null
[ "$(gr_attempts)" -ge 2 ] && ok "transient index.lock retried ($(gr_attempts) attempts)" \
  || bad "expected >=2 attempts, got '$(gr_attempts)'"

# (2) A lock that never clears: exactly 8 attempts, the op fails with git's own
#     exit code, git's error still reaches stderr, and a NOTIFY row lands under a
#     cause that never routes to the merge-door budget.
: > "$TRACE"
: > "$GR/.git/index.lock"
HOOK_GIT_RETRY_TRACE="$TRACE" hook_git_retry -C "$GR" add -A \
  >"$REPO/gr-held.out" 2>"$REPO/gr-held.err"
eq "held index.lock -> op fails with git's exit code" "$?" "128"
eq "held index.lock exhausts exactly 8 attempts" "$(gr_attempts)" "8"
grep -q "index.lock" "$REPO/gr-held.err" \
  && ok "exhaustion still reports git's error on stderr" \
  || bad "exhaustion swallowed git's error: '$(cat "$REPO/gr-held.err")'"
grep -q 'cause=git-ref-lock:transient-retry:lock_contention' "$HARNESS_LOOP_STATUS_PATH" \
  && ok "exhaustion emits the git-ref-lock NOTIFY" \
  || bad "no git-ref-lock NOTIFY row: '$(cat "$HARNESS_LOOP_STATUS_PATH" 2>/dev/null)'"
grep -q '| NOTIFY |' "$HARNESS_LOOP_STATUS_PATH" \
  && ok "the exhaustion row is a NOTIFY" || bad "exhaustion row is not a NOTIFY"
grep -q 'cause=merge-door' "$HARNESS_LOOP_STATUS_PATH" \
  && bad "git lock exhaustion must NOT route to the merge-door budget" \
  || ok "exhaustion stays off the merge-door budget"
rm -f "$GR/.git/index.lock"

# (3) A failure that is not lock contention is returned immediately — retrying a
#     genuine error would burn the budget and delay the real diagnosis.
: > "$TRACE"
hook_git_retry -C "$GR" rev-parse --verify refs/heads/no-such-branch \
  >/dev/null 2>"$REPO/gr-nonlock.err"
GR_RC=$?
[ "$GR_RC" -ne 0 ] && ok "non-lock failure propagates git's exit code ($GR_RC)" \
  || bad "non-lock failure returned 0"
eq "non-lock failure is not retried" "$(gr_attempts)" "0"

# (4) The caller's stdout is git's stdout, byte for byte. `git checkout -b`
#     announces itself on STDERR, so a helper that merged the two streams would
#     hand the caller a stdout it never wrote — silently corrupting anyone who
#     parses it.
hook_git_retry -C "$GR" checkout -b passthrough \
  >"$REPO/gr-pass.out" 2>"$REPO/gr-pass.err"
eq "success keeps stderr out of stdout" "$(cat "$REPO/gr-pass.out")" ""
grep -q "passthrough" "$REPO/gr-pass.err" \
  && ok "git's stderr reaches the caller's stderr" \
  || bad "git's stderr was swallowed: '$(cat "$REPO/gr-pass.err")'"
eq "stdout is byte-exact" "$(hook_git_retry -C "$GR" rev-parse HEAD)" "$(git -C "$GR" rev-parse HEAD)"

# (5) The config-lock shape. git says `could not lock config file …: File exists`
#     with no `.lock` anywhere in the text, so a pattern written only against the
#     index/ref wording would miss it — and this is the exact write C-HE-11 §2
#     makes (`gc.auto 0`), whose unretried failure is B-201.
: > "$TRACE"
: > "$GR/.git/config.lock"
gr_unlock_after_attempts "$GR/.git/config.lock" 2
GR_UNLOCKER=$!
HOOK_GIT_RETRY_TRACE="$TRACE" hook_git_retry -C "$GR" config gc.auto 0
eq "transient config.lock clears -> op succeeds" "$?" "0"
wait "$GR_UNLOCKER" 2>/dev/null
[ "$(gr_attempts)" -ge 2 ] && ok "config-lock contention is retried ($(gr_attempts) attempts)" \
  || bad "config-lock contention not retried: '$(gr_attempts)' attempts"
eq "the retried config write actually landed" "$(git -C "$GR" config --get gc.auto)" "0"

# (6) git runs as a foreground child of the CALLING shell. A `$(…)` capture would run
#     it in a subshell, and a subshell resets this shell's traps to default — silently
#     disarming the HUP/INT/TERM interrupt recovery that hook_safe_worktree_remove arms
#     around the very `worktree move` this now wraps. The shim reports who forked it.
GR_SHIM="$REPO/shim"
mkdir -p "$GR_SHIM"
cat > "$GR_SHIM/git" <<'GRSHIM'
#!/usr/bin/env bash
echo "$PPID" > "$GIT_SHIM_PPID_FILE"
echo "${LC_ALL:-unset}" > "$GIT_SHIM_PPID_FILE.locale"
GRSHIM
chmod +x "$GR_SHIM/git"
GIT_SHIM_PPID_FILE="$REPO/shim-ppid" PATH="$GR_SHIM:$PATH" hook_git_retry status
eq "git is forked by the calling shell, so its traps stay armed" \
  "$(cat "$REPO/shim-ppid")" "$$"
# The classifier reads git's ENGLISH diagnostics, so the helper pins LC_ALL=C on the
# invocation. Nothing else proves that: every real-git and shim message in this suite is
# already English, so deleting the pin would leave the whole suite green while a host
# with a localised LC_MESSAGES silently stopped matching (out-of-family review r5).
eq "the child git is invoked under LC_ALL=C" "$(cat "$REPO/shim-ppid.locale")" "C"

# (7) `cannot lock ref '…': is at <a> but expected <b>` is a stale-expectation conflict,
#     not contention — no amount of waiting resolves it. Retrying would burn the whole
#     budget and then file a NOTIFY naming a `lock_contention` that never happened, which
#     C-HE-13 §3 reads as pilot friction. The discriminator is `File exists`.
: > "$TRACE"
HOOK_GIT_RETRY_TRACE="$TRACE" hook_git_retry -C "$GR" update-ref refs/heads/main \
  "$(git -C "$GR" rev-parse HEAD)" 0000000000000000000000000000000000000001 \
  >/dev/null 2>"$REPO/gr-stale.err"
GR_STALE_RC=$?
[ "$GR_STALE_RC" -ne 0 ] && ok "stale-expectation ref conflict still fails ($GR_STALE_RC)" \
  || bad "stale-expectation ref conflict returned 0"
grep -q "but expected" "$REPO/gr-stale.err" \
  && ok "the stale-expectation error reaches the caller's stderr" \
  || bad "stale-expectation error swallowed: '$(cat "$REPO/gr-stale.err")'"
eq "a stale-expectation ref conflict is not retried" "$(gr_attempts)" "0"

# (8) The backoff NUMBERS, not merely the attempt count. C-HE-11 §3 fixes base 100 ms,
#     factor 2 and a 5 s cap, and "full jitter" means each wait is drawn from [0, ceiling]
#     rather than being the ceiling itself. A count-only witness is blind to all of it —
#     a zero-delay tight loop would pass every assertion above (out-of-family review r1).
#     Asserted as SHAPE, never as elapsed wall clock: the ceiling sequence is exact, and
#     the drawn sleeps are checked against their own ceiling, so load cannot flake it.
: > "$TRACE"
: > "$GR/.git/index.lock"
GR_T0=$SECONDS
HOOK_GIT_RETRY_TRACE="$TRACE" hook_git_retry -C "$GR" add -A >/dev/null 2>&1
GR_ELAPSED=$((SECONDS - GR_T0))
eq "the ceiling doubles from 100 ms and caps at 5 s" \
  "$(gr_ceilings)" "100 200 400 800 1600 3200 5000 - "
# BOTH ends of the range must be exercised. "<= ceiling" alone is satisfied by an
# always-zero sleep, and "< ceiling" alone is too -- a mutation probe caught exactly that,
# so the assertion also requires a strictly positive draw. Together they reject the two
# degenerate implementations: a zero-delay tight loop and a fixed-ceiling backoff.
GR_JITTER=$(awk '$2 != "-" {
    c = $2 / 1000
    if ($3 + 0 > c) over++
    if ($3 + 0 < c) below++
    if ($3 + 0 > 0) positive++
  } END { printf "%d %d %d", over + 0, below + 0, positive + 0 }' "$TRACE")
eq "every wait is drawn from [0, ceiling], with both ends of the range exercised" \
  "$(echo "$GR_JITTER" | awk '{ print ($1 == 0 && $2 > 0 && $3 > 0) ? "ok" \
      : "no (over=" $1 " below=" $2 " positive=" $3 ")" }')" "ok"
# And that the waits were actually TAKEN. The assertions above read values the helper
# wrote BEFORE sleeping, so deleting `sleep "$slept"` left them all green (r3) -- the
# lock here is released on attempt count, so nothing else notices the missing delay. A
# LOWER bound on elapsed time is the load-immune shape: load can only make it slower.
GR_SLEPT_S=$(awk '$3 != "-" { t += $3 } END { printf "%d", t }' "$TRACE")
[ "${GR_ELAPSED:-0}" -ge "$GR_SLEPT_S" ] \
  && ok "the waits were actually taken (${GR_ELAPSED}s elapsed >= ${GR_SLEPT_S}s slept)" \
  || bad "elapsed ${GR_ELAPSED}s is below the ${GR_SLEPT_S}s the trace claims to have slept"
rm -f "$GR/.git/index.lock"

# (9) A HELD ref lock — `refs/heads/<name>.lock`. The contract names ref AND index
#     collisions, and the only ref case above is the stale-expectation NEGATIVE one, so
#     narrowing the matcher back to index-only would have kept this suite green while
#     breaking half the contract (out-of-family review r1).
: > "$TRACE"
: > "$GR/.git/refs/heads/contended.lock"
gr_unlock_after_attempts "$GR/.git/refs/heads/contended.lock" 2
GR_UNLOCKER=$!
HOOK_GIT_RETRY_TRACE="$TRACE" hook_git_retry -C "$GR" branch contended
eq "transient refs/heads/*.lock clears -> op succeeds" "$?" "0"
wait "$GR_UNLOCKER" 2>/dev/null
[ "$(gr_attempts)" -ge 2 ] && ok "held ref-lock contention is retried ($(gr_attempts) attempts)" \
  || bad "ref-lock contention not retried: '$(gr_attempts)' attempts"
git -C "$GR" rev-parse --verify -q refs/heads/contended >/dev/null \
  && ok "the retried branch creation actually landed" || bad "branch contended missing"

# (10) A caller running under `set -e` must survive the collision this helper exists to
#      absorb. As a bare `git …; rc=$?` the failing command is NOT exempt from errexit,
#      so the shell dies at the first attempt — before the retry, the cleanup or the
#      NOTIFY (out-of-family review r1). Witnessed by attempt count, not by survival of
#      the outer shell: an exhausted budget legitimately returns non-zero, which errexit
#      then acts on, so only the trace can tell "died at attempt 1" from "ran all 8".
: > "$TRACE"
: > "$GR/.git/index.lock"
bash -euo pipefail -c '
  . "$1/lib.sh"
  HOOK_GIT_RETRY_TRACE="$3" hook_git_retry -C "$2" add -A
' _ "$SCRIPT_DIR" "$GR" "$TRACE" >/dev/null 2>&1
eq "a set -e caller is not killed mid-retry" "$(gr_attempts)" "8"
rm -f "$GR/.git/index.lock"

# (11) The SUCCESS path under `set -e`. r2 read the trailing `[ -n "$err" ] && printf …`
#      as an errexit trigger that would kill a caller on every quiet success. It is not:
#      bash exempts the non-final command of an `&&` list, and `return "$rc"` follows it
#      anyway. Measured, not argued — and pinned here so the next reader does not have to
#      re-derive it. (The r1 witness above covers only the EXHAUSTED path.)
GR_OK=$(bash -euo pipefail -c '
  . "$1/lib.sh"
  hook_git_retry -C "$2" rev-parse --short HEAD >/dev/null
  echo SURVIVED
' _ "$SCRIPT_DIR" "$GR" 2>/dev/null)
eq "a set -e caller survives a QUIET SUCCESS through the helper" "$GR_OK" "SURVIVED"

# (12) The production call sites, not just the helper. r2 (P3) was right that reverting
#      lib.sh's worktree mutations to raw `git` would leave every assertion above green.
#      A PATH shim fails the first `worktree move` with a lock message and then delegates
#      to the real git, so a wired call site retries and completes while an unwired one
#      dies on the shim's first refusal.
GR_WIRED="$REPO/wired"
git -C "$REPO" worktree add -q -b wired-branch "$GR_WIRED"
GR_SHIM2="$REPO/shim2"
mkdir -p "$GR_SHIM2"
cat > "$GR_SHIM2/git" <<'GRSHIM2'
#!/usr/bin/env bash
# Fail the FIRST call of EACH wrapped subcommand, once, via a per-subcommand marker.
# A single shared budget is NOT equivalent and was the bug in the first version of this
# shim: `worktree move` retried twice, consumed the whole budget, and `worktree remove`
# was never contended -- so reverting the remove call site to raw git left the suite
# green. Caught by mutation probe, which is the only reason it is written this way.
case "${3:-} ${4:-}" in
  "worktree move"|"worktree remove")
    marker="$GIT_SHIM_COUNT.$(echo "${3:-} ${4:-}" | tr ' ' '-')"
    if [ ! -e "$marker" ]; then
      : > "$marker"
      echo "fatal: Unable to create '/tmp/wt/.git/index.lock': File exists." >&2
      exit 128
    fi
    ;;
esac
exec "$REAL_GIT" "$@"
GRSHIM2
chmod +x "$GR_SHIM2/git"
: > "$TRACE"
rm -f "$REPO"/shim-wired.* 2>/dev/null
REAL_GIT="$(command -v git)" GIT_SHIM_COUNT="$REPO/shim-wired" \
  HOOK_GIT_RETRY_TRACE="$TRACE" PATH="$GR_SHIM2:$PATH" \
  hook_safe_worktree_remove "$REPO" "$GR_WIRED"
eq "a contended worktree move still completes the removal" "$?" "0"
[ "$(gr_attempts)" -ge 2 ] \
  && ok "both worktree call sites are wired to the retry ($(gr_attempts) attempts)" \
  || bad "worktree move/remove did NOT both go through hook_git_retry: '$(gr_attempts)'"

# (13) The RESTORE call site. r3 found it still on raw git after the forward move and
#      the removal were wrapped; three of its four callers are ordinary recovery, not
#      the signal trap the exclusion assumed, so a lock collision there strands the
#      worktree in quarantine. Same shim, driven straight at the restore.
GR_RESTORE="$REPO/restoreme"
git -C "$REPO" worktree add -q -b restore-branch "$GR_RESTORE"
git -C "$REPO" worktree move "$GR_RESTORE" "$REPO/.harness-removing-restoreme"
# The transaction must carry git's OWN spelling of the paths -- registered_path
# string-compares against `worktree list --porcelain`, and on macOS mktemp hands back
# /var/... where git reports /private/var/... . The production path reads them from
# git for the same reason.
GR_QUAR=$(git -C "$REPO" worktree list --porcelain | sed -n 's|^worktree ||p' \
  | grep '/[.]harness-removing-restoreme$' | head -n1)
GR_ORIG="$(dirname "$GR_QUAR")/restoreme"
GR_TXN="$REPO/restore-txn"
_hook_worktree_write_transaction "$GR_TXN" "$GR_ORIG" "$GR_QUAR"
: > "$TRACE"
rm -f "$REPO"/shim-restore.* 2>/dev/null
REAL_GIT="$(command -v git)" GIT_SHIM_COUNT="$REPO/shim-restore" \
  HOOK_GIT_RETRY_TRACE="$TRACE" PATH="$GR_SHIM2:$PATH" \
  _hook_worktree_restore_transaction "$REPO" "$GR_TXN" >/dev/null
eq "a contended restore still puts the worktree back" "$?" "0"
[ "$(gr_attempts)" -ge 1 ] \
  && ok "the restore call site is wired to the retry ($(gr_attempts) attempts)" \
  || bad "restore move did NOT go through hook_git_retry: '$(gr_attempts)' attempts"
[ -d "$GR_ORIG" ] && ok "the worktree is back at its original path" \
  || bad "worktree left in quarantine at $GR_QUAR"

# (14) The SIGNAL-HANDLER restore is fail-fast, where every other restore caller is not.
#      `hook_bounded` escalates SIGTERM to SIGKILL after 2 s, so a handler that sits in
#      the ~11 s budget is killed mid-restore and strands the worktree -- the exact damage
#      the retry exists to prevent (merge-gate concurrency lens). The two assertions are a
#      PAIR: fail-fast here is only correct because the ordinary path above still waits.
GR_TRAP="$REPO/trapme"
git -C "$REPO" worktree add -q -b trap-branch "$GR_TRAP"
git -C "$REPO" worktree move "$GR_TRAP" "$REPO/.harness-removing-trapme"
GR_TQUAR=$(git -C "$REPO" worktree list --porcelain | sed -n 's|^worktree ||p' \
  | grep '/[.]harness-removing-trapme$' | head -n1)
GR_TORIG="$(dirname "$GR_TQUAR")/trapme"
GR_TTXN="$REPO/trap-txn"
_hook_worktree_write_transaction "$GR_TTXN" "$GR_TORIG" "$GR_TQUAR"
# The shim used here fails EVERY time, not just once. A fail-once shim cannot tell the
# two budgets apart -- both record exactly one trace row (a single retry under max=8, a
# single exhaust row under max=1) -- so the assertion would hold no matter which the
# handler used. Only a lock that never clears separates 1 attempt from 8.
GR_SHIM3="$REPO/shim3"
mkdir -p "$GR_SHIM3"
cat > "$GR_SHIM3/git" <<'GRSHIM3'
#!/usr/bin/env bash
if [ "${3:-} ${4:-}" = "worktree move" ]; then
  echo "fatal: Unable to create '/tmp/wt/.git/index.lock': File exists." >&2
  exit 128
fi
exec "$REAL_GIT" "$@"
GRSHIM3
chmod +x "$GR_SHIM3/git"
: > "$TRACE"
(
  _HOOK_REMOVE_ROOT="$REPO" _HOOK_REMOVE_TRANSACTION="$GR_TTXN" \
  REAL_GIT="$(command -v git)" \
    HOOK_GIT_RETRY_TRACE="$TRACE" PATH="$GR_SHIM3:$PATH" \
    _hook_worktree_interrupted 143
) >/dev/null 2>&1
eq "the signal-handler restore takes ONE attempt, not the 8-attempt budget" \
  "$(gr_attempts)" "1"
# ...and the ordinary restore path, against the SAME never-clearing lock, still spends
# the full budget. Asserted as a pair: fail-fast in the handler is only correct because
# the non-handler callers still wait.
: > "$TRACE"
REAL_GIT="$(command -v git)" HOOK_GIT_RETRY_TRACE="$TRACE" PATH="$GR_SHIM3:$PATH" \
  _hook_worktree_restore_transaction "$REPO" "$GR_TTXN" >/dev/null 2>&1
eq "an ordinary restore against the same lock still spends the full budget" \
  "$(gr_attempts)" "8"

# (15) The WRAPPER's own ledger dependency. `safe-worktree-remove.sh` sources loop_lib.sh
#      so an exhausted budget leaves a durable NOTIFY rather than only a line on stderr.
#      Every other exhaustion case in this file sources loop_lib itself, and every wiring
#      case calls the library function directly, so reverting that one line left the suite
#      green (out-of-family review r5). This drives the SCRIPT, as a subprocess.
GR_WRAP="$REPO/wrapme"
git -C "$REPO" worktree add -q -b wrap-branch "$GR_WRAP"
GR_WRAP_LEDGER="$REPO/wrapper-ledger.md"
rm -f "$GR_WRAP_LEDGER"
REAL_GIT="$(command -v git)" GIT_SHIM_COUNT="$REPO/shim-wrap" \
  HARNESS_LOOP_STATUS_PATH="$GR_WRAP_LEDGER" PATH="$GR_SHIM3:$PATH" \
  bash "$SCRIPT_DIR/safe-worktree-remove.sh" "$GR_WRAP" >/dev/null 2>&1
grep -q 'cause=git-ref-lock:transient-retry:lock_contention' "$GR_WRAP_LEDGER" 2>/dev/null \
  && ok "the wrapper writes a durable NOTIFY when the budget is exhausted" \
  || bad "no NOTIFY row from the wrapper: [$(cat "$GR_WRAP_LEDGER" 2>/dev/null)]"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

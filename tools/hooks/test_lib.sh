#!/usr/bin/env bash
# Unit tests for tools/hooks/lib.sh. Hermetic (no network; temp git repo for the
# branch/loop-marker cases). Exits non-zero on any failed assertion (CI-friendly).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/lib.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
eq()  { [ "$2" = "$3" ] && ok "$1 ($2)" || bad "$1: got '$2' want '$3'"; }

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
HOME="$FAKE_HOME" CLAUDE_PROJECT_DIR="$REPO" hook_activate_session_lease "$REPO" "session-a"
( HOME="$FAKE_HOME" worktree_has_live_session "$REPO" ) \
  && ok "active Codex session lease marks worktree live" || bad "active lease missed"
LEASE_A=$(find "$REPO/.git/codex-worktree-sessions" -name 'session-session-a.lease' -print -quit)
touch -t 202001010000 "$LEASE_A"
( HOME="$FAKE_HOME" worktree_has_live_session "$REPO" ) \
  && ok "active Codex session lease does not expire" || bad "aged active lease stopped blocking removal"
HOME="$FAKE_HOME" CLAUDE_PROJECT_DIR="$REPO" hook_release_session_lease "$REPO" "session-a"
( HOME="$FAKE_HOME" worktree_has_live_session "$REPO" ) \
  && bad "released Codex session lease stayed live" || ok "SessionEnd releases Codex lease"

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

# hook_write_checkpoint (U-HK-27 writer): writes an atomic session-specific latest pointer
# with the label; skip_gh omits the open-PRs gh lookup (fast path — no network in this test).
CLAUDE_PROJECT_DIR="$REPO" hook_write_checkpoint "Test snapshot" skip_gh session-a
LATEST="$REPO/.harness/.checkpoints/precompact-latest-session-a.md"
[ -f "$LATEST" ] && ok "hook_write_checkpoint wrote session-specific latest" || bad "no checkpoint file"
grep -q "Test snapshot" "$LATEST" 2>/dev/null && ok "checkpoint carries the label" || bad "label missing"
grep -q "skipped — fast path" "$LATEST" 2>/dev/null && ok "skip_gh omits gh PR lookup" || bad "skip_gh not honored"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

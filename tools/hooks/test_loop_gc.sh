#!/usr/bin/env bash
# Hermetic test for loop_gc_worktrees (U-HK-26). Builds a throwaway repo with several
# worktrees and asserts the safe-subset gate: reap ONLY merged worktrees that are
# non-current, non-main, and free of real local state — where "real local state"
# means tracked changes, untracked files, OR a non-allowlisted IGNORED file (.env etc.;
# `git worktree remove` deletes ignored files, so the gate must be ignored-aware —
# codex P2 2026-06-03). Regenerable ignored state (.harness/ runtime, caches) does NOT
# block a reap. `_loop_gc_gh_ok` + `_loop_gc_merged_oid` are stubbed (no real gh/network).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

# Canonicalize the temp base up-front so macOS /var → /private/var symlink resolution
# can't make `rev-parse --show-toplevel` disagree with `worktree list` paths.
BASE="$(cd "$(mktemp -d)" && pwd -P)"
{ [ -n "$BASE" ] && [ -d "$BASE" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$BASE"' EXIT

# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
# shellcheck source=loop_lib.sh
. "$SCRIPT_DIR/loop_lib.sh"

# Build the fixture: a main repo (with .gitignore) + linked worktrees.
build_fixture() {
  rm -rf "$BASE"/* "$BASE"/.[!.]* 2>/dev/null || true
  git init -q -b main "$BASE/main"
  git -C "$BASE/main" config user.email t@t
  git -C "$BASE/main" config user.name t
  printf '.harness/\n.env\n__pycache__/\n.claude/settings.local.json\n' > "$BASE/main/.gitignore"
  # A tracked file under .claude/ (mirrors the real repo) so git's --ignored does NOT
  # collapse the dir to a bare `!! .claude/` — it reports `!! .claude/settings.local.json`.
  mkdir -p "$BASE/main/.claude"; echo '{}' > "$BASE/main/.claude/settings.json"
  git -C "$BASE/main" add .gitignore .claude/settings.json
  git -C "$BASE/main" commit -q -m init
  git -C "$BASE/main" worktree add -q "$BASE/wt-merged"   -b feat-merged
  git -C "$BASE/main" worktree add -q "$BASE/wt-dirty"    -b feat-dirty
  git -C "$BASE/main" worktree add -q "$BASE/wt-unmerged" -b feat-unmerged
  git -C "$BASE/main" worktree add -q "$BASE/wt-precious" -b feat-precious
  git -C "$BASE/main" worktree add -q "$BASE/wt-settings" -b feat-settings
  git -C "$BASE/main" worktree add -q "$BASE/wt-collision" -b feat-collision
  git -C "$BASE/wt-collision" commit -q --allow-empty -m "new work after the merged PR"  # HEAD advances past the merged oid
  # wt-merged carries ONLY regenerable-allowlisted ignored state → must still reap.
  mkdir -p "$BASE/wt-merged/.harness"; echo runtime > "$BASE/wt-merged/.harness/loop_status.md"
  : > "$BASE/wt-dirty/untracked.txt"        # untracked non-ignored → dirty → keep
  echo SECRET > "$BASE/wt-precious/.env"    # non-allowlisted ignored → has local state → keep
  # wt-settings carries ONLY .claude/settings.local.json (allowlisted regenerable cache)
  # → must still reap (intentional per loop_lib.sh allowlist; codex P2 follow-up).
  mkdir -p "$BASE/wt-settings/.claude"; echo '{}' > "$BASE/wt-settings/.claude/settings.local.json"
}

wt_present() { git -C "$BASE/main" worktree list --porcelain 2>/dev/null | grep -qxF "worktree $BASE/$1"; }

# gh is "available"; the per-branch merged-oid lookup is stubbed. feat-merged / dirty /
# precious / settings / collision are "merged at main's init oid"; feat-unmerged is NOT
# (isolates the merged gate). Every worktree except wt-collision sits at that oid → HEAD
# matches; wt-collision's HEAD advanced → the exact-SHA gate skips it. Dirty/precious are
# merged but kept by the other gates.
_loop_gc_gh_ok() { return 0; }
_loop_gc_merged_oid() {
  local oid; oid=$(git -C "$BASE/main" rev-parse main 2>/dev/null)
  case "$1" in
    feat-merged|feat-dirty|feat-precious|feat-settings|feat-collision) printf '%s' "$oid" ;;
    *) : ;;   # feat-unmerged etc. → empty (not merged)
  esac
}

# ── 1) reap from main: only merged + truly-reapable is removed ─────────────────
build_fixture
export CLAUDE_PROJECT_DIR="$BASE/main"
loop_gc_worktrees reap
wt_present wt-merged   && bad "reap left merged worktree (allowlisted-ignored should not block)" || ok "reaped merged worktree (regenerable ignored OK)"
wt_present wt-dirty    && ok "kept dirty worktree (untracked gate)"     || bad "removed dirty worktree"
wt_present wt-unmerged && ok "kept unmerged worktree (merged gate)"     || bad "removed unmerged worktree"
wt_present wt-precious && ok "kept worktree with .env (ignored-aware gate)" || bad "removed worktree holding .env"
[ -f "$BASE/wt-precious/.env" ] && ok ".env preserved (never silently deleted)" || bad ".env was deleted"
wt_present wt-settings && bad "kept worktree with only settings.local.json (should reap — allowlisted)" || ok "reaped worktree w/ only settings.local.json (allowlisted cache)"
wt_present wt-collision && ok "kept name-collision worktree (HEAD advanced past merged oid)" || bad "reaped a worktree whose HEAD was never merged (name collision)"
git -C "$BASE/main" rev-parse --verify -q refs/heads/feat-merged >/dev/null \
  && ok "merged branch ref preserved (worktrees only)" || bad "branch ref was deleted"

# ── 2) gh unavailable → zero removals (fail-safe) ─────────────────────────────
build_fixture
_loop_gc_gh_ok() { return 1; }   # gh offline / unauth / not installed
loop_gc_worktrees reap
wt_present wt-merged && ok "gh unavailable → no removal (fail-safe)" || bad "removed a worktree while gh unavailable"
_loop_gc_gh_ok() { return 0; }   # restore for subsequent cases

# ── 3) report mode is read-only + lists only the reapable candidate ───────────
build_fixture
OUT="$(loop_gc_worktrees report)"
printf '%s\n' "$OUT" | grep -qF "$BASE/wt-merged (feat-merged)" && ok "report lists reapable candidate" || bad "report missed candidate"
printf '%s\n' "$OUT" | grep -qE "wt-dirty|wt-unmerged|wt-precious" && bad "report listed a non-candidate" || ok "report excludes non-candidates"
wt_present wt-merged && ok "report removed nothing (read-only)" || bad "report deleted a worktree"

# Candidate observation is not removal authority: a SessionStart lease registered after
# report/classification must still be rechecked by the real loop reap path.
LIVE_HOME="$BASE/live-home"; mkdir -p "$LIVE_HOME"
OLDHOME="$HOME"; export HOME="$LIVE_HOME"
hook_register_session_lease "$BASE/wt-merged" "classified-live"
hook_activate_session_lease "$BASE/wt-merged" "classified-live"
CLASSIFIED_LEASE=$(find "$BASE/main/.git/codex-worktree-sessions" -name 'session-classified-live.lease' -print -quit)
[ "$(head -n1 "$CLASSIFIED_LEASE" 2>/dev/null)" = "active" ] \
  && ok "loop reap witness reaches active lease" || bad "loop reap witness did not activate lease"
touch -t 202001010000 "$CLASSIFIED_LEASE"
loop_gc_worktrees reap
wt_present wt-merged && ok "loop reap rechecks lease after candidate report" \
  || bad "loop reap removed candidate after SessionStart lease"
hook_release_session_lease "$BASE/wt-merged" "classified-live"
export HOME="$OLDHOME"

# ── 4) self-exclusion: current worktree is never reaped ───────────────────────
build_fixture
export CLAUDE_PROJECT_DIR="$BASE/wt-merged"   # we ARE the merged+clean worktree now
loop_gc_worktrees reap
wt_present wt-merged && ok "self-exclusion: current worktree not reaped" || bad "reaped the current worktree"
export CLAUDE_PROJECT_DIR="$BASE/main"

# ── 5) self-exclusion canonicalizes (symlink spelling differs from current) ────
# path = a symlink to wt-merged; current = canonical wt-merged. Different STRINGS, same
# physical dir. Without `pwd -P` canonicalization the string compare misses and the
# current worktree would be reaped (codex P2). Call _loop_gc_consider directly to drive
# the exact mismatch deterministically.
build_fixture
ln -s "$BASE/wt-merged" "$BASE/sym-merged"
_loop_gc_consider "$BASE/sym-merged" feat-merged "$BASE/wt-merged" main reap "$BASE/main"
wt_present wt-merged && ok "self-exclusion canonicalizes path vs current (symlink-proof)" || bad "reaped current worktree via symlinked path spelling"

# ── 6) live-session guard: a merged+clean worktree with a RECENT transcript is kept ──
# (the council-context-memory orphaning, 2026-06-04). Override HOME so the synthetic
# transcript lands under a throwaway projects dir, not the real ~/.claude.
build_fixture
FH="$BASE/fakehome"
ENC=$(printf '%s' "$(cd "$BASE/wt-merged" && pwd -P)" | tr -c '[:alnum:]' '-')
mkdir -p "$FH/.claude/projects/$ENC"; : > "$FH/.claude/projects/$ENC/live.jsonl"   # fresh = live
OLDHOME="$HOME"; export HOME="$FH"
loop_gc_worktrees reap
export HOME="$OLDHOME"
wt_present wt-merged && ok "live-session worktree kept (not reaped despite merged+clean)" || bad "reaped a worktree with a live session"

# stale transcript (older than the window) must NOT block the reap
build_fixture
ENC=$(printf '%s' "$(cd "$BASE/wt-merged" && pwd -P)" | tr -c '[:alnum:]' '-')
mkdir -p "$FH/.claude/projects/$ENC"; : > "$FH/.claude/projects/$ENC/old.jsonl"
touch -t 202001010000 "$FH/.claude/projects/$ENC/old.jsonl"
export HOME="$FH"
loop_gc_worktrees reap
export HOME="$OLDHOME"
wt_present wt-merged && bad "stale transcript wrongly blocked the reap" || ok "stale-transcript worktree still reaped (window-bounded)"

# Codex transcript venue: session_meta.cwd in ~/.codex/sessions must protect the same
# worktree, not only Claude's encoded project transcript directory.
build_fixture
mkdir -p "$FH/.codex/sessions/2026/08/01"
printf '%s\n' "{\"type\":\"session_meta\",\"payload\":{\"cwd\":\"$BASE/wt-merged\"}}" \
  > "$FH/.codex/sessions/2026/08/01/rollout-live.jsonl"
export HOME="$FH"
loop_gc_worktrees reap
export HOME="$OLDHOME"
wt_present wt-merged && ok "Codex live-session worktree kept" || bad "reaped a worktree with a live Codex session"

# The public loop GC entrypoint must preserve safe refusal/recovery dispositions 7/8/9/10.
for REMOVE_CASE in \
  '7:process retains a reference' \
  '8:restored interrupted quarantine' \
  '9:process-reference state unavailable' \
  '10:branch or HEAD changed after classification'; do
  build_fixture
  export CLAUDE_PROJECT_DIR="$BASE/main"
  FORCED_REMOVE_RC=${REMOVE_CASE%%:*}
  EXPECTED_LOG=${REMOVE_CASE#*:}
  REMOVE_LOG="$BASE/remove-${FORCED_REMOVE_RC}.log"
  hook_safe_worktree_remove() { return "$FORCED_REMOVE_RC"; }
  loop_log() { printf '%s\n' "$*" >> "$REMOVE_LOG"; }
  loop_gc_worktrees reap
  grep -qF "$EXPECTED_LOG" "$REMOVE_LOG" \
    && ok "loop GC maps safe removal rc $FORCED_REMOVE_RC" \
    || bad "loop GC lost safe removal rc $FORCED_REMOVE_RC"
done

echo
echo "RESULT: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

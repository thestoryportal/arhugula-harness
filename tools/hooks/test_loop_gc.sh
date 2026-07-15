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

# ── loop_gc_branches: branch-ref GC (extends U-HK-26 to `git branch -D`) ──────
# Separate, simpler fixture: plain local branches on the main repo (no linked
# worktrees involved), since the branch-GC gate is orthogonal to the worktree
# safe-subset gate above. Scope trimmed 2026-07-15 (operator correction) to
# match the simplified mechanism: no freshness window, no cursor, no cap —
# every branch always gets a live CI check.
branch_present() { git -C "$BASE/main" rev-parse --verify -q "refs/heads/$1" >/dev/null 2>&1; }

build_branch_fixture() {
  rm -rf "$BASE"/* "$BASE"/.[!.]* 2>/dev/null || true
  git init -q -b main "$BASE/main"
  git -C "$BASE/main" config user.email t@t
  git -C "$BASE/main" config user.name t
  git -C "$BASE/main" commit -q --allow-empty -m init
  # Self-referential local "origin" — the reap path does a genuine `git
  # ls-remote`/`git push` against it, not a stub.
  git -C "$BASE/main" remote add origin "$BASE/main"
  git -C "$BASE/main" branch b-merged-green main
  git -C "$BASE/main" branch b-merged-red main
  git -C "$BASE/main" branch b-merged-unknown main
  git -C "$BASE/main" branch b-no-merge-oid main
  MERGED_OID=$(git -C "$BASE/main" rev-parse main)
  git -C "$BASE/main" branch b-unmerged main
  git -C "$BASE/main" branch b-collision main
  git -C "$BASE/main" commit -q --allow-empty -m "advance past the merged oid"
  # Give b-collision NEW work so its tip no longer equals the merged oid.
  git -C "$BASE/main" checkout -q -b b-collision-work b-collision
  git -C "$BASE/main" commit -q --allow-empty -m "unmerged follow-up work"
  git -C "$BASE/main" branch -f b-collision b-collision-work >/dev/null 2>&1
  git -C "$BASE/main" checkout -q main
  git -C "$BASE/main" branch -D b-collision-work >/dev/null 2>&1
  # b-checked-out: merged + CI green, but currently checked out in a worktree.
  git -C "$BASE/main" branch b-checked-out "$MERGED_OID"
  git -C "$BASE/main" worktree add -q "$BASE/wt-checked-out" b-checked-out >/dev/null 2>&1
}

# gh "available"; bulk-index stub covers everything EXCEPT b-unmerged (never
# merged) and b-collision (index entry present, but the REAL tip has since
# diverged from it). b-no-merge-oid deliberately has an EMPTY mergeCommit.oid
# field (simulates gh's field being absent). headRefOid == mergeCommit.oid
# elsewhere since the gating logic under test (exact-tip match / CI target)
# is orthogonal to whether the real pre- vs post-squash SHAs differ.
_loop_gc_gh_ok() { return 0; }
build_branch_index() {
  printf 'b-merged-green\t%s\t%s\n' "$MERGED_OID" "$MERGED_OID"
  printf 'b-merged-red\t%s\t%s\n' "$MERGED_OID" "$MERGED_OID"
  printf 'b-merged-unknown\t%s\t%s\n' "$MERGED_OID" "$MERGED_OID"
  printf 'b-no-merge-oid\t%s\t\n' "$MERGED_OID"
  printf 'b-collision\t%s\t%s\n' "$MERGED_OID" "$MERGED_OID"
  printf 'b-checked-out\t%s\t%s\n' "$MERGED_OID" "$MERGED_OID"
}
_loop_gc_merged_pr_tsv() { build_branch_index; }
# Per-branch CI stub: dispatches off a test-set wrapper var naming which
# fixture branch is under test at call time (multiple branches share the
# same merge SHA in this fixture, so the SHA alone can't disambiguate).
_BRANCH_UNDER_TEST=""
_loop_gc_ci_green_for_commit() {
  case "$_BRANCH_UNDER_TEST" in
    b-merged-green|b-checked-out) return 0 ;;
    b-merged-red) return 1 ;;
    *) return 2 ;;
  esac
}

# ── 7) reap: exact-SHA + checked-out + live CI-green gates, all together ──────
build_branch_fixture
export CLAUDE_PROJECT_DIR="$BASE/main"
IDX="$(build_branch_index)"
for b in b-merged-green b-merged-red b-merged-unknown b-no-merge-oid b-unmerged b-collision b-checked-out; do
  _BRANCH_UNDER_TEST="$b"
  _loop_gc_consider_branch "$b" main reap "$BASE/main" "$IDX"
done
branch_present b-merged-green   && bad "b-merged-green not reaped (merged + CI confirmed green)" || ok "reaped b-merged-green (merged + live CI green)"
branch_present b-merged-red     && ok "kept b-merged-red (CI NOT green — held)" || bad "b-merged-red wrongly reaped (CI red)"
branch_present b-merged-unknown && ok "kept b-merged-unknown (CI conclusion unknown — fail-safe hold)" || bad "b-merged-unknown wrongly reaped (CI unknown)"
branch_present b-no-merge-oid   && ok "kept b-no-merge-oid (missing mergeCommit.oid — fail-closed hold)" || bad "b-no-merge-oid wrongly reaped (no mergeCommit.oid to verify CI against)"
branch_present b-unmerged       && ok "kept b-unmerged (no merged PR by this name)" || bad "b-unmerged wrongly reaped (no merged PR)"
branch_present b-collision      && ok "kept b-collision (tip no longer matches merged oid)" || bad "b-collision wrongly reaped (tip diverged from merged oid)"
branch_present b-checked-out    && ok "kept b-checked-out (checked out in a worktree)" || bad "b-checked-out wrongly reaped (live in a linked worktree)"
git -C "$BASE/main" worktree remove -f "$BASE/wt-checked-out" >/dev/null 2>&1 || true

# ── 8) report mode is read-only ────────────────────────────────────────────────
build_branch_fixture
_BRANCH_UNDER_TEST="b-merged-green"
OUT=$(_loop_gc_consider_branch b-merged-green main report "$BASE/main" "$(build_branch_index)")
printf '%s' "$OUT" | grep -qF "b-merged-green" && ok "report lists a reapable branch candidate" || bad "report missed a candidate"
branch_present b-merged-green && ok "report mode deleted nothing" || bad "report mode deleted a branch"
git -C "$BASE/main" worktree remove -f "$BASE/wt-checked-out" >/dev/null 2>&1 || true

# ── 9) gh unavailable → zero removals (fail-safe) ─────────────────────────────
build_branch_fixture
_loop_gc_gh_ok() { return 1; }
loop_gc_branches reap
branch_present b-merged-green && ok "gh unavailable → branch not reaped (fail-safe)" || bad "reaped a branch while gh unavailable"
_loop_gc_gh_ok() { return 0; }
git -C "$BASE/main" worktree remove -f "$BASE/wt-checked-out" >/dev/null 2>&1 || true

# ── 10) unrecognized mode refuses rather than falling through to reap ─────────
build_branch_fixture
_BRANCH_UNDER_TEST="b-merged-green"
_loop_gc_consider_branch b-merged-green main reports "$BASE/main" "$(build_branch_index)"
branch_present b-merged-green && ok "mode typo ('reports') refused, not silently reaped" || bad "mode typo caused an uncapped destructive delete"
loop_gc_branches reports >/dev/null 2>&1
branch_present b-merged-green && ok "loop_gc_branches: mode typo caused zero deletions" || bad "loop_gc_branches: mode typo caused an uncapped destructive delete"
LEDGER=$(loop_status_path)
[ -f "$LEDGER" ] && grep -qi "unrecognized mode" "$LEDGER" && ok "loop_gc_branches logs the rejection to the ledger" || bad "loop_gc_branches did not log the mode rejection"
git -C "$BASE/main" worktree remove -f "$BASE/wt-checked-out" >/dev/null 2>&1 || true

echo
echo "RESULT: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

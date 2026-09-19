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

# C-HE-09 §2 (U-HE-29): the ledger is a SHARED venue resolved from the ENVIRONMENT, not from
# the repo under test. loop_gc_worktrees logs GC rows, so without this pin a "hermetic" run
# appends them to the operator's real ~/.gstack ledger — durable user state mutated by a test
# (codex r7 P3; the same class already leaked four rows during this arc).
export HARNESS_LOOP_STATUS_PATH="${TMPDIR:-/tmp}/loop-gc-test-$$-loop_status.md"

{ [ -n "$BASE" ] && [ -d "$BASE" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
# Detached reapers launched by case 7 carry the scratch hooks dir (under $BASE) in their
# argv. Any still running when the suite ends — a timed-out wait, an early exit — is killed
# before the fixture is deleted, so none outlives the suite or acts on a vanished tree.
# A killed reaper is waited for (TERM, then KILL after 2 s) so none is still acting on the
# fixture when the caller deletes it. They are not this shell's children, so liveness is
# polled rather than `wait`ed.
kill_leftover_reapers() {
  local roots pids alive pid waited=0
  roots=$(pgrep -f "loop-gc-reap $BASE/") || return 0
  # A reaper blocked on an exec'd child (git, gh, sleep) does not pass TERM on, and once it
  # dies that child is reparented to init and no longer a pgrep -P descendant — so the whole
  # tree is snapshotted BEFORE anything is signalled, and every member is killed and waited.
  pids=$(for pid in $roots; do tree_pids "$pid"; done)
  kill $pids 2>/dev/null
  echo "  note: killed leftover detached reaper(s): $(printf '%s' "$roots" | tr '\n' ' ')"
  while :; do
    alive=""
    for pid in $pids; do kill -0 "$pid" 2>/dev/null && alive="$alive $pid"; done
    [ -z "$alive" ] && return 0
    [ "$waited" -eq 20 ] && kill -KILL $alive 2>/dev/null
    if [ "$waited" -ge 40 ]; then
      echo "  FATAL: reaper process(es) survived KILL:$alive"
      return 1
    fi
    sleep 0.1; waited=$((waited + 1))
  done
}
# Print <pid> and every descendant, one per line.
tree_pids() {
  local child
  printf '%s\n' "$1"
  for child in $(pgrep -P "$1"); do tree_pids "$child"; done
}
# Kill <pid> and every descendant, deepest first.
kill_tree() {
  local child
  for child in $(pgrep -P "$1"); do kill_tree "$child"; done
  kill "$1" 2>/dev/null
}
# One EXIT trap only — bash REPLACES the handler rather than chaining, so the ledger pin's
# cleanup has to live here rather than in a second trap.
trap 'kill_leftover_reapers; rm -rf "$BASE"; rm -f "$HARNESS_LOOP_STATUS_PATH"' EXIT

# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
# shellcheck source=loop_lib.sh
. "$SCRIPT_DIR/loop_lib.sh"
# Keep the production merged-oid lookup reachable under another name before the stubs below
# replace it, so case 5e can drive the real gh argv.
eval "$(declare -f _loop_gc_merged_oid | sed '1s/^_loop_gc_merged_oid/_real_loop_gc_merged_oid/')"

# GC classification/recheck tests need a deterministic clean reference scan on
# Linux runners whose ptrace policy makes unrelated same-user /proc entries
# unreadable. Real retained/unavailable observer behavior is covered by test_lib.sh;
# this suite separately preserves the public rc 7/8/9/10 mapping witnesses below.
_hook_worktree_open_references() { return 1; }

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
  for w in wt-merged wt-dirty wt-unmerged wt-precious wt-settings wt-collision; do
    age_admin "$BASE/$w"
  done
}

# Age a worktree's git admin files (index, HEAD reflog) past the reaper's idle grace, so a
# freshly built fixture reads as an idle worktree rather than one a session just used.
age_admin() {
  local rel f
  for rel in index logs/HEAD; do
    f=$(git -C "$1" rev-parse --path-format=absolute --git-path "$rel") || return 1
    [ -e "$f" ] && touch -t 202001010000 "$f"
  done
  return 0
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
HARNESS_CODEX_SESSION_OWNER_PID="$$" \
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

# ── 3b) U-CTX-08: loop-gc.sh's SessionStart hygiene block caps the stale-worktree
#      list at 3 + "(+N more)" (reusing loop_lib.sh's loop_cap_list, shared with
#      loop_pending_hil_summary — see test_loop_lib.sh). The library's `report` mode
#      itself stays UNCAPPED (it's the read-only candidate-enumeration API; the cap is
#      a presentation concern owned by the hook that renders SessionStart context), so
#      this drives a REAL 4-candidate report through the exact cap the hook applies.
rm -rf "$BASE"/* "$BASE"/.[!.]* 2>/dev/null || true
git init -q -b main "$BASE/main"
git -C "$BASE/main" config user.email t@t
git -C "$BASE/main" config user.name t
git -C "$BASE/main" commit -q -m init --allow-empty
for b in feat-a feat-b feat-c feat-d; do
  git -C "$BASE/main" worktree add -q "$BASE/wt-$b" -b "$b"
  age_admin "$BASE/wt-$b"
done
_loop_gc_gh_ok() { return 0; }
_loop_gc_merged_oid() {
  local oid; oid=$(git -C "$BASE/main" rev-parse main 2>/dev/null)
  case "$1" in feat-a|feat-b|feat-c|feat-d) printf '%s' "$oid" ;; *) : ;; esac
}
export CLAUDE_PROJECT_DIR="$BASE/main"
CANDS4=$(loop_gc_worktrees report)
N4=$(printf '%s\n' "$CANDS4" | grep -c .)
[ "$N4" -eq 4 ] && ok "U-CTX-08 fixture: report lists all 4 reapable candidates (library API stays uncapped)" || bad "U-CTX-08 fixture: report count $N4 != 4: [$CANDS4]"
CAPPED4=$(printf '%s\n' "$CANDS4" | loop_cap_list)
printf '%s' "$CAPPED4" | grep -q '(+1 more)' && ok "U-CTX-08: 4 real stale-worktree candidates cap to 3 + '(+1 more)'" || bad "U-CTX-08 cap on real CANDS: [$CAPPED4]"
[ "$(printf '%s' "$CAPPED4" | tr ';' '\n' | grep -c 'wt-feat-')" -eq 3 ] && ok "U-CTX-08: capped rendering names exactly 3 candidates" || bad "U-CTX-08 capped list wrong length: [$CAPPED4]"
# Restore the build_fixture-compatible stubs (feat-merged/feat-dirty/...) for every
# test below — this block's narrower feat-a..d stub must not leak past its own scope.
_loop_gc_gh_ok() { return 0; }
_loop_gc_merged_oid() {
  local oid; oid=$(git -C "$BASE/main" rev-parse main 2>/dev/null)
  case "$1" in
    feat-merged|feat-dirty|feat-precious|feat-settings|feat-collision) printf '%s' "$oid" ;;
    *) : ;;
  esac
}

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

# ── 5b) idle grace fails closed: an unresolvable git admin path skips, never removes ──
# git is wrapped so that resolving wt-merged's admin paths (--git-path) fails while HEAD
# still resolves at the merged oid, the one state that reaches the activity check.
build_fixture
git() {
  case " $* " in *" -C $BASE/wt-merged "*" --git-path "*) return 128 ;; esac
  command git "$@"
}
_loop_gc_consider "$BASE/wt-merged" feat-merged "$BASE/main" main reap "$BASE/main"
unset -f git
wt_present wt-merged && ok "idle grace: unresolvable git activity state keeps the worktree" \
  || bad "idle grace: removed a worktree whose git activity state could not be read"
grep -qF "skipped $BASE/wt-merged (feat-merged) — git activity state unavailable" "$HARNESS_LOOP_STATUS_PATH" \
  && ok "idle grace: the fail-closed skip is logged" || bad "idle grace: no GC row for the unavailable activity state"

# ── 5c) C-HE-04 §6 (v1.10 X10): a squash-merged worktree is reaped ─────────────
# The real squash-merge shape: the arc branch is created from origin/main and tracks it,
# and its own commit never enters the upstream, so it is ahead of @{u} forever. Merged at
# its exact head, clean and idle, it must be reaped; the same worktree with an uncommitted
# change must be kept.
squash_fixture() {
  build_fixture
  git init -q --bare "$BASE/origin.git"
  git -C "$BASE/main" remote add origin "$BASE/origin.git"
  git -C "$BASE/main" push -q origin main 2>/dev/null
  git -C "$BASE/main" fetch -q origin
  git -C "$BASE/main" worktree add -q --track -b feat-squash "$BASE/wt-squash" origin/main
  git -C "$BASE/wt-squash" commit -q --allow-empty -m "arc work, squash-merged upstream"
  age_admin "$BASE/wt-squash"
}
_loop_gc_merged_oid() {
  case "$1" in
    feat-squash) git -C "$BASE/wt-squash" rev-parse HEAD 2>/dev/null ;;
    *) : ;;
  esac
}
squash_fixture
[ "$(git -C "$BASE/wt-squash" rev-list --count '@{u}..HEAD')" = "1" ] \
  && ok "X10 fixture: the squash-merged worktree is ahead of its upstream" \
  || bad "X10 fixture: worktree is not ahead of its upstream"
loop_gc_worktrees report | grep -qF "$BASE/wt-squash (feat-squash)" \
  && ok "X10: report lists the squash-merged worktree" || bad "X10: report omitted the squash-merged worktree"
loop_gc_worktrees reap
wt_present wt-squash && bad "X10: ahead-of-upstream merged-at-head worktree was not reaped" \
  || ok "X10: ahead-of-upstream merged-at-head worktree reaped"
git -C "$BASE/main" rev-parse --verify -q refs/heads/feat-squash >/dev/null \
  && ok "X10: the squash-merged branch ref is left in place" || bad "X10: branch ref was deleted"
squash_fixture
: > "$BASE/wt-squash/uncommitted.txt"
age_admin "$BASE/wt-squash"
loop_gc_worktrees reap
wt_present wt-squash && ok "X10: merged-at-head worktree with an uncommitted change kept" \
  || bad "X10: reaped a merged worktree holding an uncommitted change"

# ── 5d) X10 through the reaper when the upstream no longer resolves ────────────
# After a squash merge the remote branch is deleted and the tracking ref pruned, while
# branch.<name>.merge stays configured, so @{u} stops resolving. Merged at its exact head,
# clean and idle, the worktree must still be reaped; with an uncommitted change it is kept.
squash_fixture
git -C "$BASE/main" update-ref -d refs/remotes/origin/main
git -C "$BASE/wt-squash" config --get branch.feat-squash.merge >/dev/null \
  && ! git -C "$BASE/wt-squash" rev-parse -q --verify '@{u}' >/dev/null 2>&1 \
  && ok "X10 fixture: upstream configured but unresolvable" \
  || bad "X10 fixture: upstream is not configured-but-unresolvable"
loop_gc_worktrees reap
wt_present wt-squash && bad "X10: unresolvable-upstream merged-at-head worktree was not reaped" \
  || ok "X10: unresolvable-upstream merged-at-head worktree reaped"
squash_fixture
git -C "$BASE/main" update-ref -d refs/remotes/origin/main
: > "$BASE/wt-squash/uncommitted.txt"
age_admin "$BASE/wt-squash"
loop_gc_worktrees reap
wt_present wt-squash && ok "X10: unresolvable-upstream worktree with an uncommitted change kept" \
  || bad "X10: reaped an unresolvable-upstream worktree holding an uncommitted change"

# ── 5e) the real merged-oid lookup only accepts PRs merged into the default branch ──
# X10's waiver rests on the merge having put the content on the DEFAULT branch. A fake `gh`
# on PATH plays a server holding one PR per branch: feat-trunk merged into the default
# branch (trunk, via origin/HEAD, so the base is resolved and not hard-coded), feat-release
# merged only into `release`. It records its argv and answers only the base it is asked for.
BASE_REPO="$BASE/base-repo"; FAKE_BIN="$BASE/fake-gh-bin"; GH_ARGV="$BASE/gh-argv"
git init -q -b trunk "$BASE_REPO"
git -C "$BASE_REPO" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/trunk
mkdir -p "$FAKE_BIN"
cat > "$FAKE_BIN/gh" <<'FAKE'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$GH_ARGV"
base=""; head=""
while [ "$#" -gt 0 ]; do
  case "$1" in --base) base="$2"; shift ;; --head) head="$2"; shift ;; esac
  shift
done
case "$head:$base" in
  feat-trunk:trunk|feat-trunk:) printf 'aaaa1111\n' ;;
  feat-release:release|feat-release:) printf 'bbbb2222\n' ;;
esac
exit 0
FAKE
chmod +x "$FAKE_BIN/gh"
: > "$GH_ARGV"
TRUNK_OID=$(GH_ARGV="$GH_ARGV" PATH="$FAKE_BIN:$PATH" _real_loop_gc_merged_oid feat-trunk "$BASE_REPO")
RELEASE_OID=$(GH_ARGV="$GH_ARGV" PATH="$FAKE_BIN:$PATH" _real_loop_gc_merged_oid feat-release "$BASE_REPO")
[ "$TRUNK_OID" = "aaaa1111" ] && ok "merged-oid: a PR merged into the default branch is the proof" \
  || bad "merged-oid: default-branch PR not found: '$TRUNK_OID'"
[ -z "$RELEASE_OID" ] && ok "merged-oid: a PR merged only into a non-default branch proves nothing" \
  || bad "merged-oid: a non-default-base merge counted as proof: '$RELEASE_OID'"
[ "$(grep -c -- '--base trunk' "$GH_ARGV")" -eq 2 ] \
  && ok "merged-oid: every lookup passes --base <default branch>" \
  || bad "merged-oid: gh argv lacks --base trunk: [$(tr '\n' ';' < "$GH_ARGV")]"
_loop_gc_merged_oid() {
  local oid; oid=$(git -C "$BASE/main" rev-parse main 2>/dev/null)
  case "$1" in
    feat-merged|feat-dirty|feat-precious|feat-settings|feat-collision) printf '%s' "$oid" ;;
    *) : ;;
  esac
}

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

# ── 6b) single-flight: one reaper per repository ──────────────────────────────
# Concurrent session starts each launch a reaper. With the repository reap lock held by
# another LIVE process, a reaper removes nothing and logs the skip; once that holder dies
# the kernel drops its lock and the next reaper takes over with no stale-lock cleanup.
build_fixture
export CLAUDE_PROJECT_DIR="$BASE/main"
SF_LOCK=$(_loop_gc_reap_lock_path "$BASE/main")
SF_READY="$BASE/sf-ready"
/usr/bin/python3 -c 'import fcntl,sys,time
f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); open(sys.argv[2], "w").close(); time.sleep(120)' \
  "$SF_LOCK" "$SF_READY" &
SF_HOLDER=$!
SF_WAITED=0
until [ -f "$SF_READY" ] || [ "$SF_WAITED" -ge 100 ]; do sleep 0.1; SF_WAITED=$((SF_WAITED + 1)); done
[ -f "$SF_READY" ] && ok "single-flight fixture: a live process holds the reap lock" \
  || bad "single-flight fixture: lock holder never signalled ready"
sf_skip_rows() { grep -c 'another reaper holds the repository reap lock' "$HARNESS_LOOP_STATUS_PATH" 2>/dev/null; }
# One reap from <project dir>, bounded to 15 s. A reaper facing a held lock skips at once;
# one that waits on the lock instead is killed here, so that defect fails in seconds
# rather than after the holder's 120 s.
sf_reap_bounded() {
  local pid waited=0
  ( export CLAUDE_PROJECT_DIR="$1"; loop_gc_worktrees reap ) &
  pid=$!
  while kill -0 "$pid" 2>/dev/null && [ "$waited" -lt 150 ]; do sleep 0.1; waited=$((waited + 1)); done
  if kill -0 "$pid" 2>/dev/null; then
    kill_tree "$pid"; wait "$pid" 2>/dev/null
    return 1
  fi
  wait "$pid"
}
SF_ROWS_BEFORE=$(sf_skip_rows)
sf_reap_bounded "$BASE/main" && ok "single-flight: a reaper facing the held lock returns without waiting on it" \
  || bad "single-flight: reaper still running after 15 s — it waited on the held lock instead of skipping"
wt_present wt-merged && ok "single-flight: reaper removed nothing while another holds the lock" \
  || bad "single-flight: reaper removed a worktree while another reaper held the lock"
[ "$(sf_skip_rows)" -eq $((SF_ROWS_BEFORE + 1)) ] \
  && ok "single-flight: the skip is logged as one GC row" || bad "single-flight: no GC row for the lock skip"
# The lock is per repository, not per worktree: a reaper started from a LINKED worktree
# (whose own git dir differs from the main checkout's) must contend for the same lock the
# main-checkout holder took. wt-dirty is not a candidate, and wt-merged still is.
sf_reap_bounded "$BASE/wt-dirty" && ok "single-flight: a linked-worktree reaper returns without waiting on the lock" \
  || bad "single-flight: linked-worktree reaper still running after 15 s"
wt_present wt-merged && ok "single-flight: a reaper started in a linked worktree sees the main checkout's lock held" \
  || bad "single-flight: a linked-worktree reaper removed a worktree while the repository lock was held"
[ "$(sf_skip_rows)" -eq $((SF_ROWS_BEFORE + 2)) ] \
  && ok "single-flight: the linked-worktree skip is logged" || bad "single-flight: no GC row for the linked-worktree lock skip"
kill "$SF_HOLDER" 2>/dev/null; wait "$SF_HOLDER" 2>/dev/null
loop_gc_worktrees reap
wt_present wt-merged && bad "single-flight: a dead holder's lock blocked the next reaper" \
  || ok "single-flight: after the holder dies the next reaper takes the lock and reaps"

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

# ── 7) SessionStart autonomously reaps (operator directive 2026-09-19) ─────────
# Drives the REAL hook script as a subprocess. The detached reaper is a fresh process,
# so the test shell's function stubs cannot reach it; instead the hook is run from a
# scratch hooks dir holding a byte-identical copy of loop-gc.sh and lib.sh plus a copy
# of loop_lib.sh with the stubs appended. The reaper only sees them if it sources its
# libraries from the hook's own directory — the contract under test. The stubbed
# merged-oid lookup is fast on a branch's FIRST call (the hook's synchronous report)
# and slow on feat-merged's SECOND (the reaper's), so a hook that waited on the reaper
# would take at least REAP_DELAY; the process-reference observer is stubbed clean for the same
# Linux ptrace reason as at the top of this file.
# Two more merged+clean worktrees join the fixture: wt-settings carries an ACTIVE live
# session lease (the reaper must re-check it under the removal mutex), and wt-fresh is
# brand new, so its index sits inside the idle grace.
build_fixture
export CLAUDE_PROJECT_DIR="$BASE/main"
git -C "$BASE/main" worktree add -q "$BASE/wt-fresh" -b feat-fresh
hook_register_session_lease "$BASE/wt-settings" "autoreap-live"
HARNESS_CODEX_SESSION_OWNER_PID="$$" hook_activate_session_lease "$BASE/wt-settings" "autoreap-live"
AR_LEASE=$(find "$BASE/main/.git/codex-worktree-sessions" -name 'session-autoreap-live.lease' -print -quit)
[ "$(head -n1 "$AR_LEASE" 2>/dev/null)" = "active" ] \
  && ok "autoreap fixture: wt-settings holds an active live lease" || bad "autoreap fixture: lease not active"
AR_HOOKS="$BASE/autoreap-hooks"; AR_CALLS="$BASE/autoreap-calls"; AR_HOME="$BASE/autoreap-home"
mkdir -p "$AR_HOOKS" "$AR_CALLS" "$AR_HOME"
cp "$SCRIPT_DIR/loop-gc.sh" "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh" "$AR_HOOKS/"
REAP_DELAY=4
# The first reaper holds the reap lock for LINGER seconds after its scan finishes, as a
# loaded machine can: every ledger row is visible while it still holds the lock. A next
# hook run that does not wait for it to exit loses single-flight and never reaps.
LINGER=3
cat >> "$AR_HOOKS/loop_lib.sh" <<STUBS
eval "\$(declare -f _loop_gc_scan | sed '1s/^_loop_gc_scan/_ar_real_loop_gc_scan/')"
_loop_gc_scan() {
  _ar_real_loop_gc_scan "\$@"
  [ "\$1" = reap ] && [ ! -e "$AR_CALLS/lingered" ] && { : > "$AR_CALLS/lingered"; sleep $LINGER; }
  return 0
}
_loop_gc_gh_ok() { return 0; }
_hook_worktree_open_references() { return 1; }
_loop_gc_merged_oid() {
  local f="$AR_CALLS/\$1" n
  n=\$(( \$(cat "\$f" 2>/dev/null || echo 0) + 1 )); echo "\$n" > "\$f"
  [ "\$n" -ge 2 ] && [ "\$1" = feat-merged ] && sleep $REAP_DELAY
  case "\$1" in
    feat-merged|feat-dirty|feat-settings|feat-fresh) git -C "$BASE/main" rev-parse main ;;
    *) : ;;
  esac
}
STUBS
ar_now() { /usr/bin/python3 -c 'import time; print(time.time())'; }
ar_run() { HOME="$AR_HOME" bash "$AR_HOOKS/loop-gc.sh"; }
ar_logged() { grep -qF "$1" "$HARNESS_LOOP_STATUS_PATH" 2>/dev/null; }
# Poll (bounded) until <predicate> holds; on timeout kill any reaper still running so it
# cannot act on the fixture after the suite moves on or deletes it.
ar_wait() {
  local waited=0
  until "$@" || [ "$waited" -ge 60 ]; do sleep 1; waited=$((waited + 1)); done
  "$@" && return 0
  kill_leftover_reapers
  return 1
}
# Before the next hook run: every reaper this case launched has exited and released the
# reap lock. Ledger rows alone do not say that.
ar_reapers_gone() { ! pgrep -f "loop-gc-reap $AR_HOOKS" >/dev/null; }
AR_T0=$(ar_now)
AR_OUT=$(ar_run)
AR_ELAPSED=$(/usr/bin/python3 -c 'import sys; print(float(sys.argv[2]) - float(sys.argv[1]))' "$AR_T0" "$(ar_now)")
/usr/bin/python3 -c 'import sys; sys.exit(0 if float(sys.argv[1]) < float(sys.argv[2]) else 1)' "$AR_ELAPSED" "$REAP_DELAY" \
  && ok "autoreap: hook returned in ${AR_ELAPSED}s, before the reaper's ${REAP_DELAY}s lookup" \
  || bad "autoreap: hook took ${AR_ELAPSED}s — it waited on the reaper"
wt_present wt-merged && ok "autoreap: candidate still present when the hook returned (reap is detached)" \
  || bad "autoreap: candidate already gone at hook return — reap ran synchronously"
printf '%s' "$AR_OUT" | jq -r '.hookSpecificOutput.additionalContext' \
  | grep -qF "being reaped in the background" \
  && ok "autoreap: hygiene message says the candidates are being reaped" \
  || bad "autoreap: hygiene message wrong: $AR_OUT"
# Wait for EVERY disposition: the merged removal, the dirty / live-lease / idle-grace skips
# are ledger rows; the unmerged worktree returns silently after its second lookup, so its
# call counter is the completion witness.
ar_done() {
  ar_logged "reaped worktree $BASE/wt-merged" \
    && ar_logged "skipped $BASE/wt-dirty" \
    && ar_logged "skipped $BASE/wt-settings (feat-settings) — live Claude/Codex session" \
    && ar_logged "skipped $BASE/wt-fresh (feat-fresh) — git activity within" \
    && [ "$(cat "$AR_CALLS/feat-unmerged" 2>/dev/null)" = "2" ]
}
ar_wait ar_done && ok "autoreap: detached reaper finished" \
  || bad "autoreap: detached reaper never finished (ledger: $(tail -5 "$HARNESS_LOOP_STATUS_PATH" 2>/dev/null))"
wt_present wt-merged && bad "autoreap: merged+clean worktree was NOT reaped" \
  || ok "autoreap: merged+clean non-current worktree reaped with no manual step"
wt_present wt-dirty && ok "autoreap: dirty worktree left untouched" || bad "autoreap: removed a dirty worktree"
wt_present wt-unmerged && ok "autoreap: unmerged worktree left untouched" || bad "autoreap: removed an unmerged worktree"
[ -d "$BASE/main" ] && ok "autoreap: current (main) checkout untouched" || bad "autoreap: main checkout removed"
wt_present wt-settings && ok "autoreap: merged+clean worktree with an active live lease survives the reaper" \
  || bad "autoreap: reaper removed a worktree whose session lease is live"
wt_present wt-fresh && ok "autoreap: merged+clean worktree with a just-touched index is skipped (idle grace)" \
  || bad "autoreap: reaper removed a worktree with git activity inside the idle grace"

# Same worktree once idle: age its index and HEAD reflog past the grace, start another
# session. The hook's synchronous report runs `git status` on it first; the reap still
# lands only because that probe leaves the index it reads untouched.
age_admin "$BASE/wt-fresh"
ar_wait ar_reapers_gone && ok "autoreap: the first reaper exited before the next session start" \
  || bad "autoreap: the first reaper was still running after 60 s"
ar_run >/dev/null
ar_wait ar_logged "reaped worktree $BASE/wt-fresh" \
  && ok "autoreap: the same worktree is reaped once its git admin files are past the idle grace" \
  || bad "autoreap: aged worktree not reaped (ledger: $(tail -3 "$HARNESS_LOOP_STATUS_PATH" 2>/dev/null))"
wt_present wt-fresh && bad "autoreap: aged worktree still registered" || ok "autoreap: aged worktree removed"

# No candidates → no reaper. Every worktree left is gated (dirty, unmerged, precious,
# collision, live lease), so the report is empty. A launched reaper would make its own
# merged-oid lookup for feat-dirty after the report's; only the report's may happen.
ar_wait ar_reapers_gone && ok "autoreap: the second reaper exited before the next session start" \
  || bad "autoreap: the second reaper was still running after 60 s"
AR_DIRTY_BEFORE=$(cat "$AR_CALLS/feat-dirty")
AR_OUT3=$(ar_run)
[ -z "$AR_OUT3" ] && ok "no-candidates: hook emits no hygiene context" || bad "no-candidates: unexpected context: $AR_OUT3"
pgrep -f "loop-gc-reap $AR_HOOKS" >/dev/null \
  && bad "no-candidates: a reaper process is running" || ok "no-candidates: no reaper process at hook return"
ar_reaper_looked() { [ "$(cat "$AR_CALLS/feat-dirty")" -gt $((AR_DIRTY_BEFORE + 1)) ]; }
AR_WAITED=0
until ar_reaper_looked || [ "$AR_WAITED" -ge 5 ]; do sleep 1; AR_WAITED=$((AR_WAITED + 1)); done
[ "$(cat "$AR_CALLS/feat-dirty")" -eq $((AR_DIRTY_BEFORE + 1)) ] \
  && ok "no-candidates: only the report's lookup ran — no reaper was spawned" \
  || { bad "no-candidates: feat-dirty lookups went $AR_DIRTY_BEFORE → $(cat "$AR_CALLS/feat-dirty") (a reaper ran)"; kill_leftover_reapers; }
hook_release_session_lease "$BASE/wt-settings" "autoreap-live"

# The suite's cleanup must not return while a reaper it killed still runs. This stand-in
# ignores TERM and is orphaned (not this shell's child) like a real detached reaper.
( nohup bash -c 'trap "" TERM; while :; do sleep 0.2; done' loop-gc-reap "$BASE/stubborn-reaper" \
    </dev/null >/dev/null 2>&1 & )
KR_WAITED=0
until pgrep -f "loop-gc-reap $BASE/stubborn-reaper" >/dev/null || [ "$KR_WAITED" -ge 50 ]; do sleep 0.1; KR_WAITED=$((KR_WAITED + 1)); done
KR_PID=$(pgrep -f "loop-gc-reap $BASE/stubborn-reaper")
if [ -n "$KR_PID" ]; then
  kill_leftover_reapers >/dev/null
  kill -0 $KR_PID 2>/dev/null \
    && { bad "cleanup: a TERM-ignoring reaper was still alive when kill_leftover_reapers returned"; kill -KILL $KR_PID; } \
    || ok "cleanup: kill_leftover_reapers waits for a killed reaper to exit, escalating to KILL"
else
  bad "cleanup fixture: stand-in reaper never started"
fi

# A reaper killed while it waits on an exec'd child must not leave that child running: this
# stand-in blocks on a foreground `sleep` (TERM to the bash frame does not reach it), and
# the child must be gone when kill_leftover_reapers returns.
( nohup bash -c 'sleep 30; :' loop-gc-reap "$BASE/blocked-reaper" </dev/null >/dev/null 2>&1 & )
KB_WAITED=0; KB_CHILD=""
until [ -n "$KB_CHILD" ] || [ "$KB_WAITED" -ge 50 ]; do
  KB_ROOT=$(pgrep -f "loop-gc-reap $BASE/blocked-reaper")
  [ -n "$KB_ROOT" ] && KB_CHILD=$(pgrep -P "$KB_ROOT")
  [ -n "$KB_CHILD" ] || { sleep 0.1; KB_WAITED=$((KB_WAITED + 1)); }
done
if [ -n "$KB_CHILD" ]; then
  kill_leftover_reapers >/dev/null
  kill -0 $KB_CHILD 2>/dev/null \
    && { bad "cleanup: a killed reaper's exec'd child was still running when kill_leftover_reapers returned"; kill -KILL $KB_CHILD; } \
    || ok "cleanup: kill_leftover_reapers also stops a killed reaper's exec'd children"
else
  bad "cleanup fixture: blocked stand-in reaper or its child never started"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# U-HK-44 — unreconciled-subagent sweep + prune of .harness/.agents-registry.jsonl.
#
# These cases drive the HOOK itself (`bash loop-gc.sh`) as a subprocess against a
# throwaway CLAUDE_PROJECT_DIR: a NON-git scratch dir, so the worktree arm sees zero
# worktrees and stays inert, and HOME is redirected so the real MEMORY.md can never
# flag. The sweep clause is therefore the ONLY [hygiene] part in play.
HOOK="$SCRIPT_DIR/loop-gc.sh"
SW="$BASE/sweep"; mkdir -p "$SW/home"
SPROJ="$SW/proj"
SREG="$SPROJ/.harness/.agents-registry.jsonl"
SLOCK="$SPROJ/.harness/.agents-registry.lock"

sw_reset() { rm -rf "$SPROJ"; mkdir -p "$SPROJ/.harness"; : > "$SREG"; }
# ts N-seconds-ago, in the registry's UTC format.
sw_ts() { /usr/bin/python3 -c 'import sys,time; print(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time()-float(sys.argv[1]))))' "$1"; }
# stamp <file>'s mtime to EXACTLY <seconds> old. `touch -t` takes minute granularity
# (seconds truncate to :00), so a fixture stamped N minutes back is really aged anywhere
# in [N m 00 s, N m 59 s] depending on the wall-clock phase the suite happens to reach it
# at — up to 59s of the intended headroom silently gone. Harmless for the 2-hour fixtures
# below (90 min of slack against the 30-min STALE boundary), fatal for a near-boundary
# pin: see S16 (B-169).
sw_stamp() { /usr/bin/python3 -c 'import os,sys,time; t=time.time()-float(sys.argv[2]); os.utime(sys.argv[1],(t,t))' "$1" "$2"; }
# one registry row: sw_row <ts> <event> <agent_id> <transcript>
sw_row() { printf '{"ts":"%s","event":"%s","session":"s1","agent_id":"%s","transcript":"%s","cwd":"/w"}\n' "$1" "$2" "$3" "$4"; }
# inode + mtime, as one comparable string.
sw_ino() { /usr/bin/python3 -c 'import os,sys; s=os.stat(sys.argv[1]); print(s.st_ino, int(s.st_mtime))' "$1"; }
sw_run() { HOME="$SW/home" CLAUDE_PROJECT_DIR="$SPROJ" bash "$HOOK"; }
sw_ctx() { sw_run | jq -r '.hookSpecificOutput.additionalContext // ""' 2>/dev/null; }
sw_rows() { jq -s 'length' "$SREG" 2>/dev/null || echo -1; }   # -1 ⇒ a line is unparseable

NOW_TS=$(sw_ts 0)
OLD_TS=$(sw_ts $((8 * 86400)))   # 8 days → past the 7-day prune horizon

# ── S1) AC1: two stale unreconciled keys → clause names the count and the oldest ──
sw_reset
: > "$SW/t-a.jsonl"; touch -t 202001010000 "$SW/t-a.jsonl"   # oldest
: > "$SW/t-b.jsonl"; touch -t 202006010000 "$SW/t-b.jsonl"
{ sw_row "$NOW_TS" start ag-a "$SW/t-a.jsonl"; sw_row "$NOW_TS" start ag-b "$SW/t-b.jsonl"; } > "$SREG"
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qE "(^|[^0-9])2 unreconciled subagent\\(s\\)" \
  && ok "S1 two stale unreconciled keys → clause with count" || bad "S1 clause: $OUT"
printf '%s' "$OUT" | grep -qF "oldest: ag-a" \
  && ok "S1 clause names the oldest key" || bad "S1 oldest: $OUT"
printf '%s' "$OUT" | grep -qF "[hygiene]" \
  && ok "S1 clause composed into the existing [hygiene] message" || bad "S1 not composed: $OUT"

# ── S2) AC2: fully reconciled → clause absent; nothing else flagged → hook silent ──
#         This case pins the SILENCE CONTRACT itself (empty stdout + exit 0), which is
#         why it stays absence-shaped: any companion row that must be reported would
#         make stdout non-empty and destroy the very contract under test. S2b below
#         carries the separable half — reconciled-exclusion — as a PRESENCE-based claim,
#         so a crashed sweep can no longer masquerade as "correctly reconciled".
sw_reset
: > "$SW/t-c.jsonl"; touch -t 202001010000 "$SW/t-c.jsonl"
{ sw_row "$NOW_TS" start ag-c "$SW/t-c.jsonl"; sw_row "$NOW_TS" stop ag-c "$SW/t-c.jsonl"; } > "$SREG"
OUT=$(sw_run); RC=$?
{ [ -z "$OUT" ] && [ "$RC" -eq 0 ]; } && ok "S2 all reconciled → hook silent, exit 0" || bad "S2 rc=$RC out=$OUT"

# ── S2b) AC2, LIVENESS-ANCHORED (B-180, merge-gate witness lens): S2 alone is vacuous —
#          a sweep that crashes on a registry of purely reconciled activity emits nothing
#          and exits 0, which is byte-identical to "correctly reconciled". The carve-out
#          for S2 is sound only for the silence contract, NOT for the reconciled-exclusion
#          claim, and nothing else in this file witnessed that claim against a companion.
#          Here the SAME invocation carries a reconciled pair AND an unambiguously stale
#          key: the count must be exactly 1 and must name the companion, which proves the
#          sweep ran AND that the reconciled key contributed 0.
sw_reset
: > "$SW/t-c2.jsonl"; touch -t 202001010000 "$SW/t-c2.jsonl"
: > "$SW/t-c2-live.jsonl"; sw_stamp "$SW/t-c2-live.jsonl" 7200   # 2h ⇒ unambiguously stale
{ sw_row "$NOW_TS" start ag-c2 "$SW/t-c2.jsonl"; sw_row "$NOW_TS" stop ag-c2 "$SW/t-c2.jsonl"
  sw_row "$(sw_ts 7200)" start ag-c2-live "$SW/t-c2-live.jsonl"; } > "$SREG"
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qE "(^|[^0-9])1 unreconciled subagent" \
  && ok "S2b reconciled key contributes 0 while a stale sibling is counted" \
  || bad "S2b expected exactly 1 (the stale sibling alone): '$OUT'"
printf '%s' "$OUT" | grep -qF "oldest: ag-c2-live" \
  && ok "S2b the counted key is the stale sibling, not the reconciled pair" \
  || bad "S2b counted the WRONG key: '$OUT'"

# ── S3) AC3: fresh (<30 min) unreconciled → NOT flagged (live fan-outs must not alarm) ──
#         LIVENESS-ANCHORED (B-180): asserting only `[ -z "$OUT" ]` would pass on ANY
#         silence, and loop-gc.sh:114-118 makes a failed sweep emit nothing while still
#         exiting 0. A same-invocation stale companion makes the claim PRESENCE-based:
#         exactly `1` plus `oldest: ag-d-old` proves the sweep ran AND that the fresh
#         key is the one not counted.
sw_reset
: > "$SW/t-d.jsonl"   # freshly created ⇒ mtime = now
: > "$SW/t-d-old.jsonl"; sw_stamp "$SW/t-d-old.jsonl" 7200   # 2h ⇒ unambiguously stale
{ sw_row "$NOW_TS" start ag-d "$SW/t-d.jsonl"
  sw_row "$(sw_ts 7200)" start ag-d-old "$SW/t-d-old.jsonl"; } > "$SREG"
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qE "(^|[^0-9])1 unreconciled subagent" \
  && ok "S3 fresh unreconciled not flagged (live fan-out)" \
  || bad "S3 expected exactly 1 (the 2h key alone): '$OUT'"
printf '%s' "$OUT" | grep -qF "oldest: ag-d-old" \
  && ok "S3 the counted key is the stale one, not the fresh fan-out" \
  || bad "S3 counted the WRONG key: '$OUT'"

# ── S4) AC4: 8-day rows pruned; JSONL stays valid; REGISTRY inode replaced but the
#            LOCK file is never unlinked/recreated/renamed (two holders could otherwise
#            each believe they hold exclusivity on different inodes). ────────────────
sw_reset
: > "$SLOCK"; touch -t 202001010000 "$SLOCK"
LOCK_BEFORE=$(sw_ino "$SLOCK")
: > "$SW/t-e.jsonl"
{ sw_row "$OLD_TS" start ag-old "$SW/t-old.jsonl"
  sw_row "$OLD_TS" stop  ag-old "$SW/t-old.jsonl"
  sw_row "$NOW_TS" start ag-e   "$SW/t-e.jsonl"
  sw_row "$NOW_TS" stop  ag-e   "$SW/t-e.jsonl"; } > "$SREG"
REG_INO_BEFORE=$(sw_ino "$SREG")
sw_run >/dev/null 2>&1
[ "$(sw_rows)" = "2" ] && ok "S4 8-day rows pruned, file remains valid JSONL" || bad "S4 rows=$(sw_rows): $(cat "$SREG")"
jq -e 'select(.agent_id=="ag-old")' "$SREG" >/dev/null 2>&1 && bad "S4 pruned row survived" || ok "S4 the 8-day key is gone"
jq -e 'select(.agent_id=="ag-e")' "$SREG" >/dev/null 2>&1 && ok "S4 in-horizon rows retained" || bad "S4 dropped a fresh row"
[ "$(sw_ino "$SREG")" != "$REG_INO_BEFORE" ] && ok "S4 registry inode replaced (tmp-file + rename)" || bad "S4 registry rewritten in place"
[ "$(sw_ino "$SLOCK")" = "$LOCK_BEFORE" ] && ok "S4 LOCK file untouched across the prune (inode + mtime)" \
  || bad "S4 lock changed: $LOCK_BEFORE → $(sw_ino "$SLOCK")"

# ── S5) AC5: one torn trailing line (SIGKILL mid-write) → sweep completes, other keys
#            still counted, malformed line dropped by the prune rewrite. ────────────
sw_reset
: > "$SW/t-f.jsonl"; touch -t 202001010000 "$SW/t-f.jsonl"
{ sw_row "$NOW_TS" start ag-f "$SW/t-f.jsonl"; printf '{"ts":"%s","event":"star' "$NOW_TS"; } > "$SREG"
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qE "(^|[^0-9])1 unreconciled subagent\\(s\\)" \
  && ok "S5 torn tail line skipped; other keys still counted" || bad "S5 sweep aborted: $OUT"
[ "$(sw_rows)" = "1" ] && ok "S5 malformed line dropped by the prune rewrite" || bad "S5 rows=$(sw_rows): $(cat "$SREG")"

# ── S6) AC6: `stop_blocked` is NONTERMINAL — it never reconciles a start. ──────────
sw_reset
: > "$SW/t-h.jsonl"; touch -t 202001010000 "$SW/t-h.jsonl"
{ sw_row "$NOW_TS" start ag-h "$SW/t-h.jsonl"; sw_row "$NOW_TS" stop_blocked ag-h "$SW/t-h.jsonl"; } > "$SREG"
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qE "(^|[^0-9])1 unreconciled subagent\\(s\\)" \
  && ok "S6 stop_blocked does not reconcile (still flagged)" || bad "S6 stop_blocked wrongly reconciled: $OUT"

# ── S7) AC7: PER-KEY counting — three fan-out siblings sharing one fallback transcript
#            key plus ONE accepted stop → 2 unreconciled, never zeroed to 0. ────────
sw_reset
: > "$SW/t-parent.jsonl"; touch -t 202001010000 "$SW/t-parent.jsonl"
{ sw_row "$NOW_TS" start "" "$SW/t-parent.jsonl"
  sw_row "$NOW_TS" start "" "$SW/t-parent.jsonl"
  sw_row "$NOW_TS" start "" "$SW/t-parent.jsonl"
  sw_row "$NOW_TS" stop  "" "$SW/t-parent.jsonl"; } > "$SREG"
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qE "(^|[^0-9])2 unreconciled subagent\\(s\\)" \
  && ok "S7 per-key counting: 3 starts − 1 stop = 2 (siblings not zeroed)" || bad "S7 count: $OUT"
printf '%s' "$OUT" | grep -qF "oldest: $SW/t-parent.jsonl" \
  && ok "S7 fallback key is the transcript path when agent_id is empty" || bad "S7 key: $OUT"

# ── S7b) A recorded-but-MISSING transcript counts as stale (the agent is certainly not
#         live), and a recorded-but-FRESH one still does not. ──────────────────────
sw_reset
{ sw_row "$NOW_TS" start ag-gone "$SW/never-existed.jsonl"; } > "$SREG"
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qE "(^|[^0-9])1 unreconciled subagent\\(s\\)" \
  && ok "S7b missing transcript file counts as stale" || bad "S7b missing transcript not flagged: $OUT"

# ── S7c) A key with NO recorded transcript at all is a different case from S7b's
#         recorded-but-gone path: there is no liveness proxy to age against, so the
#         sweep stays QUIET rather than alarming on a possibly-live agent. (The
#         contract keys reporting on transcript-file mtime; its stale exception is
#         scoped to "path recorded but file gone".) Pinned so the choice is explicit.
#         LIVENESS-ANCHORED (B-180, codex round 3): a bare `[ -z "$OUT" ]` passes when
#         the sweep branch for an empty-transcript row RAISES, since the hook collapses
#         that to empty stdout and still exits 0 — mutation-reproduced. A same-invocation
#         stale companion makes it PRESENCE-based instead.
sw_reset
: > "$SW/t7c-old.jsonl"; sw_stamp "$SW/t7c-old.jsonl" 7200   # 2h ⇒ unambiguously stale
{ sw_row "$NOW_TS" start ag-notrans ""
  sw_row "$(sw_ts 7200)" start ag-7c-old "$SW/t7c-old.jsonl"; } > "$SREG"
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qE "(^|[^0-9])1 unreconciled subagent" \
  && ok "S7c key with no recorded transcript stays quiet (no liveness proxy)" \
  || bad "S7c expected exactly 1 (the 2h key alone): '$OUT'"
printf '%s' "$OUT" | grep -qF "oldest: ag-7c-old" \
  && ok "S7c the counted key is the stale one, not the transcript-less key" \
  || bad "S7c counted the WRONG key: '$OUT'"

# ── S8) AC8: registry lock held elsewhere → the PRUNE is skipped this tick (registry
#            byte-identical), the sweep clause is still produced (the read needs no
#            lock), and SessionStart is never blocked past the ~2s budget. ─────────
sw_reset
: > "$SW/t-i.jsonl"; touch -t 202001010000 "$SW/t-i.jsonl"
{ sw_row "$OLD_TS" start ag-oldi "$SW/t-i.jsonl"; sw_row "$NOW_TS" start ag-i "$SW/t-i.jsonl"; } > "$SREG"
REG_SHA_BEFORE=$(shasum "$SREG" | awk '{print $1}')
/usr/bin/python3 -c '
import fcntl, sys, time
f = open(sys.argv[1], "a+")
fcntl.flock(f.fileno(), fcntl.LOCK_EX)
sys.stdout.write("held\n"); sys.stdout.flush()
time.sleep(8)
' "$SLOCK" > "$SW/holder.out" 2>/dev/null &
HOLDER=$!
for _ in $(seq 1 200); do [ -s "$SW/holder.out" ] && break; sleep 0.05; done
[ -s "$SW/holder.out" ] && ok "S8 lock holder acquired flock" || bad "S8 holder never acquired lock"
S=$(date +%s); OUT=$(sw_ctx); ELAPSED=$(( $(date +%s) - S ))
kill "$HOLDER" 2>/dev/null; wait "$HOLDER" 2>/dev/null
[ "$ELAPSED" -le 4 ] && ok "S8 hook exits promptly under a held lock (${ELAPSED}s ≤ 4s, holder holds 8s)" \
  || bad "S8 SessionStart blocked ${ELAPSED}s on the lock"
[ "$(shasum "$SREG" | awk '{print $1}')" = "$REG_SHA_BEFORE" ] \
  && ok "S8 prune skipped this tick (registry byte-identical)" || bad "S8 pruned without the lock"
printf '%s' "$OUT" | grep -qE "(^|[^0-9])2 unreconciled subagent\\(s\\)" \
  && ok "S8 sweep clause still produced (the read needs no lock)" || bad "S8 clause lost under a held lock: $OUT"

# ── S9) Lock witness (inherited #1200 gate debt): concurrent APPENDS × the prune's
#       tmp-file + rename must lose NO accepted row. Made deterministic by the lock —
#       a holder forces every party to contend, then releases; whichever order they
#       serialize in, the prune re-reads INSIDE the locked region, so every appended
#       row survives the rename. An UNLOCKED prune reads before the appends land and
#       renames over them. Run three times consecutively.
APPENDER="$SCRIPT_DIR/subagent-validate.sh"
for ROUND in 1 2 3; do
  sw_reset
  # A large registry: 1 pruneable row + 20000 in-horizon rows, so the prune's re-read +
  # rewrite is a real window rather than an instant. Only `stop` events → no sweep clause.
  /usr/bin/python3 - "$SREG" "$OLD_TS" "$NOW_TS" 20000 <<'PY'
import json
import sys

reg, old_ts, now_ts, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])


def row(ts, agent):
    return json.dumps({"ts": ts, "event": "stop", "session": "s", "agent_id": agent,
                       "transcript": "/t", "cwd": "/w"}, separators=(",", ":")) + "\n"


with open(reg, "w", encoding="utf-8") as fh:
    fh.write(row(old_ts, "pruneme"))
    for i in range(n):
        fh.write(row(now_ts, "keep%d" % i))
PY
  : > "$SLOCK"
  /usr/bin/python3 -c '
import fcntl, sys, time
f = open(sys.argv[1], "a+")
fcntl.flock(f.fileno(), fcntl.LOCK_EX)
sys.stdout.write("held\n"); sys.stdout.flush()
time.sleep(0.4)
' "$SLOCK" > "$SW/h9.out" 2>/dev/null &
  H9=$!
  for _ in $(seq 1 200); do [ -s "$SW/h9.out" ] && break; sleep 0.05; done
  for i in 1 2 3 4; do
    printf '%s' "$(jq -nc --arg a "conc$i" '{"hook_event_name":"SubagentStart","agent_id":$a}')" \
      | CLAUDE_PROJECT_DIR="$SPROJ" bash "$APPENDER" >/dev/null 2>&1 &
  done
  sw_run >/dev/null 2>&1 &
  SWEEPER=$!
  wait "$H9" 2>/dev/null; wait "$SWEEPER" 2>/dev/null; wait
  GOT=$(sw_rows)
  [ "$GOT" = "20004" ] && ok "S9 round $ROUND: no row lost across append × prune-rename (20000 kept + 4 appended)" \
    || bad "S9 round $ROUND: rows=$GOT want 20004"
  MISSING=""
  for i in 1 2 3 4; do
    jq -e --arg a "conc$i" 'select(.agent_id==$a)' "$SREG" >/dev/null 2>&1 || MISSING="$MISSING conc$i"
  done
  [ -z "$MISSING" ] && ok "S9 round $ROUND: every concurrently-appended row present" \
    || bad "S9 round $ROUND: lost rows:$MISSING"
  jq -e 'select(.agent_id=="pruneme")' "$SREG" >/dev/null 2>&1 \
    && bad "S9 round $ROUND: prune never ran (false green)" || ok "S9 round $ROUND: the prune did run (8-day row gone)"
done

# ── S10) Absent registry → the whole feature is skipped silently (cheap pre-check). ──
sw_reset
rm -f "$SREG"
OUT=$(sw_run); RC=$?
{ [ -z "$OUT" ] && [ "$RC" -eq 0 ]; } && ok "S10 absent registry → feature skipped, exit 0" || bad "S10 rc=$RC out=$OUT"

# ── S11) Abandoned prune tmp files are cleaned under the lock (codex round-1). A crash
#        between tmp.open() and os.replace() leaves an unignored registry copy; tmp files
#        are only created under the lock, so any tmp visible to a lock holder is
#        abandoned by construction and must be unlinked.
sw_reset
sw_row "$(sw_ts 700000)" start prunee /tmp/gone.jsonl >> "$SREG"   # 8-day row forces a rewrite
printf 'abandoned junk\n' > "$SREG.tmp.99999"
printf 'more junk\n' > "$SREG.tmp.4242"
sw_run >/dev/null 2>&1
{ [ ! -e "$SREG.tmp.99999" ] && [ ! -e "$SREG.tmp.4242" ]; } \
  && ok "S11 abandoned tmp files unlinked under the lock" \
  || bad "S11 tmp residue: $(ls "$SPROJ/.harness" 2>/dev/null | tr '\n' ' ')"
[ "$(sw_rows)" = "0" ] && ok "S11 registry still valid after cleanup+prune" || bad "S11 rows=$(sw_rows)"

# ── S12) Schema-invalid row (non-string agent_id) is tolerated by the sweep and dropped
#        by the prune — it must not crash the whole feature (codex round-2).
sw_reset
printf '{"ts":"%s","event":"start","session":"s1","agent_id":[1],"transcript":"/tmp/x.jsonl","cwd":"/w"}\n' "$(sw_ts 60)" >> "$SREG"
T12="$SW/t12.jsonl"; : > "$T12"; touch -t "$(date -v-2H +%Y%m%d%H%M 2>/dev/null || date -d '2 hours ago' +%Y%m%d%H%M)" "$T12"
sw_row "$(sw_ts 7200)" start s12agent "$T12" >> "$SREG"
sw_row "$(sw_ts 700000)" start oldkey12 /tmp/gone12.jsonl >> "$SREG"   # forces a rewrite
OUT=$(sw_ctx)
# 2 = s12agent (2h, stale) + oldkey12 (8d, transcript gone → stale); the schema-invalid
# row contributes nothing and, critically, does not crash the sweep to silence.
printf '%s' "$OUT" | grep -qE "(^|[^0-9])2 unreconciled subagent" \
  && ok "S12 sweep survives a schema-invalid row and still counts valid keys" \
  || bad "S12 sweep crashed or miscounted: '$OUT'"
jq -e 'select(.agent_id==[1])' "$SREG" >/dev/null 2>&1 \
  && bad "S12 schema-invalid row survived the prune" || ok "S12 schema-invalid row dropped by the rewrite"

# ── S13) Horizon-straddle balance: an old reconciled pair (start 8d, stop 6d) + a fresh
#        stale start on the SAME fallback key. Row-by-row pruning would drop only the old
#        start, and the surplus stop would mask the fresh unreconciled start; whole-key
#        pruning keeps the balance and the clause reports 1 (codex round-2).
sw_reset
T13="$SW/t13.jsonl"; : > "$T13"; touch -t "$(date -v-2H +%Y%m%d%H%M 2>/dev/null || date -d '2 hours ago' +%Y%m%d%H%M)" "$T13"
sw_row "$(sw_ts 700000)" start '' "$T13" >> "$SREG"    # 8d — outside horizon
sw_row "$(sw_ts 520000)" stop  '' "$T13" >> "$SREG"    # 6d — inside horizon
sw_row "$(sw_ts 7200)"   start '' "$T13" >> "$SREG"    # 2h — stale, unreconciled
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qE "(^|[^0-9])1 unreconciled subagent" \
  && ok "S13 straddling key keeps balance: fresh start reported, not masked" \
  || bad "S13 surplus stop masked the unreconciled start: '$OUT'"
[ "$(sw_rows)" = "3" ] && ok "S13 whole-key rule retained the straddling history" \
  || bad "S13 rows=$(sw_rows) want 3 (row-by-row prune broke the balance)"

# ── S14) TOCTOU (codex round-3): a terminal stop appended AFTER the hook's unlocked
#        pre-read but BEFORE the prune acquires the lock must NOT be reported. The
#        holder pins the hook at lock acquisition; the stop is appended directly into
#        that window; the sweep must use the prune's LOCKED re-read.
sw_reset
T14="$SW/t14.jsonl"; : > "$T14"; touch -t "$(date -v-2H +%Y%m%d%H%M 2>/dev/null || date -d '2 hours ago' +%Y%m%d%H%M)" "$T14"
sw_row "$(sw_ts 7200)" start s14agent "$T14" >> "$SREG"
sw_row "$(sw_ts 700000)" start oldkey14 /tmp/gone14.jsonl >> "$SREG"   # forces the prune arm to engage
: > "$SLOCK"
# Holder releases on a MARKER FILE, not a timer (codex delta-pass): append-before-release
# is thereby STRUCTURAL — the marker is created only after the append lands — so the
# false-red direction (stop landing after the locked re-read) cannot occur on any host,
# however slow. The direct `>>` is deliberate: routing through the real appender here
# would contend with the holder and skip past its own 2s deadline (the appender's lock
# path has its own witness in S9).
/usr/bin/python3 -c '
import fcntl, os, sys, time
f = open(sys.argv[1], "a+")
fcntl.flock(f.fileno(), fcntl.LOCK_EX)
sys.stdout.write("held\n"); sys.stdout.flush()
deadline = time.monotonic() + 10.0
while not os.path.exists(sys.argv[2]) and time.monotonic() < deadline:
    time.sleep(0.02)
' "$SLOCK" "$SW/h14.release" > "$SW/h14.out" 2>/dev/null &
H14=$!
for _ in $(seq 1 200); do [ -s "$SW/h14.out" ] && break; sleep 0.05; done
sw_run > "$SW/s14.out" 2>/dev/null &
S14PID=$!
# 0.9s pre-read margin: the hook's COLD-START latency to its unlocked pre-read is ~0.47s
# (bash + 54KB of lib sourcing + git worktree list + python spawn); a 0.4s sleep raced it
# and left the witness vacuous most runs (gate lens-3, measured; 0.9s = 12/12 exercised).
# Mis-timing here only degrades toward vacuous-pass on a pathologically slow host —
# never a false red, since release is marker-gated below.
sleep 0.9
sw_row "$(sw_ts 1)" stop s14agent "$T14" >> "$SREG"   # the reconciling stop lands in the window
: > "$SW/h14.release"   # ONLY NOW may the holder release → locked re-read sees the stop
wait "$H14" 2>/dev/null; wait "$S14PID" 2>/dev/null
OUT=$(jq -r '.hookSpecificOutput.additionalContext // ""' "$SW/s14.out" 2>/dev/null)
# The count is the sole live discriminator: the clause names only the OLDEST key
# (oldkey14, transcript-missing → age inf), so s14agent's name can never appear and a
# name-grep would be a dead assertion (gate lens-3). Pre-read mutant reports 2.
printf '%s' "$OUT" | grep -qE "(^|[^0-9])1 unreconciled subagent" \
  && ok "S14 locked snapshot used: reconciled agent not counted, real key still reported" \
  || bad "S14 stale pre-read counted the reconciled agent (or lost the real key): '$OUT'"

# ── S16) STALE boundary pin (gate lens-3): 29min unreconciled → quiet; 31min → flagged.
#        Without this pair any STALE in (~2s, 2h) passed the suite.
#
#        HEADROOM, NOT THRESHOLD (B-169). Both pins stay at 29/31 — what changed is how
#        much wall-clock the assertions spend. Two compounding leaks made a 60s budget
#        behave like a ~1s one:
#          (a) `touch -t` truncates to the minute, so the quiet side's real age was
#              uniform in [29m00s, 29m59s] — headroom to the boundary was a SAWTOOTH from
#              60s down to ~0s, decided by the phase the suite reached S16 at. Measured:
#              phase :00 → 59.3s of headroom, phase :59 → 0.70s.
#          (b) both sides shared one registry, so the 31-min assertion RE-AGED the 29-min
#              fixture across an intervening hook run (~0.8s idle, more under load).
#        Reproduced against the real hook: at phase :59 under 12 CPU spinners the 29-min
#        fixture crossed and the suite reported `2 unreconciled subagent(s)` — the exact
#        red seen on main at be081e9d. sw_stamp fixes (a); RE-STAMPING the quiet side
#        immediately before the second assertion fixes (b), so each hook invocation sees
#        a fixture that is exactly 29m old and spends its FULL 60s budget.
#        Both fixtures deliberately stay in ONE registry: the second assertion's value is
#        that it reads exactly `1` while a fresh sibling is also present, which pins the
#        per-key rule (a stale entry must not drag its fresh sibling into the count).
#        Splitting them into two registries would buy the same headroom and quietly drop
#        that witness.
#        Deliberately NOT fixed by moving the quiet side to ~20min either: that buys
#        headroom by un-pinning the constant, leaving any STALE in (20m, 31m) undetected —
#        the non-discriminating-witness failure B-143's close-out already names.
#        LIVENESS-ANCHORED QUIET SIDE (B-180). The quiet-side pin is ABSENCE-based, so
#        on its own it passes for ANY reason the substring is missing -- including a
#        sweep that emitted nothing at all. That is not hypothetical here: loop-gc.sh
#        :114-118 makes the sweep DELIBERATELY failure-invisible ("any python failure
#        yields no clause on stdout ... and this hook still exits 0"), so total silence
#        is an ENGINEERED, reachable state. An envelope/JSON check cannot separate the
#        two either -- S2 pins that a fully reconciled registry legitimately prints
#        NOTHING and exits 0, so empty is a CORRECT output, not a broken one.
#        So prove the sweep can still SPEAK before trusting its silence: with an
#        unambiguously stale 2h companion present the sweep must report exactly `1`,
#        which in ONE assertion establishes (a) the sweep is alive and (b) the 29-min
#        key is NOT being counted. Only then is the absence claim meaningful.
#        The hook is left untouched: its failure-invisibility is deliberate and
#        load-bearing for production (SessionStart must never be blocked by a sweep
#        bug); this is a test-observability fix, not a fail-loud conversion.
#        NO BLIND ABSENCE CHECK (B-180). The quiet side used to be asserted by
#        `grep -q "unreconciled" && bad || ok`, which passes for ANY silence -- and
#        loop-gc.sh:114-118 makes the sweep DELIBERATELY failure-invisible ("any python
#        failure yields no clause on stdout ... and this hook still exits 0"), so total
#        silence is an ENGINEERED, reachable state. An envelope/JSON check cannot fix it
#        either: S2 pins that a fully reconciled registry legitimately prints NOTHING and
#        exits 0, so empty is a CORRECT output.
#        A separate positive-control invocation ALSO fails to fix it (codex round 1): a
#        sweep that goes silent only for the quiet fixture leaves the control green while
#        the absence check still reports ok -- mutation-tested, 75/75 still passed.
#        So BOTH sides are pinned through ONE invocation, with PRESENCE-based assertions
#        only: a count of exactly `1` proves the 31-min key is flagged AND the 29-min key
#        is not counted, and `oldest: s16stale` proves it is the RIGHT key -- without it a
#        simultaneous low+high drift (counting s16fresh, missing s16stale) also reads `1`.
#        Silence now reds both assertions instead of passing one.
#        The hook is deliberately untouched: its failure-invisibility is load-bearing for
#        production (SessionStart must never be blocked by a sweep bug).
sw_reset
T16A="$SW/t16a.jsonl"; : > "$T16A"; sw_stamp "$T16A" 1740   # 29m -- must stay quiet
T16B="$SW/t16b.jsonl"; : > "$T16B"; sw_stamp "$T16B" 1860   # 31m -- must be flagged
sw_row "$(sw_ts 1740)" start s16fresh "$T16A" >> "$SREG"
sw_row "$(sw_ts 1860)" start s16stale "$T16B" >> "$SREG"
sw_stamp "$T16A" 1740; sw_stamp "$T16B" 1860   # exact ages at THIS invocation
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qE "(^|[^0-9])1 unreconciled subagent" \
  && ok "S16 31-min flagged and 29-min not counted (exactly 1)" \
  || bad "S16 boundary drifted (expected exactly 1): '$OUT'"
printf '%s' "$OUT" | grep -qF "oldest: s16stale" \
  && ok "S16 the counted key is the 31-min one, not the 29-min one" \
  || bad "S16 counted the WRONG key (low+high drift reads 1 too): '$OUT'"

# ── S17) KEEP near-side pin (gate lens-3): a 6-day whole-key history survives the prune.
#        Without this, KEEP could drift down to ~2h undetected (far side pinned by S4).
sw_reset
sw_row "$(sw_ts 518400)" start s17mid /tmp/gone17.jsonl >> "$SREG"   # 6d — inside horizon
sw_row "$(sw_ts 518300)" stop  s17mid /tmp/gone17.jsonl >> "$SREG"
sw_row "$(sw_ts 700000)" start s17old /tmp/gone17b.jsonl >> "$SREG"  # 8d — forces rewrite
sw_run >/dev/null 2>&1
jq -e 'select(.agent_id=="s17mid")' "$SREG" >/dev/null 2>&1 \
  && ok "S17 6-day key survives the prune (KEEP near side pinned)" \
  || bad "S17 6-day key pruned early: $(cat "$SREG")"
jq -e 'select(.agent_id=="s17old")' "$SREG" >/dev/null 2>&1 \
  && bad "S17 8-day key survived (prune did not run)" || ok "S17 8-day key pruned (far side intact)"

# ── S15) Surplus-stop credit (codex round-4): a stop whose own start append was skipped
#        (appender lock deadline) must not bank credit against a LATER sibling's start
#        on the same fallback key. Chronological fold floors at zero; the plain
#        aggregate would compute 1−1=0 and mask the dead sibling.
sw_reset
T15="$SW/t15.jsonl"; : > "$T15"; touch -t "$(date -v-2H +%Y%m%d%H%M 2>/dev/null || date -d '2 hours ago' +%Y%m%d%H%M)" "$T15"
sw_row "$(sw_ts 10800)" stop  '' "$T15" >> "$SREG"   # surplus stop (its start was skipped)
sw_row "$(sw_ts 7200)"  start '' "$T15" >> "$SREG"   # later sibling; died; stale >30min
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qE "(^|[^0-9])1 unreconciled subagent" \
  && ok "S15 surplus stop does not mask the later start" \
  || bad "S15 masked by banked stop credit: '$OUT'"

# ── U-CTX-07 companion: SessionStart reaper for the capture-failure lock ──────
# capture-failure.sh NEVER reclaims in-band (unwinnable herd races, codex rounds
# 3/4/6 on the U-CTX-07 arc); THIS single-threaded venue reaps instead.
export CLAUDE_PROJECT_DIR="$BASE/main"
mkdir -p "$BASE/main/.harness"
CFL="$BASE/main/.harness/session-issues.jsonl.lock"

# aged lock (>60s) → reaped (identity-bound: observe→mv→verify→delete)
mkdir "$CFL"; printf 'x' > "$CFL/owner"
touch -t 202001010000 "$CFL" 2>/dev/null || touch -d '2020-01-01' "$CFL" 2>/dev/null
mkdir "${CFL}.stale.12345"   # orphaned takeover remnant, AGED → swept
touch -t 202001010000 "${CFL}.stale.12345" 2>/dev/null || touch -d '2020-01-01' "${CFL}.stale.12345" 2>/dev/null
mkdir "${CFL}.reap.99999"    # a CONCURRENT reaper's FRESH in-flight dir → must survive
bash "$SCRIPT_DIR/loop-gc.sh" >/dev/null 2>&1
[ ! -d "$CFL" ] && ok "CF-reaper: aged capture-failure lock reaped at SessionStart" || bad "CF-reaper: aged lock survived"
[ ! -d "${CFL}.stale.12345" ] && ok "CF-reaper: AGED orphaned remnant swept" || bad "CF-reaper: aged remnant survived"
[ -d "${CFL}.reap.99999" ] && ok "CF-reaper: fresh concurrent .reap.* dir survives (aged-only sweep)" || bad "CF-reaper: fresh reap dir destroyed"
rm -rf "${CFL}.reap.99999"

# fresh lock (live holder) → left alone
mkdir "$CFL"; printf 'y' > "$CFL/owner"
bash "$SCRIPT_DIR/loop-gc.sh" >/dev/null 2>&1
[ -d "$CFL" ] && [ "$(cat "$CFL/owner")" = "y" ] && ok "CF-reaper: fresh lock left untouched" || bad "CF-reaper: fresh lock reaped/mutated"
rm -rf "$CFL"

# AGED lock whose owner PID is ALIVE (codex round-10: laptop sleep / SIGSTOP /
# slow holder) → NOT reaped; age alone is not abandonment.
mkdir "$CFL"; printf '%s' "$$.1700000000.123" > "$CFL/owner"   # our own live PID
touch -t 202001010000 "$CFL" 2>/dev/null || touch -d '2020-01-01' "$CFL" 2>/dev/null
bash "$SCRIPT_DIR/loop-gc.sh" >/dev/null 2>&1
[ -d "$CFL" ] && ok "CF-reaper: aged lock with LIVE owner PID survives (liveness gate)" || bad "CF-reaper: live-owner lock reaped"
rm -rf "$CFL"

echo
echo "RESULT: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

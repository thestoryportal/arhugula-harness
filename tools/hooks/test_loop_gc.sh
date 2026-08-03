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
printf '%s' "$OUT" | grep -qF "2 unreconciled subagent(s)" \
  && ok "S1 two stale unreconciled keys → clause with count" || bad "S1 clause: $OUT"
printf '%s' "$OUT" | grep -qF "oldest: ag-a" \
  && ok "S1 clause names the oldest key" || bad "S1 oldest: $OUT"
printf '%s' "$OUT" | grep -qF "[hygiene]" \
  && ok "S1 clause composed into the existing [hygiene] message" || bad "S1 not composed: $OUT"

# ── S2) AC2: fully reconciled → clause absent; nothing else flagged → hook silent ──
sw_reset
: > "$SW/t-c.jsonl"; touch -t 202001010000 "$SW/t-c.jsonl"
{ sw_row "$NOW_TS" start ag-c "$SW/t-c.jsonl"; sw_row "$NOW_TS" stop ag-c "$SW/t-c.jsonl"; } > "$SREG"
OUT=$(sw_run); RC=$?
{ [ -z "$OUT" ] && [ "$RC" -eq 0 ]; } && ok "S2 all reconciled → hook silent, exit 0" || bad "S2 rc=$RC out=$OUT"

# ── S3) AC3: fresh (<30 min) unreconciled → NOT flagged (live fan-outs must not alarm) ──
sw_reset
: > "$SW/t-d.jsonl"   # freshly created ⇒ mtime = now
{ sw_row "$NOW_TS" start ag-d "$SW/t-d.jsonl"; } > "$SREG"
OUT=$(sw_run)
[ -z "$OUT" ] && ok "S3 fresh unreconciled not flagged (live fan-out)" || bad "S3 alarmed on a live fan-out: $OUT"

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
printf '%s' "$OUT" | grep -qF "1 unreconciled subagent(s)" \
  && ok "S5 torn tail line skipped; other keys still counted" || bad "S5 sweep aborted: $OUT"
[ "$(sw_rows)" = "1" ] && ok "S5 malformed line dropped by the prune rewrite" || bad "S5 rows=$(sw_rows): $(cat "$SREG")"

# ── S6) AC6: `stop_blocked` is NONTERMINAL — it never reconciles a start. ──────────
sw_reset
: > "$SW/t-h.jsonl"; touch -t 202001010000 "$SW/t-h.jsonl"
{ sw_row "$NOW_TS" start ag-h "$SW/t-h.jsonl"; sw_row "$NOW_TS" stop_blocked ag-h "$SW/t-h.jsonl"; } > "$SREG"
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qF "1 unreconciled subagent(s)" \
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
printf '%s' "$OUT" | grep -qF "2 unreconciled subagent(s)" \
  && ok "S7 per-key counting: 3 starts − 1 stop = 2 (siblings not zeroed)" || bad "S7 count: $OUT"
printf '%s' "$OUT" | grep -qF "oldest: $SW/t-parent.jsonl" \
  && ok "S7 fallback key is the transcript path when agent_id is empty" || bad "S7 key: $OUT"

# ── S7b) A recorded-but-MISSING transcript counts as stale (the agent is certainly not
#         live), and a recorded-but-FRESH one still does not. ──────────────────────
sw_reset
{ sw_row "$NOW_TS" start ag-gone "$SW/never-existed.jsonl"; } > "$SREG"
OUT=$(sw_ctx)
printf '%s' "$OUT" | grep -qF "1 unreconciled subagent(s)" \
  && ok "S7b missing transcript file counts as stale" || bad "S7b missing transcript not flagged: $OUT"

# ── S7c) A key with NO recorded transcript at all is a different case from S7b's
#         recorded-but-gone path: there is no liveness proxy to age against, so the
#         sweep stays QUIET rather than alarming on a possibly-live agent. (The
#         contract keys reporting on transcript-file mtime; its stale exception is
#         scoped to "path recorded but file gone".) Pinned so the choice is explicit.
sw_reset
{ sw_row "$NOW_TS" start ag-notrans ""; } > "$SREG"
OUT=$(sw_run)
[ -z "$OUT" ] && ok "S7c key with no recorded transcript stays quiet (no liveness proxy)" \
  || bad "S7c alarmed without a transcript: $OUT"

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
printf '%s' "$OUT" | grep -qF "2 unreconciled subagent(s)" \
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
printf '%s' "$OUT" | grep -q "2 unreconciled subagent" \
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
printf '%s' "$OUT" | grep -q "1 unreconciled subagent" \
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
/usr/bin/python3 -c '
import fcntl, sys, time
f = open(sys.argv[1], "a+")
fcntl.flock(f.fileno(), fcntl.LOCK_EX)
sys.stdout.write("held\n"); sys.stdout.flush()
time.sleep(1.2)
' "$SLOCK" > "$SW/h14.out" 2>/dev/null &
H14=$!
for _ in $(seq 1 200); do [ -s "$SW/h14.out" ] && break; sleep 0.05; done
sw_run > "$SW/s14.out" 2>/dev/null &
S14PID=$!
sleep 0.4   # hook's unlocked pre-read has happened; it is now blocked on the lock
sw_row "$(sw_ts 1)" stop s14agent "$T14" >> "$SREG"   # the reconciling stop lands in the window
wait "$H14" 2>/dev/null; wait "$S14PID" 2>/dev/null
OUT=$(jq -r '.hookSpecificOutput.additionalContext // ""' "$SW/s14.out" 2>/dev/null)
printf '%s' "$OUT" | grep -q "s14agent" \
  && bad "S14 stale pre-read reported an already-reconciled agent: '$OUT'" \
  || ok "S14 sweep used the locked snapshot: reconciled agent not reported"
printf '%s' "$OUT" | grep -q "1 unreconciled subagent" \
  && ok "S14 the genuinely-unreconciled old key is still reported" \
  || bad "S14 lost the real unreconciled key: '$OUT'"

echo
echo "RESULT: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

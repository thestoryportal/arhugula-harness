#!/usr/bin/env bash
# Hermetic smoke test for session-start.sh (the SessionStart roadmap audit).
# Builds a throwaway repo + fixture dashboard and drives the real hook with
# CLAUDE_PROJECT_DIR pointed at it, asserting each emit branch (hash=ok /
# lag-expected / drift). No network: `gh pr list` returns empty in a repo with no
# GitHub remote, so PRS="" and the hash is computed deterministically.
# Exits non-zero on any failed assertion.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/session-start.sh"
. "$SCRIPT_DIR/../hooks/lib.sh"   # for hook_state_hash to compute the expected value

REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
git -C "$REPO" init -q -b main; git -C "$REPO" config user.email t@t.t; git -C "$REPO" config user.name t
mkdir -p "$REPO/.harness"
# C-HE-09 §2 (U-HE-29): the loop ledger is a SHARED venue outside every worktree, so it is
# no longer reachable as "$REPO/.harness/loop_status.md". Pin it hermetically for this run.
export HARNESS_LOOP_STATUS_PATH="$REPO/shared-loop_status.md"

: > "$REPO/Project_Roadmap_v1.md"
echo seed > "$REPO/.harness/seed"
git -C "$REPO" add -A; git -C "$REPO" commit -qm "base commit"

HEAD8=$(git -C "$REPO" rev-parse HEAD | head -c 8)
# Fixture state: PRS="" (no remote), FORKS=0 (no fork files), BATCH="" (none).
EXP_HASH=$(hook_state_hash "$HEAD8" "" "0" "")

write_dashboard() { # $1=hash to pin
  cat > "$REPO/.harness/roadmap_status.md" <<EOF
# Roadmap status dashboard
| Field | Value |
|---|---|
| \`workspace_state_hash\` | \`${1}\` |
| \`git_head\` | \`${HEAD8}\` (main) — base commit |

## Next action
**\`R-TEST\`** do the thing.
EOF
}

run() { CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" | jq -r '.hookSpecificOutput.additionalContext' 2>/dev/null; }

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

# 1) hash=ok — dashboard pins the correct hash; last commit is not a refresh.
write_dashboard "$EXP_HASH"
OUT=$(run)
printf '%s' "$OUT" | grep -q "hash=ok" && printf '%s' "$OUT" | grep -q "next=R-TEST" \
  && ok "hash=ok branch ($OUT)" || bad "expected hash=ok next=R-TEST, got: $OUT"

# 2) drift — wrong hash, last commit not a refresh.
write_dashboard "000000000000"
OUT=$(run)
printf '%s' "$OUT" | grep -q "ROADMAP DRIFT" && ok "drift branch ($OUT)" || bad "expected DRIFT, got: $OUT"

# 3) lag-expected — wrong hash, last commit is a GENUINE terminating refresh: the
#    reserved title prefix AND the only changed file is roadmap_status.md (§12.2.1
#    both conditions). write_dashboard rewrites only .harness/roadmap_status.md, so
#    staging just that file makes a roadmap-status-only commit.
write_dashboard "000000000000"
git -C "$REPO" add .harness/roadmap_status.md
git -C "$REPO" commit -qm "ops: roadmap status refresh post-#1 (#2)"
OUT=$(run)
printf '%s' "$OUT" | grep -q "lag-expected" && ok "lag-expected on roadmap-status-only refresh ($OUT)" || bad "expected lag-expected, got: $OUT"

# 3c) lag-expected — the same terminating refresh after GitHub's merge commit.
#     The main tip title is "Merge pull request ...", so SessionStart has to inspect
#     the second parent instead of requiring the merge commit title itself to carry
#     the reserved refresh prefix.
git -C "$REPO" checkout -qb merge-refresh
write_dashboard "222222222222"
git -C "$REPO" add .harness/roadmap_status.md
git -C "$REPO" commit -qm "ops: roadmap status refresh post-#7 (#8)"
git -C "$REPO" checkout -q main
git -C "$REPO" merge --no-ff -q merge-refresh -m "Merge pull request #8 from test/merge-refresh"
OUT=$(run)
printf '%s' "$OUT" | grep -q "lag-expected" && ok "lag-expected on merged refresh PR ($OUT)" || bad "expected lag-expected on merged refresh PR, got: $OUT"

# 4) DRIFT despite refresh title — last commit carries the reserved prefix but ALSO
#    changes a non-roadmap-status file, so it is NOT a terminating refresh under
#    §12.2.1. Title-only matching would mis-pass this as lag-expected (the false
#    negative).
write_dashboard "000000000000"
echo more > "$REPO/.harness/seed"
git -C "$REPO" add .harness/roadmap_status.md .harness/seed
git -C "$REPO" commit -qm "ops: roadmap status refresh post-#3 (#4)"
OUT=$(run)
printf '%s' "$OUT" | grep -q "ROADMAP DRIFT" && ok "mis-titled substantive commit halts as DRIFT ($OUT)" || bad "expected DRIFT (title-only false negative), got: $OUT"

# 5) Pending-HIL surfacing — when the loop ledger carries post-ACTIVATE DEFERRED-HIL
#    rows, EVERY emit branch appends the operator-facing summary (so the last unattended
#    run's deferrals are "clearly presented when the operator engages next"). Absent when
#    there is no ledger. Branch-agnostic: the suffix rides whatever audit verdict fires.
cat > "$HARNESS_LOOP_STATUS_PATH" <<'EOF'
| ts | kind | detail |
|---|---|---|
| t1 | ACTIVATE | run |
| t2 | DEFERRED-HIL | R-410 — needs container runtime |
EOF
OUT=$(run)
printf '%s' "$OUT" | grep -q "await your input" && printf '%s' "$OUT" | grep -q "R-410" \
  && ok "pending-HIL summary appended to SessionStart ($OUT)" || bad "no pending-HIL suffix: $OUT"

# 5b) C-HE-09 §5 (U-HE-29, codex r1 P3): a recent NOTIFY row surfaces as its OWN segment
#     BESIDE the HIL summary — never merged into it, and never counted as an item awaiting
#     input. Without this the production `loop_notify_summary` wiring in session-start.sh
#     could be deleted outright and this suite would stay green.
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf '| %s | NOTIFY | lane=L7;cause=g:f:c | B-2 reservation aged past its TTL |\n' "$NOW" \
  >> "$HARNESS_LOOP_STATUS_PATH"
OUT=$(run)
printf '%s' "$OUT" | grep -q "notify:" && printf '%s' "$OUT" | grep -q "B-2 reservation aged" \
  && ok "NOTIFY segment surfaces at SessionStart" || bad "no NOTIFY segment: $OUT"
printf '%s' "$OUT" | grep -q '\[L7\]' && ok "NOTIFY carries its emitting lane" || bad "NOTIFY lane not rendered: $OUT"
printf '%s' "$OUT" | grep -q "1 item(s) await your input" \
  && ok "NOTIFY is rendered BESIDE, not merged into, the HIL count" || bad "NOTIFY changed the HIL count: $OUT"

# 5c) A NOTIFY row with NO pending HIL row still surfaces (the segments are independent).
cat > "$HARNESS_LOOP_STATUS_PATH" <<EOF
| ts | kind | lane;cause | detail |
|---|---|---|---|
| $NOW | NOTIFY | lane=L7;cause=g:f:c | B-3 standalone notice |
EOF
OUT=$(run)
printf '%s' "$OUT" | grep -q "B-3 standalone notice" && ok "NOTIFY surfaces with no pending HIL rows" || bad "NOTIFY suppressed without HIL rows: $OUT"
printf '%s' "$OUT" | grep -q "await your input" && bad "a NOTIFY was counted as awaiting input: $OUT" || ok "NOTIFY never reports as awaiting input"

rm -f "$HARNESS_LOOP_STATUS_PATH"
OUT=$(run)
printf '%s' "$OUT" | grep -q "await your input" && bad "pending-HIL suffix present with no ledger: $OUT" || ok "no pending-HIL suffix when no ledger"
printf '%s' "$OUT" | grep -q "notify:" && bad "NOTIFY segment present with no ledger: $OUT" || ok "no NOTIFY segment when no ledger"

# 5d) C-HE-09 §2 cutover (U-HE-29, codex r3 P2): the migration must be reachable from a
#     PRODUCTION path, not just its own unit test. A legacy per-worktree ledger holding an
#     open gate must be drained into the shared venue by simply starting a session, and the
#     sentinel must stop it from running again.
rm -f "$HARNESS_LOOP_STATUS_PATH"
mkdir -p "$REPO/.harness"
cat > "$REPO/.harness/loop_status.md" <<'EOF'
| ts | kind | detail |
|---|---|---|
| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-124 — open in the pre-U-HE-29 venue |
EOF
OUT=$(run)
printf '%s' "$OUT" | grep -q "B-124" && ok "SessionStart drains the legacy venue (migration is reachable)" || bad "legacy gate not migrated: $OUT"
[ -f "$REPO/.harness/loop_status.md" ] && bad "legacy ledger still collecting writes" || ok "legacy ledger retired by the session-start cutover"
# 5e) The cutover is NOT one-shot (codex r4 P2): a legacy ledger that reappears — a checkout
#     still running pre-U-HE-29 code recreating it, or a worktree added later — must still be
#     drained. A sentinel-guarded cutover would strand it forever.
cat > "$REPO/.harness/loop_status.md" <<'EOF'
| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-500 — a legacy ledger that reappeared after the drain |
EOF
OUT=$(run)
printf '%s' "$OUT" | grep -q "B-500" && ok "a reappearing legacy ledger is drained on a later session" || bad "cutover is one-shot; the reappeared gate is stranded: $OUT"
# ... and a pass with nothing left to import neither re-imports nor loses anything.
OUT=$(run)
[ "$(printf '%s' "$OUT" | grep -c 'B-500')" = "1" ] && ok "an idempotent pass does not duplicate the imported row" || bad "row duplicated by a second pass: $OUT"
rm -f "$REPO/.harness/loop_status.md" "$REPO/.harness"/loop_status.md.migrated-*
rm -f "$HARNESS_LOOP_STATUS_PATH"

# 6) Reservation reconcile-log surfacing (U-HE-18, gate r1 witness P2): the log-READER
#    block is UNGATED by the U-HE-29 activation gate, so its behavior needs witnesses now.
#    The fixture repo has no tools/reservations.py, so the spawn gate stays cold -- only
#    the reader runs. Restore the clean-hash dashboard so the audit branch is stable.
git -C "$REPO" checkout -q main 2>/dev/null || true
HEAD8=$(git -C "$REPO" rev-parse HEAD | head -c 8)
EXP_HASH=$(hook_state_hash "$HEAD8" "" "0" "")
write_dashboard "$EXP_HASH"
QDIR="$(mktemp -d)"; trap 'rm -rf "$REPO" "$QDIR"' EXIT
run_q() { ARC_METRICS_QUEUE_DIR="$QDIR" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" | jq -r '.hookSpecificOutput.additionalContext' 2>/dev/null; }

# 6a) rc=2 log -> resv=ERR surfaced on every audit branch.
mkdir -p "$QDIR/reservations"
printf '%s\n' '{"rc": 2, "result": {"pr-1": "ERROR: boom"}, "ts": "t"}' > "$QDIR/reservations/.reconcile.log"
OUT=$(run_q)
printf '%s' "$OUT" | grep -q "resv=ERR" && ok "rc=2 log surfaces resv=ERR ($OUT)" || bad "expected resv=ERR for rc=2 log, got: $OUT"

# 6b) rc=0 log -> NO resv token.
printf '%s\n' '{"rc": 0, "result": {}, "ts": "t"}' > "$QDIR/reservations/.reconcile.log"
OUT=$(run_q)
printf '%s' "$OUT" | grep -q "resv=" && bad "resv token present for clean rc=0 log: $OUT" || ok "clean rc=0 log stays silent"

# 6c) corrupt log (not JSON / missing rc) -> resv=ERR (fail closed, never fail open).
printf '%s\n' 'not json at all' > "$QDIR/reservations/.reconcile.log"
OUT=$(run_q)
printf '%s' "$OUT" | grep -q "resv=ERR" && ok "corrupt log fails closed to resv=ERR ($OUT)" || bad "corrupt log did not surface resv=ERR: $OUT"

# 6d) log path is a DIRECTORY -> structural corruption surfaced.
rm -f "$QDIR/reservations/.reconcile.log"
mkdir "$QDIR/reservations/.reconcile.log"
OUT=$(run_q)
printf '%s' "$OUT" | grep -q "resv=ERR(reconcile log path corrupt" && ok "directory log path surfaced as corrupt ($OUT)" || bad "directory log path not surfaced: $OUT"
rmdir "$QDIR/reservations/.reconcile.log"

# 6e) reservations root is a regular FILE -> store corruption surfaced.
rm -rf "$QDIR/reservations"
: > "$QDIR/reservations"
OUT=$(run_q)
printf '%s' "$OUT" | grep -q "resv=ERR(reservations store corrupt" && ok "file store root surfaced as corrupt ($OUT)" || bad "file store root not surfaced: $OUT"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

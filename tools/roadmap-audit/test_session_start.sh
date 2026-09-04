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
#    Timestamps must be REAL ISO-8601 (the ts column's contract, and what loop_now
#    writes): C-HE-10's coalescer parses them, and a placeholder like `t2` is an
#    unparseable shape no writer can produce. A RECENT row is still inside the
#    coalescing window, so the bounded summary is what surfaces here.
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
cat > "$HARNESS_LOOP_STATUS_PATH" <<EOF
| ts | kind | detail |
|---|---|---|
| $NOW | ACTIVATE | run |
| $NOW | DEFERRED-HIL | R-410 — needs container runtime |
EOF
OUT=$(run)
printf '%s' "$OUT" | grep -q "await your input" && printf '%s' "$OUT" | grep -q "R-410" \
  && ok "pending-HIL summary appended to SessionStart ($OUT)" || bad "no pending-HIL suffix: $OUT"

# 5a) C-HE-10 §2 (U-HE-30) INTEGRATION: once a group's window has closed, the SessionStart
#     path emits the BATCHED cause-grouped prompt instead of the bounded summary, and the
#     two lanes gated on one cause collapse into a single line. Exercising loop_hil_deliver
#     directly (test_loop_lib.sh) cannot catch a mis-wiring here.
cat > "$HARNESS_LOOP_STATUS_PATH" <<'EOF'
| ts | kind | lane;cause | detail |
|---|---|---|---|
| 2020-01-01T00:00:00Z | DEFERRED-HIL | lane=LA;cause=merge-door-lease-acquire:transient-retry:lease_contended | B-81 — waiting |
| 2020-01-01T00:00:30Z | DEFERRED-HIL | lane=LB;cause=merge-door-lease-acquire:transient-retry:lease_contended | B-82 — waiting |
EOF
OUT=$(run)
printf '%s' "$OUT" | grep -q "2 item(s) need you" \
  && ok "past-window group delivers as ONE batched prompt at SessionStart ($OUT)" \
  || bad "no batched delivery: $OUT"
printf '%s' "$OUT" | grep -q "B-81" && printf '%s' "$OUT" | grep -q "B-82" \
  && ok "both lanes' gates ride the one batched prompt" || bad "batch lost a lane: $OUT"
#     The batch renders BESIDE the standing pending summary, never instead of it (codex
#     r2 P1): the COALESCE-DELIVERED row is durable before this process publishes output,
#     so a crash in between would otherwise mark a gate delivered that nobody saw. The
#     always-on summary makes that unreachable -- the item still surfaces as pending.
printf '%s' "$OUT" | grep -q "await your input" \
  && ok "the pending summary renders BESIDE the batch, not instead of it" \
  || bad "the batch suppressed the standing pending register: $OUT"
OUT=$(run)
printf '%s' "$OUT" | grep -q "need you" \
  && bad "the same generation was delivered twice: $OUT" \
  || ok "a second SessionStart does not re-deliver the same generation"
printf '%s' "$OUT" | grep -q "2 item(s) await your input" \
  && ok "an undelivered-again gate still surfaces as pending after its batch" \
  || bad "the gate vanished once its generation was delivered: $OUT"

# Restore the inside-window fixture for the NOTIFY assertions below.
cat > "$HARNESS_LOOP_STATUS_PATH" <<EOF
| ts | kind | detail |
|---|---|---|
| $NOW | ACTIVATE | run |
| $NOW | DEFERRED-HIL | R-410 — needs container runtime |
EOF

# 5b) C-HE-09 §5 (U-HE-29, codex r1 P3): a recent NOTIFY row surfaces as its OWN segment
#     BESIDE the HIL summary — never merged into it, and never counted as an item awaiting
#     input. Without this the production `loop_notify_summary` wiring in session-start.sh
#     could be deleted outright and this suite would stay green.
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
# 5d) B-232 trigger segment (plan Task 8 Step 3): the rolling 30-day lease_held_yield count is
#     evaluated by THIS hook every session — a ledger with no yield rows reads 0/5, six rows
#     inside one window fire the trigger, five do not.
printf '%s' "$OUT" | grep -q "\[b-232\] lease_held_yields_30d_max=0/5" \
  && ok "B-232 segment evaluates to 0/5 on a ledger with no yield rows" || bad "no B-232 segment: $OUT"
printf '%s' "$OUT" | grep -q "TRIGGER FIRED" && bad "B-232 fired on zero rows: $OUT" || ok "B-232 does not fire on zero rows"
_Y="merge-door-lease-acquire:lease_held_yield"
{
  printf '| ts | kind | lane;cause | detail |\n|---|---|---|---|\n'
  for d in 01 02 03 04 05 06; do printf '| 2020-01-%sT00:00:00Z | NOTIFY | lane=L7;cause=%s | holder=u-x backoff=0 |\n' "$d" "$_Y"; done
} > "$HARNESS_LOOP_STATUS_PATH"
OUT=$(run)
printf '%s' "$OUT" | grep -q "\[b-232\] lease_held_yields_30d_max=6/5 TRIGGER FIRED" \
  && ok "B-232 fires at six yield rows in one 30-day window" || bad "B-232 did not fire: $OUT"
{
  printf '| ts | kind | lane;cause | detail |\n|---|---|---|---|\n'
  for d in 01 02 03 04 05; do printf '| 2020-01-%sT00:00:00Z | NOTIFY | lane=L7;cause=%s | holder=u-x backoff=0 |\n' "$d" "$_Y"; done
} > "$HARNESS_LOOP_STATUS_PATH"
OUT=$(run)
printf '%s' "$OUT" | grep -q "\[b-232\] lease_held_yields_30d_max=5/5" && ! printf '%s' "$OUT" | grep -q "TRIGGER FIRED" \
  && ok "B-232 reads 5/5 without firing at the threshold" || bad "B-232 threshold wrong: $OUT"
# 5e) An evaluation FAILURE is printed in the segment's place, never dropped as a silent zero.
printf '| ts | kind | lane;cause | detail |\n|---|---|---|---|\n| yesterday | NOTIFY | lane=L7;cause=%s | h |\n' "$_Y" > "$HARNESS_LOOP_STATUS_PATH"
OUT=$(run)
printf '%s' "$OUT" | grep -q "\[b-232\] trigger evaluation FAILED: lease_yield_trigger: cannot evaluate" \
  && ok "B-232 evaluation failure surfaces in the banner" || bad "B-232 failure swallowed: $OUT"
printf '%s' "$OUT" | grep -q "lease_held_yields_30d_max=0/5" && bad "B-232 failure read as zero: $OUT" || ok "B-232 failure is never a zero"

rm -f "$HARNESS_LOOP_STATUS_PATH"
OUT=$(run)
printf '%s' "$OUT" | grep -q "await your input" && bad "pending-HIL suffix present with no ledger: $OUT" || ok "no pending-HIL suffix when no ledger"
printf '%s' "$OUT" | grep -q "notify:" && bad "NOTIFY segment present with no ledger: $OUT" || ok "no NOTIFY segment when no ledger"
printf '%s' "$OUT" | grep -q "\[b-232\]" && bad "B-232 segment present with no ledger: $OUT" || ok "no B-232 segment when no ledger"

rm -f "$REPO/.harness/loop_status.md"
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

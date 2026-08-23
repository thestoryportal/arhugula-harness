#!/usr/bin/env bash
# Hermetic test for tools/hooks/lane-init.sh (U-HE-31; C-HE-11 §1 lane index, §2 gc.auto,
# §5 RAM-headroom probe). Builds a throwaway repo with two worktrees, a scratch lane
# registry (ARC_METRICS_QUEUE_DIR) and a scratch loop ledger (HARNESS_LOOP_STATUS_PATH),
# then SOURCES the script the way a lane does. Exits non-zero on any failed assertion.
#
# The script is sourced in a SUBSHELL for every case: an exported HARNESS_LANE_INDEX
# leaking from one case into the next would make the allocation assertions vacuous (the
# script honours a preset index and allocates nothing).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INIT="$SCRIPT_DIR/lane-init.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

[ -f "$INIT" ] || { echo "FATAL: missing $INIT"; exit 1; }

ROOT="$(mktemp -d)"
{ [ -n "$ROOT" ] && [ -d "$ROOT" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$ROOT"' EXIT

# Hermetic git identity: CI runners carry no global user.name/user.email, so every commit
# in a fixture repo must supply it inline or the fixture dies CI-only.
git init -q "$ROOT/repo" || { echo "FATAL: git init"; exit 1; }
(
  cd "$ROOT/repo" && : > seed && printf '.harness/\n' > .gitignore && git add seed .gitignore \
    && git -c user.name=t -c user.email=t@example.invalid commit -qm init
) || { echo "FATAL: fixture commit"; exit 1; }
git -C "$ROOT/repo" worktree add -q "$ROOT/wt" -b lane-a  || { echo "FATAL: worktree a"; exit 1; }
git -C "$ROOT/repo" worktree add -q "$ROOT/wt2" -b lane-b || { echo "FATAL: worktree b"; exit 1; }

export ARC_METRICS_QUEUE_DIR="$ROOT/queue"
export HARNESS_LOOP_STATUS_PATH="$ROOT/loop_status.md"
LANES="$ROOT/queue/lanes"

# --- 1. lane id is exported, persisted, and STABLE across sources -------------------
ID1=$(cd "$ROOT/wt" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_ID")
[ -n "$ID1" ] && ok "HARNESS_LANE_ID exported" || bad "no HARNESS_LANE_ID"
( cd "$ROOT/wt" && source "$INIT" >/dev/null 2>&1 && env | grep -q '^HARNESS_LANE_ID=' ) \
  && ok "HARNESS_LANE_ID is exported into the environment" || bad "lane id not exported"
[ -s "$ROOT/wt/.harness/.lane-id" ] && ok "lane id persisted at .harness/.lane-id" \
  || bad "lane id not persisted"
ID2=$(cd "$ROOT/wt" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_ID")
[ "$ID1" = "$ID2" ] && ok "persisted lane id is re-read, never re-minted" \
  || bad "lane id changed across sources: '$ID1' -> '$ID2'"
ID_OTHER=$(cd "$ROOT/wt2" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_ID")
[ -n "$ID_OTHER" ] && [ "$ID_OTHER" != "$ID1" ] && ok "a second worktree mints its own lane id" \
  || bad "second worktree lane id: '$ID_OTHER' vs '$ID1'"

# --- 2. lane index: distinct per worktree, by exclusive create ----------------------
K1=$(cd "$ROOT/wt"  && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_INDEX")
K2=$(cd "$ROOT/wt2" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_INDEX")
{ [ -n "$K1" ] && [ -n "$K2" ] && [ "$K1" != "$K2" ] && [ -f "$LANES/$K1" ] && [ -f "$LANES/$K2" ]; } \
  && ok "distinct lane index per worktree via exclusive create" || bad "index: '$K1' '$K2'"
grep -qF -- "$ROOT/wt" "$LANES/$K1" && ok "registry entry records the claiming worktree path" \
  || bad "registry entry lacks the worktree path: $(cat "$LANES/$K1" 2>/dev/null)"

# --- 3. re-sourcing the SAME worktree reuses its index, never leaks a second one ----
# The teardown release (safe-worktree-remove.sh) deletes the entries whose path is the
# removed worktree; a lane holding two indices would strand whichever the release missed.
K1_AGAIN=$(cd "$ROOT/wt" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_INDEX")
[ "$K1_AGAIN" = "$K1" ] && ok "same worktree reuses its lane index" \
  || bad "index churned for one worktree: '$K1' -> '$K1_AGAIN'"
ENTRIES=$(ls "$LANES" | wc -l | tr -d ' ')
[ "$ENTRIES" = "2" ] && ok "two worktrees hold exactly two registry entries" \
  || bad "registry entry count is $ENTRIES, want 2"

# --- 4. a preset HARNESS_LANE_INDEX is honoured and allocates nothing ---------------
KP=$(cd "$ROOT/wt" && HARNESS_LANE_INDEX=7 bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_INDEX\"")
{ [ "$KP" = "7" ] && [ ! -f "$LANES/7" ]; } && ok "preset index honoured, no registry write" \
  || bad "preset index: '$KP', registry entry present: $([ -f "$LANES/7" ] && echo yes || echo no)"

# --- 5. gc.auto 0: repo-wide, written once, idempotent ------------------------------
( cd "$ROOT/wt" && source "$INIT" >/dev/null 2>&1; cd "$ROOT/wt" && source "$INIT" >/dev/null 2>&1 )
GC_ALL=$(git -C "$ROOT/wt" config --get-all gc.auto | wc -l | tr -d ' ')
{ [ "$(git -C "$ROOT/wt" config --get gc.auto)" = "0" ] && [ "$GC_ALL" = "1" ]; } \
  && ok "gc.auto=0 written once (idempotent)" \
  || bad "gc.auto writes: $(git -C "$ROOT/wt" config --get-all gc.auto | tr '\n' ' ')"
[ "$(git -C "$ROOT/repo" config --get gc.auto)" = "0" ] \
  && ok "gc.auto is repo-wide (visible from the main checkout)" || bad "gc.auto not repo-wide"

# --- 6. RAM probe (C-HE-11 §5): shortfall at k>=2 -> NOTIFY + stack absent -----------
# Both clauses must bite: the machine is below the floor AND less is available than one
# stack needs. Either alone is not a shortfall (case 6b covers the small-but-idle machine).
OUT=$(cd "$ROOT/wt" && HARNESS_LANE_INDEX_FORCE=2 HARNESS_RAM_FLOOR_GB=99999 HARNESS_LANE_STACK_NEED_GB=99999 \
  bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT")
[ "$OUT" = "ABSENT" ] && ok "RAM shortfall at lane>=2 skips the stack" || bad "ram probe said '$OUT'"
grep -q '| NOTIFY | .*ram_floor' "$HARNESS_LOOP_STATUS_PATH" \
  && ok "RAM shortfall emits a NOTIFY row naming the constraint" \
  || bad "no NOTIFY ram_floor row in $HARNESS_LOOP_STATUS_PATH"
NOTIFY_ROW=$(grep '| NOTIFY | .*ram_floor' "$HARNESS_LOOP_STATUS_PATH" | tail -1)
case "$NOTIFY_ROW" in
  *cause=merge-door*|*cause=reservation*) bad "environmental shortfall used a coordination cause: $NOTIFY_ROW" ;;
  *) ok "cause is environmental, never merge-door-/reservation- (C-HE-13 §3)" ;;
esac

# --- 6b. below the floor but genuinely idle: the probe ALLOWS the lane ---------------
# The machine-class floor decides whether to probe; the probe is of AVAILABLE memory. A
# floor-only gate would refuse a lane on a small machine with the whole of it free.
OUT=$(cd "$ROOT/wt" && HARNESS_LANE_INDEX=2 HARNESS_RAM_FLOOR_GB=99999 HARNESS_LANE_STACK_NEED_GB=0 \
  bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT")
[ "$OUT" = "ALLOWED" ] && ok "below the floor but with headroom, the lane is allowed" \
  || bad "idle small machine refused: '$OUT'"

# --- 7. RAM probe never gates lanes 0/1, however low the machine --------------------
for k in 0 1; do
  OUT=$(cd "$ROOT/wt" && HARNESS_LANE_INDEX="$k" HARNESS_RAM_FLOOR_GB=99999 \
    bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT")
  [ "$OUT" = "ALLOWED" ] && ok "lane $k is never gated by the RAM floor" || bad "lane $k said '$OUT'"
done

# --- 8. a lane above the floor is allowed -------------------------------------------
OUT=$(cd "$ROOT/wt" && HARNESS_LANE_INDEX=2 HARNESS_RAM_FLOOR_GB=0 \
  bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT")
[ "$OUT" = "ALLOWED" ] && ok "lane 2 above the floor brings the stack up" || bad "floor 0 said '$OUT'"

# --- 9. exhausted index space fails loud, never silently unset -----------------------
# An unset HARNESS_LANE_INDEX defaults every consumer to lane 0 — i.e. a silent collision
# with the lane-0 project name and ports, exactly what the registry exists to prevent.
EXH="$ROOT/exhausted"
mkdir -p "$EXH/lanes"
i=0; while [ "$i" -lt 350 ]; do printf 'other-lane %s\n' "$ROOT/not-our-worktree-$i" > "$EXH/lanes/$i"; i=$((i + 1)); done
OUT=$(cd "$ROOT/wt2" && ARC_METRICS_QUEUE_DIR="$EXH" \
  bash -c "source '$INIT' >/dev/null 2>&1; echo \"rc=\$? idx=\${HARNESS_LANE_INDEX:-unset}\"")
case "$OUT" in
  "rc=0 "*) bad "exhausted index space reported success: $OUT" ;;
  *"idx=unset") ok "exhausted index space fails loud with no index exported" ;;
  *) bad "exhausted index space: $OUT" ;;
esac

# --- 9b. a zero-byte CLAIM is a corpse the protocol cannot produce — reclaim it -------
# Under `ln` publication a claim is never observable without its owner, so an empty entry is
# a pre-protocol crash or a stray touch. Skipping past it would burn that index forever.
CORPSE="$ROOT/corpse"; mkdir -p "$CORPSE/lanes"; : > "$CORPSE/lanes/0"
KC=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$CORPSE" HARNESS_LANE_INDEX_FORCE=0 \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_INDEX\"")
{ [ "$KC" = "0" ] && [ -s "$CORPSE/lanes/0" ]; } && ok "a zero-byte claim is reclaimed, not skipped" \
  || bad "corpse claim: k=$KC, entry now: [$(cat "$CORPSE/lanes/0" 2>/dev/null)]"

# --- 10. source witness: no coordination cause family anywhere in the script ---------
grep -q 'lane_stack_allowed' "$INIT" && ok "lane_stack_allowed is defined by the script" \
  || bad "lane_stack_allowed missing"
grep -q 'cause=merge-door\|cause=reservation\|merge-door-\|reservation-' "$INIT" \
  && bad "script names a coordination cause family" \
  || ok "script never emits a merge-door-/reservation- cause"

# --- 10b. an EMPTY .lane-id marker never yields an empty lane id ---------------------
# The failure the publication protocol removes: a crash (or a loser observing the file
# between open() and the payload write) leaves a zero-byte marker. `>` under noclobber can
# never replace it, so a naive re-read would export an EMPTY lane id forever.
: > "$ROOT/wt2/.harness/.lane-id"
ID_EMPTY=$(cd "$ROOT/wt2" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_ID")
{ [ -n "$ID_EMPTY" ] && [ -s "$ROOT/wt2/.harness/.lane-id" ]; } \
  && ok "an empty .lane-id corpse is repaired, not carried forever" \
  || bad "empty marker: id='$ID_EMPTY', marker still empty: $([ -s "$ROOT/wt2/.harness/.lane-id" ] && echo no || echo yes)"
ID_REPAIRED=$(cd "$ROOT/wt2" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_ID")
[ "$ID_REPAIRED" = "$ID_EMPTY" ] && ok "the repaired marker is then stable" \
  || bad "repaired marker churned: '$ID_EMPTY' -> '$ID_REPAIRED'"
printf '%s\n' "$ID_OTHER" > "$ROOT/wt2/.harness/.lane-id"

# --- 10c. losing the create race to OUR OWN path adopts that index, never k+1 ---------
# Two shells opening the SAME worktree at once: both scan, both miss, one creates k. The
# loser must adopt k — incrementing would give one lane two indices and two Docker stacks.
RACE="$ROOT/race"; mkdir -p "$RACE/lanes"
printf '%s %s\n' "someone-else" "$(cd "$ROOT/wt" && pwd -P)" > "$RACE/lanes/0"
KR=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$RACE" HARNESS_LANE_INDEX_FORCE=0 \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_INDEX\"")
{ [ "$KR" = "0" ] && [ ! -f "$RACE/lanes/1" ]; } && ok "a lost create race for our own path adopts that index" \
  || bad "lost race allocated a second index: k=$KR, lanes/1 present: $([ -f "$RACE/lanes/1" ] && echo yes || echo no)"

# --- 11. teardown releases the claim, end to end through safe-worktree-remove.sh -----
# The real removal path, not a direct call to the helper: the release only matters if the
# script every teardown actually runs reaches it, and only on the success branch.
git -C "$ROOT/repo" worktree add -q "$ROOT/wt3" -b lane-c || { echo "FATAL: worktree c"; exit 1; }
K3=$(cd "$ROOT/wt3" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_INDEX")
[ -f "$LANES/$K3" ] && ok "third lane claims an index" || bad "third lane did not claim"
CLAUDE_PROJECT_DIR="$ROOT/repo" bash "$SCRIPT_DIR/safe-worktree-remove.sh" "$ROOT/wt3" >/dev/null 2>&1
RM_RC=$?
[ "$RM_RC" -eq 0 ] && ok "safe-worktree-remove.sh removed the lane worktree" \
  || bad "safe-worktree-remove.sh rc=$RM_RC"
[ ! -f "$LANES/$K3" ] && ok "teardown released the lane index" || bad "lane index $K3 leaked after teardown"
{ [ -f "$LANES/$K1" ] && [ -f "$LANES/$K2" ]; } && ok "teardown left the surviving lanes' claims alone" \
  || bad "teardown removed a surviving lane's entry"

# --- 12. the DIRECT hook_safe_worktree_remove call releases too (loop GC's path) -----
# loop_gc_worktrees calls the library function, never the wrapper script. A release wired
# only to the wrapper would let every GC-reaped lane leak its index permanently.
git -C "$ROOT/repo" worktree add -q "$ROOT/wt4" -b lane-d || { echo "FATAL: worktree d"; exit 1; }
K4=$(cd "$ROOT/wt4" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_INDEX")
[ -f "$LANES/$K4" ] && ok "fourth lane claims an index" || bad "fourth lane did not claim"
(
  cd "$ROOT/wt4" || exit 1
  BR=$(git -C "$ROOT/wt4" symbolic-ref --quiet --short HEAD)
  OID=$(git -C "$ROOT/wt4" rev-parse HEAD)
  cd "$ROOT/repo" || exit 1
  source "$SCRIPT_DIR/lib.sh"
  hook_safe_worktree_remove "$ROOT/repo" "$ROOT/wt4" "$BR" "$OID"
) >/dev/null 2>&1
DIRECT_RC=$?
[ "$DIRECT_RC" -eq 0 ] && ok "direct hook_safe_worktree_remove succeeded" || bad "direct removal rc=$DIRECT_RC"
[ ! -f "$LANES/$K4" ] && ok "the direct removal path released the lane index too" \
  || bad "lane index $K4 leaked through the direct (loop GC) removal path"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

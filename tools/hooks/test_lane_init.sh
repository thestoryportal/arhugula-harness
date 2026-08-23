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

# --- 4. a preset HARNESS_LANE_INDEX is honoured AND takes the claim ------------------
# Honouring a free preset without claiming it would let two worktrees preset the same index
# and both proceed onto one Compose project — the exclusive-create contract exists precisely
# to stop that, and a preset is no less a lane than an allocated one.
PRESETQ="$ROOT/preset-q"
KP=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$PRESETQ" HARNESS_LANE_INDEX=7 \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_INDEX\"")
{ [ "$KP" = "7" ] && [ -f "$PRESETQ/lanes/7" ]; } && ok "a free preset index is honoured and claimed" \
  || bad "preset index: '$KP', claim present: $([ -f "$PRESETQ/lanes/7" ] && echo yes || echo no)"
grep -qF -- "$ROOT/wt" "$PRESETQ/lanes/7" && ok "the preset claim records the presetting worktree" \
  || bad "preset claim content: [$(cat "$PRESETQ/lanes/7" 2>/dev/null)]"

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
RAMQ="$ROOT/ram-q"
OUT=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$RAMQ" HARNESS_LANE_INDEX=2 HARNESS_RAM_FLOOR_GB=99999 HARNESS_LANE_STACK_NEED_GB=99999 \
  bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT")
[ "$OUT" = "ABSENT" ] && ok "RAM shortfall at lane>=2 skips the stack" || bad "ram probe said '$OUT'"
SRC_RC=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$RAMQ" HARNESS_LANE_INDEX=2 \
  bash -c "source '$INIT' >/dev/null 2>&1; echo \$?")
[ "$SRC_RC" = "0" ] && ok "that ABSENT came from the probe, not a failed init" \
  || bad "the init itself failed (rc=$SRC_RC) — the ABSENT above proves nothing"
grep -q '| NOTIFY | .*ram_floor' "$HARNESS_LOOP_STATUS_PATH" \
  && ok "RAM shortfall emits a NOTIFY row naming the constraint" \
  || bad "no NOTIFY ram_floor row in $HARNESS_LOOP_STATUS_PATH"
NOTIFY_ROW=$(grep '| NOTIFY | .*ram_floor' "$HARNESS_LOOP_STATUS_PATH" | tail -1)
case "$NOTIFY_ROW" in
  *cause=merge-door*|*cause=reservation*) bad "environmental shortfall used a coordination cause: $NOTIFY_ROW" ;;
  *) ok "cause is environmental, never merge-door-/reservation- (C-HE-13 §3)" ;;
esac

PROBEQ="$ROOT/probe-q"

# --- 6b. below the floor but genuinely idle: the probe ALLOWS the lane ---------------
# The machine-class floor decides whether to probe; the probe is of AVAILABLE memory. A
# floor-only gate would refuse a lane on a small machine with the whole of it free.
OUT=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$ROOT/idle-q" HARNESS_LANE_INDEX=2 HARNESS_RAM_FLOOR_GB=99999 HARNESS_LANE_STACK_NEED_GB=0 \
  bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT")
[ "$OUT" = "ALLOWED" ] && ok "below the floor but with headroom, the lane is allowed" \
  || bad "idle small machine refused: '$OUT'"

# --- 7. RAM probe never gates lanes 0/1, however low the machine --------------------
# A SEPARATE registry per preset: indices 0/1 are claimed by wt/wt2 above, presetting an
# index another worktree owns is refused (case 21 asserts that), and a worktree may hold
# only one claim — so each preset case gets its own registry.
for k in 0 1; do
  OUT=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$PROBEQ-$k" HARNESS_LANE_INDEX="$k" HARNESS_RAM_FLOOR_GB=99999 \
    bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT")
  [ "$OUT" = "ALLOWED" ] && ok "lane $k is never gated by the RAM floor" || bad "lane $k said '$OUT'"
done

# --- 8. a lane above the floor is allowed -------------------------------------------
OUT=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$PROBEQ-above" HARNESS_LANE_INDEX=2 HARNESS_RAM_FLOOR_GB=0 \
  bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT")
[ "$OUT" = "ALLOWED" ] && ok "lane 2 above the floor brings the stack up" || bad "floor 0 said '$OUT'"

# --- 9. exhausted index space fails loud, never silently unset -----------------------
# An unset HARNESS_LANE_INDEX defaults every consumer to lane 0 — i.e. a silent collision
# with the lane-0 project name and ports, exactly what the registry exists to prevent.
EXH="$ROOT/exhausted"
mkdir -p "$EXH/lanes"
# The held paths are real directories so the fixture models 350 lanes that genuinely hold
# their indices, rather than 350 records pointing at nothing.
mkdir -p "$ROOT/held"
i=0; while [ "$i" -lt 350 ]; do mkdir -p "$ROOT/held/$i"; printf 'other-lane %s\n' "$ROOT/held/$i" > "$EXH/lanes/$i"; i=$((i + 1)); done
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
KC=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$CORPSE" \
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
KR=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$RACE" \
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
# The removal path itself is environment-dependent: its open-reference probe needs /proc +
# /usr/bin/python3 or lsof, and a runner with neither aborts at rc 9 BEFORE reaching the
# release. Both outcomes are asserted rather than one being skipped — a removal that did not
# happen must NOT free the index, which is its own real invariant.
case "$RM_RC" in
  0)
    ok "safe-worktree-remove.sh removed the lane worktree"
    [ ! -f "$LANES/$K3" ] && ok "teardown released the lane index" || bad "lane index $K3 leaked after teardown"
    ;;
  9)
    ok "removal unavailable here (rc=9, no open-reference probe) — asserting the negative instead"
    [ -f "$LANES/$K3" ] && ok "a removal that did not happen does not free the index" \
      || bad "index $K3 freed by a FAILED removal"
    rm -f "$LANES/$K3"        # the fixture's own cleanup; the release path is witnessed directly at case 17
    ;;
  *) bad "safe-worktree-remove.sh rc=$RM_RC (neither a completed removal nor the known probe-unavailable rc)" ;;
esac
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
case "$DIRECT_RC" in
  0)
    ok "direct hook_safe_worktree_remove succeeded"
    [ ! -f "$LANES/$K4" ] && ok "the direct removal path released the lane index too" \
      || bad "lane index $K4 leaked through the direct (loop GC) removal path"
    ;;
  9)
    ok "direct removal unavailable here (rc=9, no open-reference probe) — asserting the negative"
    [ -f "$LANES/$K4" ] && ok "a failed direct removal does not free the index" \
      || bad "index $K4 freed by a FAILED direct removal"
    rm -f "$LANES/$K4"
    ;;
  *) bad "direct removal rc=$DIRECT_RC (neither completed nor the known probe-unavailable rc)" ;;
esac
# The release itself — the thing loop GC's direct call must reach — is witnessed
# environment-independently at case 17, which drives hook_release_lane_index directly.
grep -q 'hook_release_lane_index "\$wt"' "$SCRIPT_DIR/lib.sh" \
  && ok "the release is wired inside hook_safe_worktree_remove (every caller, incl. loop GC)" \
  || bad "hook_safe_worktree_remove no longer calls hook_release_lane_index"

# --- 13. a RELATIVE queue dir is refused (it would give every lane its own lanes/0) ---
OUT=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="relative/queue" \
  bash -c "source '$INIT' >/dev/null 2>&1; echo \"rc=\$? idx=\${HARNESS_LANE_INDEX:-unset}\"")
[ "$OUT" = "rc=1 idx=unset" ] && ok "a relative ARC_METRICS_QUEUE_DIR is refused" \
  || bad "relative queue dir accepted: $OUT"

# --- 14. index knobs are range-checked BEFORE becoming a filename --------------------
# `00` and `08` parse as integers but are DIFFERENT registry filenames from `0` and `8`
# while mapping to the same Compose project — two claims, one stack.
for bad_k in 350 999 ../escape abc " " 00 08 007; do
  OUT=$(cd "$ROOT/wt" && HARNESS_LANE_INDEX="$bad_k" \
    bash -c "source '$INIT' >/dev/null 2>&1; echo \"rc=\$? id=\${HARNESS_LANE_ID:-unset}\"")
  # rc AND the identity: validation runs after the id is exported, so a refusal that leaves
  # it set hands this lane's identity to the next worktree the shell enters.
  [ "$OUT" = "rc=1 id=unset" ] && ok "HARNESS_LANE_INDEX='$bad_k' refused, identity cleared" \
    || bad "index '$bad_k': $OUT"
done
[ ! -e "$LANES/../escape" ] && ok "no claim was published outside the registry" || bad "claim escaped QUEUE_DIR/lanes"

# --- 15. a worktree path with a SPACE round-trips through the claim record ------------
# The record is space-delimited, so an unsanitised id (or a naive read) would misparse the
# path: the same worktree would claim extra indices and teardown would match none of them.
git -C "$ROOT/repo" worktree add -q "$ROOT/with space" -b lane-space || { echo "FATAL: spaced worktree"; exit 1; }
KS=$(cd "$ROOT/with space" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_INDEX")
IDS=$(cd "$ROOT/with space" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_ID")
case "$IDS" in *" "*) bad "lane id carries a space: '$IDS'" ;; *) ok "lane id is space-free" ;; esac
KS2=$(cd "$ROOT/with space" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_INDEX")
[ "$KS2" = "$KS" ] && ok "a spaced worktree path reuses its own claim" \
  || bad "spaced path claimed twice: '$KS' then '$KS2'"

# --- 16. an unwritable ledger makes the shortfall SAY so, never claim a phantom NOTIFY -
: > "$ROOT/not-a-dir"   # a REGULAR FILE as the venue's parent: mkdir -p cannot create under it,
                       # so the ledger genuinely cannot be published (a merely-absent
                       # directory does not test this — loop_status_ensure creates it).
ERR=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$ROOT/notify-q" HARNESS_LANE_INDEX=2 HARNESS_RAM_FLOOR_GB=99999 HARNESS_LANE_STACK_NEED_GB=99999 \
  HARNESS_LOOP_STATUS_PATH="$ROOT/not-a-dir/loop_status.md" \
  bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed" 2>&1 >/dev/null)
case "$ERR" in
  *"could NOT be written"*) ok "an unwritable ledger is reported, not silently claimed" ;;
  *) bad "no durable-record warning on a failed NOTIFY write: [$ERR]" ;;
esac

# --- 17. releasing an index brings that lane's Compose stack down FIRST ---------------
# `docker compose up -d` ADOPTS an existing project rather than refusing it, so recycling
# an index whose containers still run would hand the next lane a dead lane's state. A stub
# docker on PATH records the invocation; the real daemon is neither needed nor touched.
STUB="$ROOT/stub-bin"; mkdir -p "$STUB"
cat > "$STUB/docker" <<STUBEOF
#!/usr/bin/env bash
echo "\$@" >> "$ROOT/docker-calls.log"
exit 0
STUBEOF
chmod +x "$STUB/docker"
REL="$ROOT/release-q"; mkdir -p "$REL/lanes"
printf '%s %s\n' "some-lane" "$ROOT/reaped-wt" > "$REL/lanes/5"
(
  PATH="$STUB:$PATH"; export PATH
  CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$REL" \
    bash -c "source '$SCRIPT_DIR/lib.sh'; hook_release_lane_index '$ROOT/reaped-wt'"
) >/dev/null 2>&1
[ ! -f "$REL/lanes/5" ] && ok "the released index is freed" || bad "index 5 not released"
grep -q 'compose -p arhugula-r420-self-hosted-local-lane5 .* down' "$ROOT/docker-calls.log" 2>/dev/null \
  && ok "release took lane 5's Compose project down before recycling the index" \
  || bad "no compose down for the released lane: [$(cat "$ROOT/docker-calls.log" 2>/dev/null | tr '\n' '/')]"
# The NEGATIVE half, and the only thing that distinguishes the two branches: a VERIFIED-CLEAN
# release must leave no fence. Both branches free the claim and both reach docker, so claim
# absence and the call log are identical between them — without this, swapping the arms of the
# rc case would pass, and every cleanly released index would gate the next lane on it.
[ ! -f "$REL/lanes/.orphaned-5" ] && ok "a verified-clean release leaves NO orphan fence" \
  || bad "clean release wrote .orphaned-5 — the next lane on this index would be gated"

# --- 18. corpse repair NEVER proceeds without the exclusive repair lock ---------------
# Atomic replace alone is not mutual exclusion: two repairers minting different ids and
# replacing in sequence each walk away with a different identity for one worktree. A held
# lock must therefore make the repair FAIL LOUD, not fall back to an unlocked repair.
git -C "$ROOT/repo" worktree add -q "$ROOT/wt5" -b lane-e || { echo "FATAL: worktree e"; exit 1; }
mkdir -p "$ROOT/wt5/.harness"; : > "$ROOT/wt5/.harness/.lane-id"
mkdir -p "$ROOT/wt5/.harness/.lane-id.repair"          # a peer repairer holds the lock
OUT=$(cd "$ROOT/wt5" && bash -c "source '$INIT' >/dev/null 2>&1; echo \"rc=\$? id=\${HARNESS_LANE_ID:-unset}\"")
case "$OUT" in
  "rc=1 id=unset") ok "a held repair lock refuses the repair instead of racing it" ;;
  *) bad "locked corpse repair proceeded anyway: $OUT" ;;
esac
rmdir "$ROOT/wt5/.harness/.lane-id.repair"
ID5=$(cd "$ROOT/wt5" && source "$INIT" >/dev/null 2>&1 && printf '%s' "$HARNESS_LANE_ID")
[ -n "$ID5" ] && ok "with the lock free the corpse is repaired normally" || bad "repair did not recover: '$ID5'"

# --- 19. the released lane's VOLUMES go too, and a FAILED cleanup keeps the claim -----
rm -f "$ROOT/docker-calls.log"
printf '%s %s\n' "some-lane" "$ROOT/reaped-wt-b" > "$REL/lanes/6"
(
  PATH="$STUB:$PATH"; export PATH
  CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$REL" \
    bash -c "source '$SCRIPT_DIR/lib.sh'; hook_release_lane_index '$ROOT/reaped-wt-b'"
) >/dev/null 2>&1
grep -q 'down --volumes' "$ROOT/docker-calls.log" 2>/dev/null \
  && ok "teardown removes the lane's named volumes, not just its containers" \
  || bad "compose down ran without --volumes: [$(cat "$ROOT/docker-calls.log" 2>/dev/null | tr '\n' '/')]"
{ [ ! -f "$REL/lanes/6" ] && [ ! -f "$REL/lanes/.orphaned-6" ]; } \
  && ok "the volume-removing clean release frees the index and writes no fence" \
  || bad "clean release left claim=$([ -f "$REL/lanes/6" ] && echo yes || echo no) fence=$([ -f "$REL/lanes/.orphaned-6" ] && echo yes || echo no)"

# a cleanup that FAILS must not free the index — the containers still hold its ports
cat > "$STUB/docker" <<STUBEOF
#!/usr/bin/env bash
[ "\$1" = "info" ] && exit 0
echo "\$@" >> "$ROOT/docker-calls.log"
exit 1
STUBEOF
chmod +x "$STUB/docker"
printf '%s %s\n' "some-lane" "$ROOT/reaped-wt-c" > "$REL/lanes/7"
(
  PATH="$STUB:$PATH"; export PATH
  CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$REL" \
    bash -c "source '$SCRIPT_DIR/lib.sh'; hook_release_lane_index '$ROOT/reaped-wt-c'"
) >/dev/null 2>&1
# A failed cleanup FENCES the index rather than holding the claim: the claim is inheritable
# by a new worktree at the same path (reuse is by path), the marker is not.
[ -f "$REL/lanes/.orphaned-7" ] && ok "a failed cleanup fences the index with an orphan marker" \
  || bad "no orphan marker after a failed cleanup"
[ ! -f "$REL/lanes/7" ] && ok "the fenced index is released for reuse" || bad "index 7 kept despite the fence"

# ...but if the FENCE itself cannot be written, the claim stays — never remove both.
printf '%s %s\n' "some-lane" "$ROOT/reaped-wt-e" > "$REL/lanes/10"
mkdir -p "$REL/lanes/.orphaned-10"        # a directory: the marker file write cannot land
ERR=$(
  PATH="$STUB:$PATH"; export PATH
  CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$REL" \
    bash -c "source '$SCRIPT_DIR/lib.sh'; hook_release_lane_index '$ROOT/reaped-wt-e'" 2>&1 >/dev/null
)
[ -f "$REL/lanes/10" ] && ok "an unwritable fence keeps the claim (never both fences gone)" \
  || bad "index 10 freed with neither claim nor marker"
case "$ERR" in
  *"could not be written"*) ok "the unwritable fence is reported, not swallowed" ;;
  *) bad "no diagnostic for an unwritable fence: [$ERR]" ;;
esac
rmdir "$REL/lanes/.orphaned-10"; rm -f "$REL/lanes/10"

# --- 20. a failed gc.auto write is reported (C-HE-11 §2 must not fail silently) -------
# Outside any git repository `git config` cannot write, which is the deterministic stand-in
# for the unwritable/locked shared config the contract's guard depends on.
ERR=$(cd "$ROOT" && HARNESS_LANE_ID=probe-lane ARC_METRICS_QUEUE_DIR="$ROOT/gcq" \
  bash -c "source '$INIT'" 2>&1 >/dev/null)
case "$ERR" in
  *"could NOT set gc.auto=0"*) ok "a failed gc.auto write is reported" ;;
  *) bad "gc.auto failure was silent: [$ERR]" ;;
esac

# --- 21. an id/index carried across worktrees by one shell is caught, not inherited ----
# `source` in lane A, `cd` to lane B, `source` again: the exports survive the cd. Without
# these checks B would run under A's reservation identity and A's Compose project.
OUT=$(cd "$ROOT/wt2" && HARNESS_LANE_INDEX="$K1" \
  bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?")
[ "$OUT" = "rc=1" ] && ok "a preset index owned by another worktree is refused" \
  || bad "index $K1 (owned by wt) accepted inside wt2: $OUT"
OUT=$(cd "$ROOT/wt2" && HARNESS_LANE_INDEX="$K2" \
  bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?")
[ "$OUT" = "rc=0" ] && ok "a preset index this worktree owns is accepted" \
  || bad "wt2 refused its own index $K2: $OUT"
# a stale exported id loses to the worktree's own persisted marker
ID_STALE=$(cd "$ROOT/wt2" && HARNESS_LANE_ID="$ID1" \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_ID\"")
{ [ "$ID_STALE" != "$ID1" ] && [ -n "$ID_STALE" ]; } \
  && ok "a stale exported lane id loses to the worktree's persisted marker" \
  || bad "wt2 adopted wt's id: '$ID_STALE'"
# an id bound to another worktree's CLAIM never seeds a fresh worktree's marker
git -C "$ROOT/repo" worktree add -q "$ROOT/wt6" -b lane-f || { echo "FATAL: worktree f"; exit 1; }
ID_SEED=$(cd "$ROOT/wt6" && HARNESS_LANE_ID="$ID1" \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_ID\"")
{ [ "$ID_SEED" != "$ID1" ] && [ -n "$ID_SEED" ]; } \
  && ok "an id already bound to another lane's claim is not adopted by a fresh worktree" \
  || bad "wt6 inherited wt's identity: '$ID_SEED'"

# --- 22. an unverifiable cleanup frees the index but records the obligation -----------
# A stopped daemon is NOT proof that nothing survives: its containers and named volumes
# still exist under the project name, and a later `up` adopts them. Keeping the claim
# forever would leak an index on every reap of a machine whose daemon is simply off, so the
# index is freed and the obligation is carried to the point of next use.
cat > "$STUB/docker" <<STUBEOF
#!/usr/bin/env bash
[ "\$1" = "info" ] && exit 1     # daemon unreachable: cleanup cannot be VERIFIED
echo "\$@" >> "$ROOT/docker-calls.log"
exit 0
STUBEOF
chmod +x "$STUB/docker"
printf '%s %s\n' "some-lane" "$ROOT/reaped-wt-d" > "$REL/lanes/8"
(
  PATH="$STUB:$PATH"; export PATH
  CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$REL" \
    bash -c "source '$SCRIPT_DIR/lib.sh'; hook_release_lane_index '$ROOT/reaped-wt-d'"
) >/dev/null 2>&1
[ ! -f "$REL/lanes/8" ] && ok "an unverifiable cleanup still frees the index" || bad "index 8 kept"
[ -f "$REL/lanes/.orphaned-8" ] && ok "the uncleaned stack is recorded as a deferred obligation" \
  || bad "no .orphaned-8 marker written"

# --- 23. the next lane on that index clears the obligation before using the stack -----
rm -f "$ROOT/docker-calls.log"
cat > "$STUB/docker" <<STUBEOF
#!/usr/bin/env bash
echo "\$@" >> "$ROOT/docker-calls.log"
exit 0
STUBEOF
chmod +x "$STUB/docker"
OUT=$(
  PATH="$STUB:$PATH"; export PATH
  cd "$ROOT/wt" && CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$REL" \
    HARNESS_LANE_INDEX=8 HARNESS_RAM_FLOOR_GB=0 \
    bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT"
)
[ "$OUT" = "ALLOWED" ] && ok "a cleared obligation lets the new lane bring its stack up" \
  || bad "lane 8 still refused after cleanup: '$OUT'"
[ ! -f "$REL/lanes/.orphaned-8" ] && ok "the obligation marker is removed once honoured" \
  || bad ".orphaned-8 survived a successful cleanup"

# --- 24. while the obligation stands, the lane's stack stays ABSENT -------------------
# Refused at ANY index, 0 and 1 included: `up` would ADOPT the dead lane's containers
# rather than fail, so this is not a resource question the RAM floor covers.
# Its OWN registry: case 23 left this worktree holding index 8 in $REL, and the one-claim
# rule would refuse index 9 there — the source would fail and this case would read ABSENT
# for the wrong reason.
ORPH2="$ROOT/orphan-q2"; mkdir -p "$ORPH2/lanes"
printf 'stale\n' > "$ORPH2/lanes/.orphaned-9"
cat > "$STUB/docker" <<STUBEOF
#!/usr/bin/env bash
[ "\$1" = "info" ] && exit 1
exit 0
STUBEOF
chmod +x "$STUB/docker"
OUT=$(
  PATH="$STUB:$PATH"; export PATH
  cd "$ROOT/wt" && CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$ORPH2" \
    HARNESS_LANE_INDEX=9 HARNESS_RAM_FLOOR_GB=0 \
    bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT"
)
[ "$OUT" = "ABSENT" ] && ok "an unhonoured obligation keeps the stack absent, even at a low index" \
  || bad "lane 9 started a stack over an uncleaned project: '$OUT'"
# ...and it is a FAULT (3), not the designed RAM skip (1): the recipe exits non-zero on 3,
# so downstream automation cannot read "no stack" as "stack skipped as designed".
RC=$(
  PATH="$STUB:$PATH"; export PATH
  cd "$ROOT/wt" && CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$ORPH2" \
    HARNESS_LANE_INDEX=9 HARNESS_RAM_FLOOR_GB=0 \
    bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed; echo \$?"
)
[ "$RC" = "3" ] && ok "an uncleaned inherited stack reports a fault code, not the RAM skip" \
  || bad "orphan refusal returned '$RC', want 3"
RC=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$ROOT/ramrc-q" HARNESS_LANE_INDEX=2 \
  HARNESS_RAM_FLOOR_GB=99999 HARNESS_LANE_STACK_NEED_GB=99999 \
  bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed; echo \$?")
[ "$RC" = "1" ] && ok "the designed RAM skip keeps its own code" || bad "RAM skip returned '$RC', want 1"

# --- 25. a preset index is refused unless a claim positively NAMES this worktree ------
# Absence-of-objection is not ownership: an empty or malformed claim, or one that could not
# be published at all, would otherwise let two callers run the same unowned project.
BADQ="$ROOT/badclaim-q"; mkdir -p "$BADQ/lanes"
: > "$BADQ/lanes/3"                                  # empty claim: owned by nobody
OUT=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$BADQ" HARNESS_LANE_INDEX=3 \
  bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?")
[ "$OUT" = "rc=1" ] && ok "a preset index with an empty claim is refused" || bad "empty claim accepted: $OUT"
printf 'just-an-id-no-path\n' > "$BADQ/lanes/4"      # malformed: no path field
OUT=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$BADQ" HARNESS_LANE_INDEX=4 \
  bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?")
[ "$OUT" = "rc=1" ] && ok "a preset index with a malformed claim is refused" || bad "malformed claim accepted: $OUT"

# --- 26. one worktree, one claim — a later preset cannot add a second -----------------
# Two shells in one lane holding different indices would run different Compose projects,
# ports and volumes while both believed they were the same lane.
ONEQ="$ROOT/oneclaim-q"
K_FIRST=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$ONEQ" \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_INDEX\"")
[ -n "$K_FIRST" ] && ok "the lane takes its first index" || bad "no first index"
OUT=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$ONEQ" HARNESS_LANE_INDEX=42 \
  bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?")
[ "$OUT" = "rc=1" ] && ok "a second index for the same worktree is refused" \
  || bad "worktree took a second claim: $OUT"
[ ! -f "$ONEQ/lanes/42" ] && ok "the refused preset left no claim behind" || bad "claim 42 was published"
OUT=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$ONEQ" HARNESS_LANE_INDEX="$K_FIRST" \
  bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?")
[ "$OUT" = "rc=0" ] && ok "presetting the index it already holds is accepted" \
  || bad "lane refused its own index: $OUT"

# --- 27. a lane id carrying whitespace cannot corrupt the claim record ----------------
SANQ="$ROOT/sanitize-q"
git -C "$ROOT/repo" worktree add -q "$ROOT/wt7" -b lane-g || { echo "FATAL: worktree g"; exit 1; }
K_SAN=$(cd "$ROOT/wt7" && ARC_METRICS_QUEUE_DIR="$SANQ" HARNESS_LANE_ID="bad id with spaces" \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_INDEX\"")
ID_SAN=$(cd "$ROOT/wt7" && ARC_METRICS_QUEUE_DIR="$SANQ" \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_ID\"")
case "$ID_SAN" in *" "*) bad "an exported id's spaces reached the marker: '$ID_SAN'" ;; *) ok "an exported id is sanitised before it seeds the marker" ;; esac
# A colon is MAPPED rather than deleted: reservations._check_id rejects one outright, so an
# id carrying it would persist and then fail every reservation call this lane makes.
COLONQ="$ROOT/colon-q"
git -C "$ROOT/repo" worktree add -q "$ROOT/wt9" -b lane-i || { echo "FATAL: worktree i"; exit 1; }
ID_COLON=$(cd "$ROOT/wt9" && ARC_METRICS_QUEUE_DIR="$COLONQ" HARNESS_LANE_ID="host:12345-lane" \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_ID\"")
case "$ID_COLON" in
  *:*) bad "a colon survived into the lane id: '$ID_COLON'" ;;
  "") bad "the colon-bearing id produced no lane id at all" ;;
  *) ok "a colon is mapped, not carried into an id every reservation call would reject" ;;
esac
grep -qF -- "$ID_COLON" "$ROOT/wt9/.harness/.lane-id" \
  && ok "and the persisted marker carries that same usable id" \
  || bad "marker disagrees with the exported id: [$(cat "$ROOT/wt9/.harness/.lane-id" 2>/dev/null)]"
# The DOWNSTREAM half, driven for real rather than asserted in a comment: the mapped id must
# be ACCEPTED by the reservation store, and the raw colon-bearing one REFUSED by it. Without
# both halves the mapping is a rule with no stated consequence — and `selectable` would not
# have witnessed it either, since it never validates the id it is given.
RESQ="$ROOT/res-q"
( ARC_METRICS_QUEUE_DIR="$RESQ" uv run python "$SCRIPT_DIR/../reservations.py" reserve \
    --arc-id probe-colon-mapped --lane-id "$ID_COLON" --branch probe --arc-type applying ) >/dev/null 2>&1
[ $? -eq 0 ] && ok "the mapped id is accepted by the reservation store" \
  || bad "the reservation store refused the id lane-init produced: '$ID_COLON'"
( ARC_METRICS_QUEUE_DIR="$RESQ" uv run python "$SCRIPT_DIR/../reservations.py" reserve \
    --arc-id probe-colon-raw --lane-id "host:12345-lane" --branch probe --arc-type applying ) >/dev/null 2>&1
[ $? -ne 0 ] && ok "and a raw colon-bearing id is refused there — which is what the mapping avoids" \
  || bad "the store accepted a colon id, so the mapping guards nothing"
grep -qF -- "$ROOT/wt7" "$SANQ/lanes/$K_SAN" \
  && ok "the claim record still parses back to this worktree" \
  || bad "claim record corrupted: [$(cat "$SANQ/lanes/$K_SAN" 2>/dev/null)]"

# --- 28. a BLANK (newline-only) marker is a corpse too, not a valid identity ----------
# `-s` is a size test and a lone newline passes it: publication then cannot replace the file
# while every read of it yields an empty id, which no claim scan or teardown can ever match.
BLANKQ="$ROOT/blank-q"
git -C "$ROOT/repo" worktree add -q "$ROOT/wt8" -b lane-h || { echo "FATAL: worktree h"; exit 1; }
mkdir -p "$ROOT/wt8/.harness"; printf '\n' > "$ROOT/wt8/.harness/.lane-id"
ID_BLANK=$(cd "$ROOT/wt8" && ARC_METRICS_QUEUE_DIR="$BLANKQ" \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\${HARNESS_LANE_ID:-}\"")
[ -n "$ID_BLANK" ] && ok "a newline-only marker is repaired like any other corpse" \
  || bad "blank marker yielded an empty lane id"
K_BLANK=$(cd "$ROOT/wt8" && ARC_METRICS_QUEUE_DIR="$BLANKQ" \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_INDEX\"")
grep -qF -- "$ROOT/wt8" "$BLANKQ/lanes/$K_BLANK" && ok "its claim is matchable for reuse and teardown" \
  || bad "claim unmatched: [$(cat "$BLANKQ/lanes/$K_BLANK" 2>/dev/null)]"

# --- 29. an inherited claim is adopted only if its FENCE can be written ---------------
FENCEQ="$ROOT/fence-q"; mkdir -p "$FENCEQ/lanes"
printf '%s %s\n' "previous-occupant" "$(cd "$ROOT/wt" && pwd -P)" > "$FENCEQ/lanes/2"
OUT=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$FENCEQ" \
  bash -c "source '$INIT' >/dev/null 2>&1; printf '%s' \"\$HARNESS_LANE_INDEX\"")
{ [ "$OUT" = "2" ] && [ -f "$FENCEQ/lanes/.orphaned-2" ]; } \
  && ok "a claim from a previous occupant of this path is adopted AND fenced" \
  || bad "inherited claim: k='$OUT', fence present: $([ -f "$FENCEQ/lanes/.orphaned-2" ] && echo yes || echo no)"
grep -qF -- "$ROOT/wt" "$FENCEQ/lanes/2" && ok "the adopted claim is rebound to this lane" \
  || bad "claim still names the previous occupant"
# ...and refused outright when the fence cannot land
FENCEQ2="$ROOT/fence-q2"; mkdir -p "$FENCEQ2/lanes"
printf '%s %s\n' "previous-occupant" "$(cd "$ROOT/wt" && pwd -P)" > "$FENCEQ2/lanes/2"
mkdir -p "$FENCEQ2/lanes/.orphaned-2"      # a directory: the fence file cannot be written
OUT=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$FENCEQ2" \
  bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?")
[ "$OUT" = "rc=1" ] && ok "an unfenceable inherited claim is refused, not adopted" \
  || bad "adopted an unfenceable inherited stack: $OUT"

# --- 30. a failed init leaves no identity behind for the next worktree ----------------
# The id is exported before the index is allocated. If allocation then fails, an id left in
# the shell would be inherited by the next worktree that shell enters — and since the failed
# lane holds no claim, nothing binds it elsewhere and both would persist one identity.
EXH2="$ROOT/exhausted2"; mkdir -p "$EXH2/lanes"
mkdir -p "$ROOT/held2"
i=0; while [ "$i" -lt 350 ]; do mkdir -p "$ROOT/held2/$i"; printf 'other %s\n' "$ROOT/held2/$i" > "$EXH2/lanes/$i"; i=$((i + 1)); done
OUT=$(cd "$ROOT/wt5" && ARC_METRICS_QUEUE_DIR="$EXH2" \
  bash -c "source '$INIT' >/dev/null 2>&1; echo \"rc=\$? id=\${HARNESS_LANE_ID:-unset}\"")
case "$OUT" in
  "rc=1 id=unset") ok "a failed allocation leaves no exported identity" ;;
  *) bad "failed init kept its identity exported: $OUT" ;;
esac

# --- 31. a cleaned orphan whose marker cannot be removed keeps the stack absent -------
# Worse than never writing the marker: it survives a SUCCESSFUL cleanup, and the next source
# of lane-init reads it and runs `down --volumes` against the stack started in between.
STICKQ="$ROOT/sticky-q"; mkdir -p "$STICKQ/lanes"
printf 'stale\n' > "$STICKQ/lanes/.orphaned-3"
# The claim is pre-created for THIS worktree: with the directory read-only below, an
# unclaimed index could not be published either, and the refusal would then come from the
# claim rather than the marker — the same ABSENT for a different reason.
STICK_ID=$(cd "$ROOT/wt" && printf '%s' "$(cat "$ROOT/wt/.harness/.lane-id")")
printf '%s %s\n' "$STICK_ID" "$(cd "$ROOT/wt" && pwd -P)" > "$STICKQ/lanes/3"
chmod 500 "$STICKQ/lanes"                      # cleanup can read it; the unlink cannot land
OUT=$(
  PATH="$STUB:$PATH"; export PATH
  cd "$ROOT/wt" && CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$STICKQ" \
    HARNESS_LANE_INDEX=3 HARNESS_RAM_FLOOR_GB=0 \
    bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT"
)
[ "$OUT" = "ABSENT" ] && ok "an unremovable orphan marker keeps the stack absent" \
  || bad "started a stack a later init would tear down: '$OUT'"
STICK_RC=$(
  PATH="$STUB:$PATH"; export PATH
  cd "$ROOT/wt" && CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$STICKQ" \
    HARNESS_LANE_INDEX=3 bash -c "source '$INIT' >/dev/null 2>&1; echo \$?"
)
[ "$STICK_RC" = "0" ] && ok "that ABSENT came from the marker, not a refused init" \
  || bad "the init itself failed (rc=$STICK_RC) — the ABSENT above proves nothing"
chmod 700 "$STICKQ/lanes"

# --- 34. an oversized digit string cannot become a claim filename ---------------------
# `test -ge` exits 2 on an integer too large for the shell, which `if` reads as false.
OUT=$(cd "$ROOT/wt" && HARNESS_LANE_INDEX=999999999999999999999999999999 \
  bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?")
[ "$OUT" = "rc=1" ] && ok "an oversized index is refused, not published" || bad "oversized index accepted: $OUT"
[ ! -e "$LANES/999999999999999999999999999999" ] && ok "no oversized claim filename exists" \
  || bad "an out-of-contract claim filename was published"

# --- 35. gc.auto is written ONCE, counted as WRITES rather than stored values ---------
# The stored-value count cannot see this regress: replacing the guarded write with an
# unconditional one still leaves exactly one value in the config. Only counting invocations
# distinguishes "set once, idempotent" (the §2 word) from "set on every source".
GITSTUB="$ROOT/git-stub"; mkdir -p "$GITSTUB"
cat > "$GITSTUB/git" <<'GITEOF'
#!/usr/bin/env bash
# Records every `config gc.auto 0` WRITE, and answers the guard's read from a state file so
# the second source sees the value the first one set.
if [ "$1" = "config" ] && [ "$2" = "--get" ] && [ "$3" = "gc.auto" ]; then
  [ -f "$GC_STATE" ] && cat "$GC_STATE"
  exit 0
fi
if [ "$1" = "config" ] && [ "$2" = "gc.auto" ] && [ "$3" = "0" ]; then
  echo "write" >> "$GC_WRITES"; echo 0 > "$GC_STATE"; exit 0
fi
exec /usr/bin/git "$@"
GITEOF
chmod +x "$GITSTUB/git"
export GC_STATE="$ROOT/gc-state" GC_WRITES="$ROOT/gc-writes"
rm -f "$GC_STATE" "$GC_WRITES"
GCQ="$ROOT/gc-q"
for _ in 1 2 3; do
  ( PATH="$GITSTUB:$PATH"; export PATH
    cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$GCQ" bash -c "source '$INIT'" ) >/dev/null 2>&1
done
GC_N=$(wc -l < "$GC_WRITES" 2>/dev/null | tr -d ' ')
[ "${GC_N:-0}" = "1" ] && ok "gc.auto is WRITTEN once across three sources (not once per source)" \
  || bad "gc.auto write count across three sources = ${GC_N:-0}, want 1"
unset GC_STATE GC_WRITES

# --- 36. SOURCING alone never runs a teardown (the status recipe must stay read-only) --
# `just r420-self-hosted-stack-status` sources lane-init. If clearing a fence happened at
# source time, that read-only command would delete an orphaned project's containers and
# named volumes before printing anything — and it is an auto-allowed command in loop mode.
rm -f "$ROOT/docker-calls.log"
cat > "$STUB/docker" <<STUBEOF
#!/usr/bin/env bash
echo "\$@" >> "$ROOT/docker-calls.log"
exit 0
STUBEOF
chmod +x "$STUB/docker"
QUIETQ="$ROOT/quiet-q"; mkdir -p "$QUIETQ/lanes"
printf 'stale\n' > "$QUIETQ/lanes/.orphaned-2"
(
  PATH="$STUB:$PATH"; export PATH
  cd "$ROOT/wt" && CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$QUIETQ" \
    HARNESS_LANE_INDEX=2 bash -c "source '$INIT'"
) >/dev/null 2>&1
grep -q 'down' "$ROOT/docker-calls.log" 2>/dev/null \
  && bad "sourcing ran a teardown: [$(cat "$ROOT/docker-calls.log" 2>/dev/null | tr '\n' '/')]" \
  || ok "sourcing alone runs no teardown — the fence is honoured at stack-up, not at source"
[ -f "$QUIETQ/lanes/.orphaned-2" ] && ok "and the fence is still standing for the lane that asks" \
  || bad "the fence was cleared by a mere source"
# ...while the lane that actually asks for a stack DOES honour it.
OUT=$(
  PATH="$STUB:$PATH"; export PATH
  cd "$ROOT/wt" && CLAUDE_PROJECT_DIR="$SCRIPT_DIR/../.." ARC_METRICS_QUEUE_DIR="$QUIETQ" \
    HARNESS_LANE_INDEX=2 HARNESS_RAM_FLOOR_GB=0 \
    bash -c "source '$INIT' >/dev/null 2>&1; lane_stack_allowed && echo ALLOWED || echo ABSENT"
)
{ [ "$OUT" = "ALLOWED" ] && [ ! -f "$QUIETQ/lanes/.orphaned-2" ]; } \
  && ok "lane_stack_allowed clears the fence and admits the lane" \
  || bad "stack-up path did not honour the fence: '$OUT'"

# --- 37. a marker written BEFORE sanitisation is REFUSED, not silently resolved --------
# `mint-lane-id` preserved a space in the worktree basename, so markers predating this unit
# can hold `host-with space-abc`. Neither automatic answer is safe: adopting it corrupts the
# space-delimited claim, and rewriting it changes a DURABLE identity, orphaning any
# reservation recorded under the old id. The lane refuses and names both forms.
MIGQ="$ROOT/migrate-q"
git -C "$ROOT/repo" worktree add -q "$ROOT/wt10" -b lane-j || { echo "FATAL: worktree j"; exit 1; }
mkdir -p "$ROOT/wt10/.harness"
printf 'legacy host-with space-abc\n' > "$ROOT/wt10/.harness/.lane-id"
OUT=$(cd "$ROOT/wt10" && ARC_METRICS_QUEUE_DIR="$MIGQ" \
  bash -c "source '$INIT' >/dev/null 2>&1; echo \"rc=\$? id=\${HARNESS_LANE_ID:-unset}\"")
[ "$OUT" = "rc=1 id=unset" ] && ok "an unsanitisable persisted id is refused, not adopted or rewritten" \
  || bad "legacy marker was resolved automatically: $OUT"
grep -qF -- "host-with space-abc" "$ROOT/wt10/.harness/.lane-id" \
  && ok "and the marker is left untouched, so no reservation is orphaned" \
  || bad "the refusal rewrote the marker anyway: [$(cat "$ROOT/wt10/.harness/.lane-id" 2>/dev/null)]"
ERR=$(cd "$ROOT/wt10" && ARC_METRICS_QUEUE_DIR="$MIGQ" bash -c "source '$INIT'" 2>&1 >/dev/null)
case "$ERR" in
  *"not usable as written"*) ok "the refusal names the file and both forms" ;;
  *) bad "unhelpful refusal message: [$ERR]" ;;
esac
[ ! -d "$MIGQ/lanes" ] || [ -z "$(ls -A "$MIGQ/lanes" 2>/dev/null)" ] \
  && ok "a refused lane claims no index" || bad "the refused lane still took a claim"

# --- 38. a failed source leaves NO lane identity AND no lane index behind --------------
# The index is as dangerous as the id: a shell that carries a stale one into another
# worktree runs that lane on the previous lane's Compose project, ports and volumes.
OUT=$(cd "$ROOT/wt" && HARNESS_LANE_ID=carried-over HARNESS_LANE_INDEX=5 \
  ARC_METRICS_QUEUE_DIR="relative/not/absolute" \
  bash -c "source '$INIT' >/dev/null 2>&1; echo \"rc=\$? id=\${HARNESS_LANE_ID:-unset} k=\${HARNESS_LANE_INDEX:-unset}\"")
[ "$OUT" = "rc=1 id=unset k=unset" ] && ok "a failed source clears both the id and the index" \
  || bad "failed source kept lane state: $OUT"
OUT=$(cd "$ROOT/wt" && HARNESS_LANE_ID=carried-over HARNESS_LANE_INDEX=999 \
  bash -c "source '$INIT' >/dev/null 2>&1; echo \"rc=\$? id=\${HARNESS_LANE_ID:-unset} k=\${HARNESS_LANE_INDEX:-unset}\"")
[ "$OUT" = "rc=1 id=unset k=unset" ] && ok "and so does a refused index, not just a refused registry" \
  || bad "refused index kept lane state: $OUT"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

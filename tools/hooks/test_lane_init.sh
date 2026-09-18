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

# --- 5b. the gc.auto write goes through the C-HE-11 §3 bounded retry (U-HE-32) ------
# Out-of-family review r3 noted the wiring at this call site had no regression witness:
# reverting it to raw git left every suite green. A shim refuses the first `config
# gc.auto` with the CONFIG lock wording -- which carries no `.lock` substring at all,
# so it also pins the classifier branch that shape needs.
git -C "$ROOT/wt" config --unset-all gc.auto 2>/dev/null
GC_SHIM="$ROOT/gcshim"
mkdir -p "$GC_SHIM"
cat > "$GC_SHIM/git" <<'GCSHIM'
#!/usr/bin/env bash
if [ "${1:-} ${2:-}" = "config gc.auto" ] && [ ! -e "$GIT_SHIM_MARK" ]; then
  : > "$GIT_SHIM_MARK"
  echo "error: could not lock config file .git/config: File exists" >&2
  exit 255
fi
exec "$REAL_GIT" "$@"
GCSHIM
chmod +x "$GC_SHIM/git"
GC_TRACE="$ROOT/gc-trace"
: > "$GC_TRACE"
rm -f "$ROOT/gc-mark"
(
  cd "$ROOT/wt" || exit 1
  REAL_GIT="$(command -v git)"
  export REAL_GIT GIT_SHIM_MARK="$ROOT/gc-mark" HOOK_GIT_RETRY_TRACE="$GC_TRACE"
  export PATH="$GC_SHIM:$PATH"
  source "$INIT" >/dev/null 2>&1
)
[ "$(wc -l < "$GC_TRACE" | tr -d ' ')" -ge 1 ] \
  && ok "the gc.auto write is wired to the bounded retry" \
  || bad "gc.auto write did NOT go through hook_git_retry"
[ "$(git -C "$ROOT/wt" config --get gc.auto)" = "0" ] \
  && ok "and a contended gc.auto write still lands" \
  || bad "gc.auto unset after contention: [$(git -C "$ROOT/wt" config --get gc.auto)]"

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
    bash -c "source '$INIT' >/dev/null 2>&1
printf 'rc=%s id=%s leaked=' \"\$?\" \"\${HARNESS_LANE_ID:-unset}\"
set | sed -n 's/^\(_LI_[A-Za-z0-9_]*\)=.*/\1/p' | grep -v '^_LI_ORPHAN_DIR\$' | sort | tr '\n' ','")
  # The namespace is SCANNED, not enumerated. A hand-written list cannot support a claim about
# "the whole `_LI_*` namespace": the four-name version silently omitted `_LI_ID`, which carries
# the lane identity, so dropping its two cleanups leaked that identity into the caller's
# interactive shell ON THE SUCCESS PATH, in both shells, while this suite stayed byte-identical
# and the Python scanner reported zero violations. That is the SECOND time a hand-maintained
# list here under-counted the namespace -- `_LI_ORPHAN_DIR` was the first -- so the list is gone
# rather than extended. `_LI_ORPHAN_DIR` is excluded by name because it IS the exported surface,
# which is the one documented exception. Measured identical in bash and zsh, with controls:
# nothing set -> empty, only _LI_ORPHAN_DIR set -> empty. (merge-gate witness lens, r10.)
# rc, the identity, AND the whole `_LI_*` namespace. Validation runs after the id is
  # exported, so a refusal that leaves it set hands this lane's identity to the next
  # worktree the shell enters; and a refusal that leaves a `_LI_*` local behind writes it
  # into the caller's interactive shell for good. `leaked=` is a sentinel the run must
  # emit -- an empty capture (the source never ran) must not read as a clean refusal.
  [ "$OUT" = "rc=1 id=unset leaked=" ] \
    && ok "HARNESS_LANE_INDEX='$bad_k' refused, identity and _LI_* namespace cleared" \
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

# --- 39. the duplicate-claim withdrawal, all three arms ------------------------------
# This guard decides whether a duplicate claim for one worktree is withdrawn or kept, and it
# cannot be reached by pre-seeding: a claim that already exists for this path is found by the
# opening scan, which takes the reuse branch and never runs the post-verify. The window is
# between that scan and the create — so the fixture opens it deterministically by stubbing
# `mktemp`, which lane-init calls in exactly that gap, to plant a peer's claim before the
# real one is made. Without this the guard is three untested branches: a mutation dropping
# the published check, or the index comparison, passes every other assertion in this file.
GUARDBIN="$ROOT/guard-bin"; mkdir -p "$GUARDBIN"
cat > "$GUARDBIN/mktemp" <<'MKEOF'
#!/usr/bin/env bash
if [ -n "${PLANT_AT:-}" ] && [ ! -f "$PLANT_DIR/lanes/.planted" ]; then
  mkdir -p "$PLANT_DIR/lanes"
  printf '%s %s\n' "peer-source" "$PLANT_PATH" > "$PLANT_DIR/lanes/$PLANT_AT"
  : > "$PLANT_DIR/lanes/.planted"
fi
exec /usr/bin/mktemp "$@"
MKEOF
chmod +x "$GUARDBIN/mktemp"
WTP="$(cd "$ROOT/wt" && pwd -P)"

# (a) we PUBLISHED and hold the HIGHER index -> ours is the one withdrawn.
HIQ="$ROOT/guard-hi-q"; mkdir -p "$HIQ/lanes"
OUT=$(
  PATH="$GUARDBIN:$PATH"; export PATH
  cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$HIQ" HARNESS_LANE_INDEX=5 \
    PLANT_DIR="$HIQ" PLANT_AT=1 PLANT_PATH="$WTP" \
    bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?"
)
[ "$OUT" = "rc=1" ] && ok "a raced duplicate claim refuses the lane" || bad "raced init returned $OUT"
[ ! -f "$HIQ/lanes/5" ] && ok "the higher index we published is withdrawn" || bad "our higher claim survived"
[ -f "$HIQ/lanes/1" ] && ok "and the lower claim stands" || bad "the withdrawal took the lower claim"

# (b) we PUBLISHED but hold the LOWER index -> ours STANDS, so two racing sources cannot both
# withdraw and leave the worktree with zero claims.
LOQ="$ROOT/guard-lo-q"; mkdir -p "$LOQ/lanes"
OUT=$(
  PATH="$GUARDBIN:$PATH"; export PATH
  cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$LOQ" HARNESS_LANE_INDEX=2 \
    PLANT_DIR="$LOQ" PLANT_AT=9 PLANT_PATH="$WTP" \
    bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?"
)
[ "$OUT" = "rc=1" ] && ok "the lower-index source also refuses the lane" || bad "lower-index init returned $OUT"
[ -f "$LOQ/lanes/2" ] && ok "the LOWER index we published is kept — one survivor, not zero" \
  || bad "both sides withdrew; the worktree would be left with no claim at all"
[ -f "$LOQ/lanes/9" ] && ok "and the peer's higher claim is left for the peer to withdraw" \
  || bad "this source deleted the peer's claim"

# (c) we ADOPTED the claim at our index -> never deleted, whatever the ordering. `ln` fails
# once so the loop takes its adopt path onto an occupant that already names this worktree.
cat > "$GUARDBIN/ln" <<'LNEOF'
#!/usr/bin/env bash
if [ -n "${FAIL_LN_ONCE:-}" ] && [ ! -f "$FAIL_LN_ONCE" ]; then
  : > "$FAIL_LN_ONCE"; exit 1
fi
exec /bin/ln "$@"
LNEOF
chmod +x "$GUARDBIN/ln"
cat > "$GUARDBIN/mktemp" <<'MK2EOF'
#!/usr/bin/env bash
if [ -n "${PLANT_DIR:-}" ] && [ ! -f "$PLANT_DIR/lanes/.planted" ]; then
  mkdir -p "$PLANT_DIR/lanes"
  printf '%s %s\n' "peer-source" "$PLANT_PATH" > "$PLANT_DIR/lanes/0"
  printf '%s %s\n' "peer-source" "$PLANT_PATH" > "$PLANT_DIR/lanes/9"
  : > "$PLANT_DIR/lanes/.planted"
fi
exec /usr/bin/mktemp "$@"
MK2EOF
chmod +x "$GUARDBIN/mktemp"
ADQ="$ROOT/guard-adopt-q"; mkdir -p "$ADQ/lanes"
OUT=$(
  PATH="$GUARDBIN:$PATH"; export PATH
  cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$ADQ" \
    PLANT_DIR="$ADQ" PLANT_PATH="$WTP" FAIL_LN_ONCE="$ROOT/ln-failed-once" \
    bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?"
)
[ "$OUT" = "rc=1" ] && ok "an adopted-plus-duplicate state refuses the lane" || bad "adopt arm returned $OUT"
[ -f "$ADQ/lanes/0" ] && ok "a claim we ADOPTED is never deleted, even holding the lower index" \
  || bad "the withdrawal deleted a live peer's claim — the P1 this guard exists to prevent"
[ -f "$ADQ/lanes/9" ] && ok "and the peer's other claim stands" || bad "peer claim 9 removed"

# --- 40. THREE-way: the survivor is the minimum, not the lexicographically first ------
# BOUND: these cases pin convergence when the racers SEE each other's claims. They do not
# pin at-most-one in general, because scan-and-decide cannot enforce it — a source that
# publishes and scans before any peer exists keeps its claim and never re-checks (B-202).
# `lanes/*` sorts lexicographically, so "10" precedes "2". A rule that acts on the first
# duplicate it meets resolves two racers but not three: the source holding 3 would compare
# only against "10", conclude it is the lower, and stand alongside 2 — two survivors for one
# worktree. The fixture plants BOTH peers, so the source under test must find the minimum
# across the whole directory rather than the first match.
THREEQ="$ROOT/guard-three-q"; mkdir -p "$THREEQ/lanes"
cat > "$GUARDBIN/mktemp" <<'MK3EOF'
#!/usr/bin/env bash
if [ -n "${PLANT_DIR:-}" ] && [ ! -f "$PLANT_DIR/lanes/.planted" ]; then
  mkdir -p "$PLANT_DIR/lanes"
  printf '%s %s\n' "peer-a" "$PLANT_PATH" > "$PLANT_DIR/lanes/2"
  printf '%s %s\n' "peer-b" "$PLANT_PATH" > "$PLANT_DIR/lanes/10"
  : > "$PLANT_DIR/lanes/.planted"
fi
exec /usr/bin/mktemp "$@"
MK3EOF
chmod +x "$GUARDBIN/mktemp"
# This source holds 3: lower than the lex-first peer ("10") but HIGHER than the true
# minimum ("2"), so it must withdraw. Acting on the first match would keep it.
OUT=$(
  PATH="$GUARDBIN:$PATH"; export PATH
  cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$THREEQ" HARNESS_LANE_INDEX=3 \
    PLANT_DIR="$THREEQ" PLANT_PATH="$WTP" \
    bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?"
)
[ "$OUT" = "rc=1" ] && ok "the three-way racer refuses the lane" || bad "three-way init returned $OUT"
[ ! -f "$THREEQ/lanes/3" ] \
  && ok "it withdraws against the MINIMUM (2), not the lexicographically first (10)" \
  || bad "claim 3 survived alongside 2 — two claims for one worktree"
{ [ -f "$THREEQ/lanes/2" ] && [ -f "$THREEQ/lanes/10" ]; } \
  && ok "and it touches neither peer's claim" || bad "a peer's claim was removed"
# ...and the true minimum still stands when IT is the source under test.
THREEQ2="$ROOT/guard-three-q2"; mkdir -p "$THREEQ2/lanes"
rm -f "$THREEQ/lanes/.planted"
OUT=$(
  PATH="$GUARDBIN:$PATH"; export PATH
  cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$THREEQ2" HARNESS_LANE_INDEX=1 \
    PLANT_DIR="$THREEQ2" PLANT_PATH="$WTP" \
    bash -c "source '$INIT' >/dev/null 2>&1; echo rc=\$?"
)
[ -f "$THREEQ2/lanes/1" ] && ok "the minimum of three keeps its claim — exactly one survivor" \
  || bad "the minimum withdrew too; the worktree would hold no claim"

# --- the sourced script must load its libraries in EVERY shell a lane may use -------
# Regression (2026-09-17): `_LI_ROOT` was resolved from `${BASH_SOURCE[0]}` alone, which
# only bash sets. Sourced from zsh -- this workspace's interactive venue -- it expanded
# empty, `dirname` gave `.`, the root landed two levels above $HOME, BOTH library loads
# failed, and `source` still returned 0. The caller walked away with a lane holding no
# `hook_git_retry` (so the repo-wide `gc.auto 0` of C-HE-11 §2 was never attempted) and no
# `loop_log_structured` (so the C-HE-11 §5 shortfall NOTIFY could not be emitted). The
# contract asserted here is behavioural: after sourcing, the library functions lane-init
# calls are callable.
# Which shells this runner can verify is a VALUE, resolved once. `SHELLS_UNVERIFIED` is
# reported beside PASS/FAIL so a run that skipped a shell can never be mistaken for one that
# covered it -- absence of coverage and absence of defects must not print the same.
# Both shells are REQUIRED, not opportunistic. The defect this file exists to pin is
# zsh-only, so a runner without zsh would gate green on a reverted fix -- and CI gates on the
# exit status, which a printed NOTE never reaches. Absence is therefore a counted FAILURE,
# and CI installs zsh for the job that runs this suite (codex r9 P2).
SHELLS=""; SHELLS_UNVERIFIED=""
for _s in bash zsh; do
  if command -v "$_s" >/dev/null 2>&1; then SHELLS="$SHELLS $_s"
  else SHELLS_UNVERIFIED="$SHELLS_UNVERIFIED $_s"; fi
done
SHELLS="${SHELLS# }"; SHELLS_UNVERIFIED="${SHELLS_UNVERIFIED# }"
[ -n "$SHELLS" ] || { echo "FATAL: neither bash nor zsh is executable here"; exit 1; }
for _s in $SHELLS_UNVERIFIED; do
  bad "$_s is not installed -- lane-init portability is UNVERIFIED for it, and the defect this suite pins is zsh-only"
done

LIB_FNS="hook_bounded hook_git_retry loop_log_structured loop_status_ensure loop_status_path"
for SH in $SHELLS; do
  PORT=$("$SH" -c "cd '$ROOT/wt' && source '$INIT' >/dev/null 2>&1
printf 'rc=%s ' \$?
for f in $LIB_FNS; do type \"\$f\" >/dev/null 2>&1 || printf 'nofn:%s ' \"\$f\"; done
[ -n \"\${HARNESS_LANE_ID:-}\" ] || printf 'no-id '
[ -n \"\${HARNESS_LANE_INDEX:-}\" ] || printf 'no-index '
[ -f \"$LANES/\${HARNESS_LANE_INDEX:--}\" ] || printf 'no-claim '")
  [ "$PORT" = "rc=0 " ] && ok "$SH: sourcing lane-init loads both libraries AND brings the lane up" \
    || bad "$SH: lane did not come up cleanly: $PORT"
done

# ...and the SAME contract over a FRESHLY EMPTY registry, which the case above structurally
# cannot reach: it runs against $LANES, which earlier cases have already populated. An empty
# lanes/ is the first-lane-on-a-machine state -- and the state after the last claim is released
# -- and under zsh's default NO_NULL_GLOB an unmatched glob is FATAL. Measured before the fix:
# zsh died at the registry scan with rc=126, HARNESS_LANE_ID EXPORTED, no index and no claim,
# i.e. exactly the half-built lane the refusal paths exist to forbid, and not even the
# contractual rc=1; bash on the identical fixture came up clean. The whole suite stayed 156/0
# throughout, which is why this case exists. (merge-gate witness-adequacy lens, r8.)
FRESHWT="$ROOT/freshwt"; mkdir -p "$FRESHWT/tools/hooks"
cp "$INIT" "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh" "$FRESHWT/tools/hooks/" \
  || { echo "FATAL: freshwt populate"; exit 1; }
for SH in $SHELLS; do
  rm -rf "$FRESHWT/.harness" "$ROOT/freshq"; mkdir -p "$ROOT/freshq"
  # stderr is captured SEPARATELY and checked for the GLOB error specifically, not for blanket
  # cleanliness: this fixture is not a git repo, so lane-init correctly reports that it could not
  # set gc.auto, and an "stderr must be empty" assertion would fail on that fixture artifact in
  # BOTH shells (measured). The narrow needle is what pins the second mechanism: the function
  # boundary stops the FATAL failure, but only the `(N)` arm keeps zsh from printing
  # `no matches found` into the lane shell on every first init.
  FRESH=$(cd "$FRESHWT" && env -u HARNESS_LANE_ID -u HARNESS_LANE_INDEX \
    ARC_METRICS_QUEUE_DIR="$ROOT/freshq" "$SH" -c "source tools/hooks/lane-init.sh >/dev/null 2>/tmp/li-fresh-err.$$
printf 'rc=%s idx=%s' \"\$?\" \"\${HARNESS_LANE_INDEX:-unset}\"")
  FRESH="$FRESH globerr=$(grep -qF 'no matches found' "/tmp/li-fresh-err.$$" && echo YES || echo no)"
  rm -f "/tmp/li-fresh-err.$$"
  # claims counted OUTSIDE the subshell: NODIR keeps "registry vanished" distinct from "no claim".
  FRESH="$FRESH claims=$([ -d "$ROOT/freshq/lanes" ] && ls "$ROOT/freshq/lanes" | wc -l | tr -d ' ' || echo NODIR)"
  [ "$FRESH" = "rc=0 idx=0 globerr=no claims=1" ] \
    && ok "$SH: a lane comes up over a FRESHLY EMPTY registry" \
    || bad "$SH: lane did not come up over an empty registry: '$FRESH' (want rc=0 idx=0 globerr=no claims=1)"
done

# zsh names the sourced file in `$0` only while FUNCTION_ARGZERO is set. It is on by
# default, but it is an ordinary option a lane's zsh config may turn off, and then `$0` is
# the bare shell name and any root derived from it resolves against the caller's cwd. The
# non-default state therefore needs its own witness -- the default-state case above passes
# either way and cannot discriminate. (codex r1 P2.)
if printf '%s\n' $SHELLS | grep -qx zsh; then
  # The trailing `ran:` is the sentinel every other case in this file carries: without it an
  # empty capture -- a zsh that died before the loop -- reads identically to "nothing was
  # undefined", so absence of a run and absence of a defect print the same (witness lens r6 P3).
  NOFAZ=$(zsh -c "setopt NO_FUNCTION_ARGZERO; cd / && source '$INIT' >/dev/null 2>&1
for f in $LIB_FNS; do type \"\$f\" >/dev/null 2>&1 || printf '%s ' \"\$f\"; done
printf 'ran:'")
  [ "$NOFAZ" = "ran:" ] && ok "zsh: libraries load under NO_FUNCTION_ARGZERO too" \
    || bad "zsh NO_FUNCTION_ARGZERO: expected 'ran:', got '$NOFAZ'"
fi

# CDPATH is consulted only for an operand that does not begin with / ./ or ../ -- so this
# hazard exists ONLY when the root is reached by a relative spelling, which is exactly how
# the loop skill types it (`source tools/hooks/lane-init.sh`). The absolute `$INIT` used
# elsewhere in this file cannot reach the mechanism, so this case builds its own tree and
# sources it relatively, with a decoy `tools/hooks` on CDPATH for `cd` to prefer.
CDFIX="$ROOT/cdfix"; mkdir -p "$CDFIX/tools/hooks"
cp "$INIT" "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh" "$CDFIX/tools/hooks/" \
  || { echo "FATAL: cdfix populate"; exit 1; }
CDTRAP="$ROOT/cdtrap"; mkdir -p "$CDTRAP/tools/hooks"
# bash ONLY, deliberately. zsh's `cd` resolves a cwd-relative literal before it consults
# CDPATH, so a zsh iteration here passes whether or not `CDPATH=` is present -- it cannot
# redden under any mutation of the guard it claims to pin. A `for SH in bash zsh` shape
# would imply dual-shell coverage while verifying one shell (merge-gate witness lens, r2).
TRAPPED=$(cd "$CDFIX" && CDPATH="$CDTRAP" bash -c "source tools/hooks/lane-init.sh >/dev/null 2>&1; type hook_git_retry >/dev/null 2>&1 && echo yes")
[ "$TRAPPED" = "yes" ] && ok "bash: a hostile CDPATH does not relocate the library root" \
  || bad "bash: CDPATH relocated the root; libraries did not load"

# `$0`/`BASH_SOURCE` carry the spelling the caller used, never a canonical path, so a root
# derived from either is only as cwd-proof as this pins it. Sourcing by absolute path from
# an unrelated cwd must still find the libraries beside the script.
for SH in $SHELLS; do
  ABS=$("$SH" -c "cd / && source '$INIT' >/dev/null 2>&1; type hook_git_retry >/dev/null 2>&1 && echo yes" 2>/dev/null)
  [ "$ABS" = "yes" ] && ok "$SH: absolute-path sourcing resolves the root from an unrelated cwd" \
    || bad "$SH: absolute-path sourcing from / did not load the libraries"
done

# ...and when the libraries genuinely cannot be resolved, sourcing must say so and refuse,
# never hand back a half-built lane at rc=0. A copy with no `tools/hooks` siblings beside
# it is the cheapest way to make the root unresolvable without touching the real tree.
DETACHED="$ROOT/detached-lane-init.sh"
cp "$INIT" "$DETACHED" || { echo "FATAL: cp lane-init"; exit 1; }
# `rc=` prefix is a sentinel: a capture that never ran is empty, which must NOT read the
# same as a correct refusal. Exact-match, not `!= 0` (witness lens r2 P3).
DET_RC=$(cd "$ROOT/wt" && bash -c "source '$DETACHED' >/dev/null 2>&1; echo rc=\$?")
[ "$DET_RC" = "rc=1" ] \
  && ok "an unresolvable library root makes sourcing fail loudly ($DET_RC)" \
  || bad "unresolvable library root did not refuse cleanly: '$DET_RC' (empty = never ran)"
# This file cleans up every `_LI_*` local on every exit path -- it is sourced, so anything
# left defined is written into the caller's interactive shell for good. A newly introduced
# local has to join that discipline or it is a permanent leak (and can clobber a caller's
# own variable of the same name). Asserted on the SUCCESS path, which is the one a lane
# actually takes. (codex r3 P3.)
for SH in $SHELLS; do
  # `ran:` is a sentinel the successful source must emit. Without it an empty capture --
  # a source that never executed at all -- reads exactly like a clean no-leak pass
  # (witness lens r2 P3).
  LEAKED=$("$SH" -c "cd '$ROOT/wt' && source '$INIT' >/dev/null 2>&1
printf 'ran:'
set | sed -n 's/^\(_LI_[A-Za-z0-9_]*\)=.*/\1/p' | grep -v '^_LI_ORPHAN_DIR\$' | sort | tr '\n' ' '")
  [ "$LEAKED" = "ran:" ] && ok "$SH: a successful init leaves no _LI_* local in the caller's shell" \
    || bad "$SH: init leaked or never ran: '$LEAKED'"
done

# ...and the refusal paths must clear it too, not just the success path. The index-exhaustion
# refusal is the reachable one to drive: fill every lane slot < 350 with a FOREIGN worktree's
# claim and this lane can allocate nothing. Before this arc that exit cleared HARNESS_* and
# the `_li_*` locals but left the whole outer `_LI_*` scope defined. (codex r4 P3.)
EXHQ="$ROOT/exhaust-q"; mkdir -p "$EXHQ/lanes"
_i=0; while [ "$_i" -lt 350 ]; do printf 'foreign /not/this/worktree\n' > "$EXHQ/lanes/$_i"; _i=$((_i+1)); done
for SH in $SHELLS; do
  EXH=$(cd "$ROOT/wt" && ARC_METRICS_QUEUE_DIR="$EXHQ" "$SH" -c "source '$INIT' >/dev/null 2>&1
printf 'rc=%s ' \$?
set | sed -n 's/^\(_LI_[A-Za-z0-9_]*\)=.*/\1/p' | grep -v '^_LI_ORPHAN_DIR\$' | sort | tr '\n' ' '")
  case "$EXH" in
    "rc=1 ") ok "$SH: index exhaustion refuses AND clears the whole _LI_* scope" ;;
    rc=1*)   bad "$SH: exhaustion refused but leaked: $EXH" ;;
    *)       bad "$SH: exhaustion did not refuse: $EXH" ;;
  esac
done

# Sourcing is not transactional -- `. lib.sh` puts its functions in the caller for good -- so
# presence of BOTH libraries is established before either is sourced. The case that proves it
# is the asymmetric one: lib.sh present, loop_lib.sh absent. Before the two-phase load the
# caller was left holding lib.sh's functions after being told the lane was not initialised;
# now it holds none of them. (codex r5 P2.)
HALFFIX="$ROOT/halfwt"; mkdir -p "$HALFFIX/tools/hooks"
cp "$INIT" "$SCRIPT_DIR/lib.sh" "$HALFFIX/tools/hooks/" || { echo "FATAL: halfwt populate"; exit 1; }
for SH in $SHELLS; do
  HALF=$(cd "$HALFFIX" && "$SH" -c "source tools/hooks/lane-init.sh >/dev/null 2>&1
printf 'rc=%s ' \$?
type hook_bounded >/dev/null 2>&1 && printf 'hook_bounded-LEAKED'")
  [ "$HALF" = "rc=1 " ] \
    && ok "$SH: a missing SECOND library leaves none of the first's functions in the caller" \
    || bad "$SH: half-initialised after second-library failure: $HALF"
done

# ...and the OTHER arm of the two-phase load. The case above deletes loop_lib.sh, so the
# PRESENCE preflight rejects it and the per-source status check is never reached -- removing
# that check's `|| { _li_fail=...; break; }` would leave the case above green. This one
# supplies a loop_lib.sh that is readable (passing the preflight) and RETURNS NONZERO, which
# only the status check can catch (codex r9 P3).
FAILFIX="$ROOT/failwt"; mkdir -p "$FAILFIX/tools/hooks"
cp "$INIT" "$SCRIPT_DIR/lib.sh" "$FAILFIX/tools/hooks/" || { echo "FATAL: failwt populate"; exit 1; }
printf 'hook_from_failing_lib() { :; }\nreturn 3\n' > "$FAILFIX/tools/hooks/loop_lib.sh"
for SH in $SHELLS; do
  FAILED=$(cd "$FAILFIX" && "$SH" -c "source tools/hooks/lane-init.sh >/dev/null 2>&1
printf 'rc=%s' \$?")
  [ "$FAILED" = "rc=1" ] \
    && ok "$SH: a readable SECOND library that returns nonzero is rejected by the status check" \
    || bad "$SH: nonzero second library was not rejected: $FAILED"
done

# ...and at a DIFFERENT refusal exit than the one above, which is the whole point. The r10
# witness drove only the unresolvable-library-root path -- the one site that then carried the
# fix -- so it was structurally unable to notice that the other exits did not. This case
# refuses via index validation, which returns from far lower in the file, and asserts the same
# contract. Both pass now because the invalidation is hoisted to a single unconditional site
# above every exit rather than repeated at each one (merge-gate concurrency lens, r2).
# The env var is exported on its own line, not as a prefix to `source`: a prefix assignment to
# a special builtin is not portable here and silently yielded an empty capture, which the
# `rc=` sentinel caught rather than passing as a clean result.
FARQ="$ROOT/farq"; mkdir -p "$FARQ/lanes"
for SH in $SHELLS; do
  FAR_EXIT=$("$SH" -c "cd '$ROOT/wt'
export ARC_METRICS_QUEUE_DIR='$FARQ'
source '$INIT' >/dev/null 2>&1
export HARNESS_LANE_INDEX=../escape
source '$INIT' >/dev/null 2>&1
printf 'rc=%s orphan=%s fn=%s' \"\$?\" \"\${_LI_ORPHAN_DIR:+set}\" \"\$(type lane_stack_allowed >/dev/null 2>&1 && echo callable || echo gone)\"")
  [ "$FAR_EXIT" = "rc=1 orphan= fn=gone" ] \
    && ok "$SH: a refusal at a LATER exit also invalidates the prior callable surface" \
    || bad "$SH: later-exit refusal left the prior lane callable: '$FAR_EXIT'"
done

# A refused init must publish NO CLAIM -- asserted behaviourally, at the EXECUTED entry point.
# `return` at the top level of a non-sourced script is an error in bash that does NOT stop
# execution, so the library-load refusal needs the `2>/dev/null || exit 1` tail that every
# other top-level exit in the file carries. Without it the run announces "lane NOT initialised", then walks the whole
# protocol with neither library loaded, persists a lane id, takes an EXCLUSIVE claim in the
# shared registry, and exits 0 -- a slot nothing ever reclaims, since release matches a removed
# worktree path, and no caller notices because the status is 0. The file is mode 755, so the
# executed entry point is reachable even though every call site sources today.
# This pins the CONTRACT (a refusal publishes no claim), not the shape of the exit line, so it
# cannot be evaded by rewriting the exit -- the lexical-scanner trap this arc already paid for.
# Several exits are driven, deliberately, because the tail is hand-repeated per site and CANNOT
# be hoisted: the r5 witness drove only the library-load refusal -- the site the defect was found
# at -- and was therefore structurally unable to notice a bare `return` at any other exit. The
# cases below are the list; no count is restated here, because every count written into this
# block so far has been falsified by the next round that added a case. Measured:
# a bare `return 1` at the non-integer-index refusal made an executed run exit 0 while the whole
# suite stayed byte-identical. That is the same per-site drift this file already records at
# FAR_EXIT. (merge-gate concurrency lens r5; witness-adequacy lens r6 P2.)
#
# The asserted pair is `rc` + `claims`. It deliberately does NOT assert id=absent at the LATE
# exits: the lane id is minted BEFORE index validation, so correct code there already persists an
# identity. Re-using the early exit's triple would assert a falsehood.
EXECFIX="$ROOT/execwt"; mkdir -p "$EXECFIX/tools/hooks" "$ROOT/execq/lanes"
cp "$INIT" "$EXECFIX/tools/hooks/" || { echo "FATAL: execwt populate"; exit 1; }
# lib.sh / loop_lib.sh deliberately NOT copied: that is what forces the library-load refusal.
for SH in $SHELLS; do
  rm -rf "$EXECFIX/.harness" "$ROOT/execq/lanes"; mkdir -p "$ROOT/execq/lanes"
  EXEC_REFUSED=$(cd "$EXECFIX" && ARC_METRICS_QUEUE_DIR="$ROOT/execq" "$SH" tools/hooks/lane-init.sh >/dev/null 2>&1
printf 'rc=%s claims=%s id=%s' "$?" \
  "$([ -d "$ROOT/execq/lanes" ] && ls "$ROOT/execq/lanes" | wc -l | tr -d ' ' || echo NODIR)" \
  "$([ -f "$EXECFIX/.harness/.lane-id" ] && echo persisted || echo absent)")
  [ "$EXEC_REFUSED" = "rc=1 claims=0 id=absent" ] \
    && ok "$SH: an EXECUTED lane-init refusing BEFORE the libraries load publishes no claim" \
    || bad "$SH: executed early-exit refusal leaked state: '$EXEC_REFUSED' (want rc=1 claims=0 id=absent)"
done

# The LATE exits: libraries present, so execution reaches the index validation. The indices below
# drive ../escape ("must be an integer 0..349"), 00 ("must be canonical (no leading zeros)")
# and 400 ("must be < 350") -- named by their refusal text, not by line, because this arc's own
# insertions above them have already invalidated one set of line cites; the
# ARC_METRICS_QUEUE_DIR case that follows drives the relative-path refusal (lane-init.sh:141). NO CLAIM IS
# MADE HERE ABOUT COMPLETENESS. Three successive rounds each wrote a bound over this set and each
# was falsified by execution in the next -- r6 named a fixed pair, r7 replaced that with "every
# refusal reachable with nothing but an environment variable", and r8 falsified THAT with lane-init.sh:141.
# A bound is a second copy of the list below, and second copies drift. The list is the coverage;
# a new externally-reachable refusal is covered when it appears here, and not before.
# The r6 absorption drove only the first index, and a bare `return 1` at either of the other two
# left the
# whole suite
# byte-identical while an executed run exited 0 and walked on toward publishing a claim. There is
# no prose bound here now: this list IS the coverage, so it cannot disagree with itself.
EXECLATE="$ROOT/execlate"; mkdir -p "$EXECLATE/tools/hooks" "$ROOT/execlateq/lanes"
cp "$INIT" "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh" "$EXECLATE/tools/hooks/" \
  || { echo "FATAL: execlate populate"; exit 1; }
for SH in $SHELLS; do
  for BAD_IDX in ../escape 00 400; do
    rm -rf "$EXECLATE/.harness" "$ROOT/execlateq/lanes"; mkdir -p "$ROOT/execlateq/lanes"
    # HARNESS_LANE_ID is cleared explicitly: a lane shell exports it, and with it set zsh dies on
    # the pre-fix unguarded registry glob over the deliberately-empty registry and never REACHES the
    # refusal -- the assertion would then pass for the wrong reason (spec lens, r7 P3).
    EXEC_LATE=$(cd "$EXECLATE" && env -u HARNESS_LANE_ID ARC_METRICS_QUEUE_DIR="$ROOT/execlateq" \
      HARNESS_LANE_INDEX="$BAD_IDX" "$SH" tools/hooks/lane-init.sh >/dev/null 2>&1
printf 'rc=%s claims=%s' "$?" \
  "$([ -d "$ROOT/execlateq/lanes" ] && ls "$ROOT/execlateq/lanes" | wc -l | tr -d ' ' || echo NODIR)")
    [ "$EXEC_LATE" = "rc=1 claims=0" ] \
      && ok "$SH: an EXECUTED lane-init refusing on HARNESS_LANE_INDEX=$BAD_IDX publishes no claim" \
      || bad "$SH: executed refusal on '$BAD_IDX' leaked state: '$EXEC_LATE' (want rc=1 claims=0)"
  done
done

# A queue path containing WHITESPACE or a GLOB METACHARACTER. Every other case in this file
# uses a whitespace-free path, which is why the suite stayed green over a real regression: the
# scan helper briefly emitted FULL PATHS that each call site word-split, so one space in
# ARC_METRICS_QUEUE_DIR made every claim invisible to every scan. The failure was SILENT and
# permissive -- measured, a worktree already holding lanes/0 then sourcing with
# HARNESS_LANE_INDEX=1 got rc=0 and the registry ended holding BOTH 0 and 1 for one worktree,
# where the direct glob it replaced refused. That is the stranding hazard the header at lane-init.sh:17-19
# forbids, and it was quieter than the zsh bug the helper exists to fix.
#
# The path carries a space AND a `*`: word-splitting and pathname expansion are two separate
# triggers on a command substitution, and the helper's contract has to survive both.
# (merge-gate concurrency lens, r9.)
WSQ="$ROOT/q W*S"; WSWT="$ROOT/wswt"; mkdir -p "$WSWT/tools/hooks"
cp "$INIT" "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh" "$WSWT/tools/hooks/" \
  || { echo "FATAL: wswt populate"; exit 1; }
for SH in $SHELLS; do
  rm -rf "$WSWT/.harness" "$WSQ"; mkdir -p "$WSQ/lanes"
  WS=$(cd "$WSWT" && env -u HARNESS_LANE_ID -u HARNESS_LANE_INDEX \
    ARC_METRICS_QUEUE_DIR="$WSQ" "$SH" -c "source tools/hooks/lane-init.sh >/dev/null 2>&1
export HARNESS_LANE_INDEX=1
source tools/hooks/lane-init.sh >/dev/null 2>&1
printf 'rc2=%s' \"\$?\"")
  WS="$WS claims=$([ -d "$WSQ/lanes" ] && ls "$WSQ/lanes" | wc -l | tr -d ' ' || echo NODIR)"
  # rc2=1 AND one claim: the second source must REFUSE to add a second entry for one worktree.
  [ "$WS" = "rc2=1 claims=1" ] \
    && ok "$SH: a queue path with a space and a glob char still refuses a second claim" \
    || bad "$SH: whitespace/glob queue path broke reuse-detection: '$WS' (want rc2=1 claims=1)"
done

# The relative-ARC_METRICS_QUEUE_DIR refusal (lane-init.sh:141). It needs its own case rather than another
# index in the loop above, because it is reached through a DIFFERENT environment variable -- which
# is exactly why the r7 bound missed it: that bound generalised over the loop's variable, not over
# the refusals.
#
# This case asserts the REFUSAL COUNT, not rc, and that is the whole point. Measured: with a bare
# `return 1` at lane-init.sh:141 the executed run still exits 1, because a LATER refusal catches it -- so an
# rc-only assertion passes either way and witnesses nothing. What the defect actually does is walk
# PAST its own refusal, and that is observable: clean code emits exactly one `lane-init:` line,
# the mutant emits two (its own, then `return: can only return from a function or sourced
# script`, then a second refusal). The contract here is that a refusal is TERMINAL; rc is a proxy
# that something downstream can satisfy on the defect's behalf. The r7 witness lens was right to
# decline pressing this site on rc grounds; the refusal count is what makes it witnessable.
# (merge-gate spec-conformance and witness-adequacy lenses, r8.)
EXECREL="$ROOT/execrel"; mkdir -p "$EXECREL/tools/hooks"
cp "$INIT" "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh" "$EXECREL/tools/hooks/" \
  || { echo "FATAL: execrel populate"; exit 1; }
for SH in $SHELLS; do
  rm -rf "$EXECREL/.harness" "$EXECREL/relq"
  EXEC_REL=$(cd "$EXECREL" && env -u HARNESS_LANE_ID -u HARNESS_LANE_INDEX \
    ARC_METRICS_QUEUE_DIR=relq "$SH" tools/hooks/lane-init.sh >/dev/null 2>"/tmp/li-rel-err.$$"
printf 'rc=%s' "$?")
  EXEC_REL="$EXEC_REL refusals=$(grep -c '^lane-init:' "/tmp/li-rel-err.$$")"
  EXEC_REL="$EXEC_REL claims=$([ -d "$EXECREL/relq/lanes" ] && ls "$EXECREL/relq/lanes" | wc -l | tr -d ' ' || echo NODIR)"
  rm -f "/tmp/li-rel-err.$$"
  [ "$EXEC_REL" = "rc=1 refusals=1 claims=NODIR" ] \
    && ok "$SH: an EXECUTED refusal of a relative queue dir is TERMINAL and publishes no claim" \
    || bad "$SH: executed relative-queue refusal was not terminal: '$EXEC_REL' (want rc=1 refusals=1 claims=NODIR)"
done

# A refusal must invalidate the PREVIOUS source's surface, not just this source's variables.
# The refusal cases above mostly enter from a fresh shell and so cannot see state an earlier
# successful source left behind: measured before the fix, `lane_stack_allowed` survived a
# refusal and returned 0 -- "bring the stack up" -- with the index defaulted to 0, i.e. another
# lane's Docker project and ports. (codex r10 P2. Not destructive: `_lane_clear_orphaned_stack`
# re-reads HARNESS_LANE_INDEX and returns early on empty, verified with a planted marker that
# survived -- the hazard is the stale ANSWER, not a stale teardown.)
STALEQ="$ROOT/staleq"; mkdir -p "$STALEQ/lanes"
for SH in $SHELLS; do
  STALE_FN=$("$SH" -c "cd '$ROOT/wt' && ARC_METRICS_QUEUE_DIR='$STALEQ' source '$INIT' >/dev/null 2>&1
source '$DETACHED' >/dev/null 2>&1
printf 'orphan=%s fn=%s' \"\${_LI_ORPHAN_DIR:+set}\" \"\$(type lane_stack_allowed >/dev/null 2>&1 && echo callable || echo gone)\"")
  [ "$STALE_FN" = "orphan= fn=gone" ] \
    && ok "$SH: a refusal invalidates the prior source's callable surface" \
    || bad "$SH: refusal left the prior lane callable: $STALE_FN"
done

# `_LI_ORPHAN_DIR` is the fifth member of this namespace and the one documented exception:
# `lane_stack_allowed` reads it after sourcing returns, so it MUST survive a successful init.
# The leak cases above enumerate four names and therefore cannot see it either way -- which
# is exactly how the header came to claim that all of `_LI_*` is cleared. Pinned in both
# directions here: it must survive success, and it must not be the reason a refusal looks
# clean. (codex r9 P3.)
for SH in $SHELLS; do
  ORPH=$("$SH" -c "cd '$ROOT/wt' && source '$INIT' >/dev/null 2>&1
printf 'rc=%s orphan=%s' \"\$?\" \"\${_LI_ORPHAN_DIR:+set}\"")
  [ "$ORPH" = "rc=0 orphan=set" ] \
    && ok "$SH: _LI_ORPHAN_DIR survives a successful init (lane_stack_allowed reads it)" \
    || bad "$SH: _LI_ORPHAN_DIR disposition wrong: '$ORPH' (lane_stack_allowed would break)"
done

# The namespace contract covers every exit, so pin the REFUSAL path too, with all four
# reserved names pre-set. The success case below enters from a freshly unset shell and so
# cannot see a member the refusal forgets; this one can. (codex r6 P3.)
for SH in $SHELLS; do
  REFUSED=$("$SH" -c "cd '$ROOT/wt' && _LI_SRC=a _LI_ROOT=b _LI_Q=c _LI_WT=d
source '$DETACHED' >/dev/null 2>&1
set | sed -n 's/^\(_LI_[A-Za-z0-9_]*\)=.*/\1/p' | grep -v '^_LI_ORPHAN_DIR\$' | sort | tr '\n' ' '")
  [ -z "$REFUSED" ] \
    && ok "$SH: a refused init clears the whole _LI_* namespace, not just what it had set" \
    || bad "$SH: refusal left reserved names defined: $REFUSED"
done

# `_LI_*` is lane-init's OWN namespace, and a caller's value in it is CLEARED, not preserved
# -- deliberately, and identically for the variable this arc introduced and the one that has
# always been there. codex r4 proposed save/restore for `_LI_SRC` alone; refused, because it
# would make one member behave unlike its siblings and add a restore arm no real caller
# reaches. This pins the decision so that "fixing" it later goes red instead of passing
# silently: both variables must read `cleared` even when the caller set them.
for SH in $SHELLS; do
  OWNED=$("$SH" -c "cd '$ROOT/wt' && _LI_SRC=caller-value _LI_ROOT=caller-root
source '$INIT' >/dev/null 2>&1
printf '%s/%s' \"\${_LI_SRC:-cleared}\" \"\${_LI_ROOT:-cleared}\"")
  [ "$OWNED" = "cleared/cleared" ] \
    && ok "$SH: _LI_* is lane-init's namespace — a caller's value is cleared, as for _LI_ROOT" \
    || bad "$SH: _LI_* not uniformly owned (_LI_SRC/_LI_ROOT): $OWNED"
done

# A refusal must also STRIP the lane identity, which is what every other failure path in
# lane-init.sh does. The case that matters is not a fresh shell (it has nothing to leak) but
# one already carrying lane A's identity that then sources a broken init for lane B: if the
# exports survive, the shell reports "not initialised" and keeps acting as lane A, and this
# workspace binds reservations to lane_id. (codex r2 P2.)
for SH in $SHELLS; do
  STALE=$("$SH" -c "export HARNESS_LANE_ID=laneA HARNESS_LANE_INDEX=1
source '$DETACHED' >/dev/null 2>&1
printf '%s/%s' \"\${HARNESS_LANE_ID:-cleared}\" \"\${HARNESS_LANE_INDEX:-cleared}\"")
  [ "$STALE" = "cleared/cleared" ] \
    && ok "$SH: a refused init clears a prior lane's exported identity" \
    || bad "$SH: refused init left a stale identity behind: $STALE"
done

DET_ERR=$(cd "$ROOT/wt" && bash -c "source '$DETACHED' 2>&1 >/dev/null")
case "$DET_ERR" in
  *"lane-init: cannot read tools/hooks/"*lib.sh*|*"lane-init: failed to load tools/hooks/"*lib.sh*)
    ok "and it names the library it could not load" ;;
  *) bad "failure message does not name the missing library: '$DET_ERR'" ;;
esac
case "$DET_ERR" in
  *"lane NOT initialised"*) ok "and it says the lane is not initialised" ;;
  *) bad "failure message does not state the lane is uninitialised: '$DET_ERR'" ;;
esac

echo "---"
[ -z "$SHELLS_UNVERIFIED" ] && echo "PASS=$PASS FAIL=$FAIL" \
  || echo "PASS=$PASS FAIL=$FAIL SHELLS_UNVERIFIED=$SHELLS_UNVERIFIED"
[ "$FAIL" -eq 0 ] || exit 1

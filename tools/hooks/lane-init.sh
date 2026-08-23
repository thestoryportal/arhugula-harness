#!/usr/bin/env bash
# Lane initialisation (C-HE-11). SOURCE this at worktree start:
#
#     source tools/hooks/lane-init.sh
#
# It exports HARNESS_LANE_ID (stable for the life of the worktree) and HARNESS_LANE_INDEX
# (the small integer `k` that namespaces this lane's Docker project and host ports), sets
# `gc.auto 0` repo-wide once, and defines `lane_stack_allowed` for the R-420 stack recipes.
#
# Sourced, never executed: the whole point is the exports. Do NOT `set -e` here — it would
# apply to the caller's shell.
#
# Three facts this file is the sole carrier of:
#   * the lane id is minted ONCE per worktree and PERSISTED at `.harness/.lane-id`
#     (gitignored). Re-minting per session would hand one lane two identities, and the
#     reservation store's same-lane resume would then read its own record as a peer's.
#   * the lane index is claimed by EXCLUSIVE CREATE of `QUEUE_DIR/lanes/<k>` and released
#     by `safe-worktree-remove.sh` at teardown. A worktree that already holds an entry
#     REUSES it: two entries for one path would strand whichever the release missed.
#   * a RAM shortfall is ENVIRONMENTAL. It is reported as a NOTIFY under a `lane-env:`
#     cause family, never a coordination one (C-HE-13 §3), and it skips the stack rather
#     than letting `docker compose up` fail opaquely mid-pilot (C-HE-11 §5).

_LI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=lib.sh
. "$_LI_ROOT/tools/hooks/lib.sh"
# shellcheck source=loop_lib.sh
. "$_LI_ROOT/tools/hooks/loop_lib.sh"

_LI_Q="${ARC_METRICS_QUEUE_DIR:-$HOME/.gstack/projects/arhugula-v2/arc-metrics-queue}"
_LI_WT="$(pwd -P)"   # physical path: the registry is compared against it at teardown

# ── lane id ──────────────────────────────────────────────────────────────────────────
_lane_init_id() {
  local f="$_LI_WT/.harness/.lane-id" id
  [ -n "${HARNESS_LANE_ID:-}" ] && { printf '%s' "$HARNESS_LANE_ID"; return 0; }
  if [ -s "$f" ]; then
    IFS= read -r id < "$f"
    [ -n "$id" ] && { printf '%s' "$id"; return 0; }
  fi
  id=$( (cd "$_LI_ROOT" && uv run --quiet python tools/reservations.py mint-lane-id \
          --worktree "$_LI_WT") 2>/dev/null | tr -d ' \t\n\r|;[]' )
  # Fallback keeps the SAME shape as reservations.mint_lane_id (host-worktree-8hex) so a
  # lane minted without uv is indistinguishable downstream from one minted with it.
  [ -n "$id" ] || id="$(hostname -s 2>/dev/null || echo host)-$(basename "$_LI_WT")-$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
  mkdir -p "$(dirname "$f")" 2>/dev/null
  # A ZERO-BYTE marker is a corpse, not a claim: only the pre-publication-protocol code
  # (or a stray `touch`) could produce one, and leaving it in place is unrecoverable —
  # `[ -s ]` never adopts it and an exclusive create can never replace it, so every later
  # session re-mints and none persists. Unlink it before publishing. Two shells both
  # repairing is harmless: publication is atomic and both re-read the winner's id.
  { [ -e "$f" ] && [ ! -s "$f" ]; } && rm -f "$f" 2>/dev/null
  # PUBLICATION PROTOCOL, the same one loop_status_ensure uses and for the same reason. A
  # bare `set -o noclobber; > "$f"` publishes the NAME at open() and the payload after: a
  # concurrent loser can see a file that is still empty, keep its own id, and the two shells
  # then hold divergent identities — and a crash inside that window leaves an empty marker
  # that noclobber can never replace, so every later run re-mints and none can persist.
  # Writing to an exclusively-created temp and publishing with `ln` makes the marker visible
  # only once it is COMPLETE; the loser of the link race is a harmless no-op.
  local tmp
  if tmp=$(mktemp "$f.XXXXXXXX" 2>/dev/null) && [ -n "$tmp" ]; then
    if printf '%s\n' "$id" > "$tmp" 2>/dev/null; then
      ln "$tmp" "$f" 2>/dev/null || true
    fi
    rm -f "$tmp" 2>/dev/null
  fi
  # RE-READ after publication: if a concurrent session in this worktree won the race, ITS id
  # is the lane id — adopting our own would fork the identity.
  # FAIL LOUD if nothing is there to read. Returning the freshly minted id from an
  # unpersisted publication would hand this session an identity the NEXT session cannot
  # recover — it would mint a different one for the same worktree, which is precisely the
  # split identity the persisted marker exists to prevent. An unwritable `.harness/` is a
  # broken lane, not a lane with a temporary id.
  if [ ! -s "$f" ]; then
    echo "lane-init: could not persist a lane id at $f — refusing to continue with an unrecoverable identity" >&2
    return 1
  fi
  IFS= read -r id < "$f"
  printf '%s' "$id"
}
if ! _LI_ID="$(_lane_init_id)"; then
  unset _LI_ROOT _LI_Q _LI_WT _LI_ID
  unset -f _lane_init_id
  return 1 2>/dev/null || exit 1
fi
export HARNESS_LANE_ID="$_LI_ID"
unset _LI_ID

# ── lane index ───────────────────────────────────────────────────────────────────────
# A preset HARNESS_LANE_INDEX is honoured verbatim and claims nothing: the caller
# (a compose recipe, a test) is asserting an index it already owns.
if [ -z "${HARNESS_LANE_INDEX:-}" ]; then
  mkdir -p "$_LI_Q/lanes" 2>/dev/null
  _li_k=""
  # Reuse this worktree's existing claim, unless HARNESS_LANE_INDEX_FORCE asks for a fresh
  # claim at or above a given index (the RAM-probe path needs a k>=2 lane on demand).
  if [ -z "${HARNESS_LANE_INDEX_FORCE:-}" ]; then
    for _li_f in "$_LI_Q"/lanes/*; do
      [ -f "$_li_f" ] || continue
      IFS=' ' read -r _li_id _li_path < "$_li_f"
      [ "${_li_path:-}" = "$_LI_WT" ] && { _li_k="$(basename "$_li_f")"; break; }
    done
  fi
  if [ -z "$_li_k" ]; then
    _li_k="${HARNESS_LANE_INDEX_FORCE:-0}"
    while :; do
      # SAME publication protocol as the lane-id marker, for the same reason: a bare
      # noclobber redirect makes the claim file visible EMPTY between open() and the
      # payload write, and a concurrent initializer of this same worktree reading it in
      # that window sees no owner, decides the claim is someone else's, and takes k+1 —
      # one lane, two indices, two stacks. The payload is written to an exclusively-created
      # temp and published with `ln`, so a claim is never observable without its owner.
      if _li_tmp=$(mktemp "$_LI_Q/lanes/.claim.XXXXXXXX" 2>/dev/null) && [ -n "$_li_tmp" ] \
         && printf '%s %s\n' "$HARNESS_LANE_ID" "$_LI_WT" > "$_li_tmp" 2>/dev/null \
         && ln "$_li_tmp" "$_LI_Q/lanes/$_li_k" 2>/dev/null; then
        rm -f "$_li_tmp" 2>/dev/null
        break
      fi
      rm -f "${_li_tmp:-}" 2>/dev/null
      # The claim can lose to a CONCURRENT init of THIS SAME worktree. Incrementing past it
      # would give one lane two indices, so the occupant is inspected: adopt it when it is
      # ours. A ZERO-BYTE occupant is a corpse the current protocol cannot produce (a
      # pre-protocol crash, or a stray touch) — unlink it and retry this same k ONCE, never
      # in a loop, so a genuinely contended index still advances.
      IFS=' ' read -r _li_id _li_path < "$_LI_Q/lanes/$_li_k" 2>/dev/null
      [ "${_li_path:-}" = "$_LI_WT" ] && break
      if [ -e "$_LI_Q/lanes/$_li_k" ] && [ ! -s "$_LI_Q/lanes/$_li_k" ] && [ -z "${_li_retried:-}" ]; then
        _li_retried=1; rm -f "$_LI_Q/lanes/$_li_k" 2>/dev/null; continue
      fi
      _li_retried=""
      _li_k=$((_li_k + 1))
      if [ "$_li_k" -ge 350 ]; then
        # Never fall through with an unset index: every consumer defaults to lane 0, so a
        # silent miss puts this lane on lane 0's project name, ports and volumes.
        echo "lane-init: no free lane index < 350 in $_LI_Q/lanes — refusing to continue" >&2
        unset _li_k _li_f _li_id _li_path _li_tmp _li_retried
        return 1 2>/dev/null || exit 1
      fi
    done
  fi
  export HARNESS_LANE_INDEX="$_li_k"
  unset _li_k _li_f _li_id _li_path _li_tmp _li_retried
fi

# ── git gc ───────────────────────────────────────────────────────────────────────────
# Repo-wide and idempotent: `extensions.worktreeConfig` is unset, so `git config` already
# writes the shared config — the read guard is what keeps it to ONE value, not a per-source
# duplicate that `--get-all` would return twice.
if [ "$(git config --get gc.auto 2>/dev/null)" != "0" ]; then
  git config gc.auto 0 2>/dev/null
fi

# ── RAM headroom probe (C-HE-11 §5) ──────────────────────────────────────────────────
# True when this lane may bring the three-container R-420 stack up. Lanes 0 and 1 always
# may: the floor exists to stop the THIRD concurrent stack on a 16 GB reference machine.
# The contract has TWO clauses and they are not the same measurement. TOTAL physical memory
# (the machine class) decides WHETHER to probe at all — that is what the 32 GB default is a
# floor on, and comparing a 32 GB default against free memory would refuse the third stack on
# exactly the machine the floor is written to admit. On a machine below that floor, the probe
# itself is of AVAILABLE memory against what one stack needs, so a small-but-idle machine can
# still run the lane and a small-and-loaded one is told why it cannot.
#
# HARNESS_LANE_STACK_NEED_GB is an implementation estimate for the three containers, not a
# spec number (the spec quantifies only the machine floor) — hence the knob. Unreadable
# availability is treated as a shortfall: refusing loudly beats an opaque `up` failure
# mid-pilot, which is the outcome this whole probe exists to replace.
_lane_available_gb() {
  if [ "$(uname)" = "Darwin" ]; then
    # vm_stat pages: free + inactive + speculative are reclaimable without swapping.
    vm_stat 2>/dev/null | awk '
      /page size of/ { for (i = 1; i <= NF; i++) if ($i ~ /^[0-9]+$/) ps = $i }
      /Pages free/ || /Pages inactive/ || /Pages speculative/ { gsub(/\./, "", $NF); pages += $NF }
      END { if (ps > 0 && pages > 0) printf "%d", (pages * ps) / 1073741824 }'
  else
    awk '/MemAvailable/ { printf "%d", $2 / 1048576 }' /proc/meminfo 2>/dev/null
  fi
}
lane_stack_allowed() {
  local floor_gb="${HARNESS_RAM_FLOOR_GB:-32}" need_gb="${HARNESS_LANE_STACK_NEED_GB:-6}"
  local mem_gb avail_gb k="${HARNESS_LANE_INDEX:-0}"
  [ "$k" -ge 2 ] || return 0
  if [ "$(uname)" = "Darwin" ]; then
    mem_gb=$(( $(sysctl -n hw.memsize) / 1073741824 ))
  else
    mem_gb=$(( $(awk '/MemTotal/{print $2}' /proc/meminfo) / 1048576 ))
  fi
  [ "$mem_gb" -ge "$floor_gb" ] && return 0          # at or above the floor: no probe owed
  avail_gb="$(_lane_available_gb)"
  if [ -n "$avail_gb" ] && [ "$avail_gb" -ge "$need_gb" ]; then
    return 0
  fi
  loop_log_structured NOTIFY "${HARNESS_LANE_ID:--}" "lane-env:transient-retry:ram_floor" \
    "lane $k: ${mem_gb}GB machine < floor ${floor_gb}GB and ${avail_gb:-unknown}GB available < ${need_gb}GB needed; self-hosted stack skipped (stack=absent)"
  return 1
}

unset _LI_ROOT _LI_Q _LI_WT
unset -f _lane_init_id

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

# Corpse repair (of a zero-byte marker or claim) must be MUTUALLY EXCLUSIVE. Atomic replace
# alone is not enough: two repairers each minting a value, replacing in sequence, and each
# re-reading at a different moment can walk away with different answers for one worktree.
# `mkdir` is the atomic exclusive primitive here. A repairer that cannot take the lock NEVER
# repairs — it waits briefly, re-reads what the holder published, and otherwise fails loud.
# There is deliberately no unlocked fallback: a stale lock (a crash mid-repair) leaves a
# visible `<path>.repair` directory and a named error, which is recoverable; an unlocked
# repair reintroduces exactly the divergence this lock exists to remove.
_lane_repair_lock() {
  local d="$1.repair" i=0
  while ! mkdir "$d" 2>/dev/null; do
    i=$((i + 1))
    [ "$i" -ge 25 ] && return 1     # ~2.5s — the holder published, or its lock is stale
    sleep 0.1
  done
  return 0
}
_lane_repair_unlock() { rmdir "$1.repair" 2>/dev/null; return 0; }

_LI_Q="${ARC_METRICS_QUEUE_DIR:-$HOME/.gstack/projects/arhugula-v2/arc-metrics-queue}"
_LI_WT="$(pwd -P)"   # physical path: the registry is compared against it at teardown
# The registry only means anything if every lane resolves it to the SAME directory. A
# relative override resolves against each lane's own CWD, so every lane would create its
# own `lanes/0` and then share one Docker project and port block while the registry looked
# perfectly consistent. Rejected as the misconfiguration it is (loop_status_path does the
# same for the same reason) rather than silently producing per-worktree registries.
case "$_LI_Q" in
  /*) ;;
  *) echo "lane-init: ARC_METRICS_QUEUE_DIR must be an absolute path, got '$_LI_Q'" >&2
     unset _LI_ROOT _LI_Q _LI_WT
     return 1 2>/dev/null || exit 1 ;;
esac

# ── lane id ──────────────────────────────────────────────────────────────────────────
# 0 iff some OTHER worktree's registry claim already carries this lane id — i.e. the value
# in the environment belongs to a different lane. One shell that sources in lane A, cd's to
# lane B and sources again would otherwise hand B the identity of A, and B would never get
# a marker of its own: two worktrees, one reservation identity.
_lane_id_bound_elsewhere() {
  local want="$1" f id path
  [ -d "$_LI_Q/lanes" ] || return 1
  for f in "$_LI_Q"/lanes/*; do
    [ -f "$f" ] || continue
    IFS=' ' read -r id path < "$f"
    { [ "${id:-}" = "$want" ] && [ "${path:-}" != "$_LI_WT" ]; } && return 0
  done
  return 1
}

_lane_init_id() {
  # id="" not a bare declaration: callers run under `set -u`, where reading an unset local
  # aborts the whole source.
  local f="$_LI_WT/.harness/.lane-id" id=""
  # THE MARKER IS THE AUTHORITY, ahead of the environment: it is per-worktree and durable,
  # while an exported id is per-shell and follows a `cd`. When both exist and disagree, the
  # marker wins and the stale export is corrected.
  # `-s` is a SIZE test, and a file holding just a newline passes it: publication then
  # cannot replace it (not a corpse by size) while every read yields an empty id. Emptiness
  # is therefore judged on the CONTENT of the first line, everywhere this file inspects it.
  _li_marker_blank() { [ ! -s "$1" ] && return 0; IFS= read -r _b < "$1"; [ -z "${_b:-}" ]; }
  if ! _li_marker_blank "$f"; then
    IFS= read -r id < "$f"
    if [ -n "$id" ]; then
      { [ -n "${HARNESS_LANE_ID:-}" ] && [ "$HARNESS_LANE_ID" != "$id" ]; } \
        && echo "lane-init: HARNESS_LANE_ID=$HARNESS_LANE_ID does not belong to this worktree — using the persisted $id" >&2
      printf '%s' "$id"
      return 0
    fi
  fi
  if [ -n "${HARNESS_LANE_ID:-}" ]; then
    # Sanitise FIRST, then test. An exported value is operator- or agent-supplied text, and
    # the sanitiser is what will actually be persisted — checking the raw form lets `bad id`
    # slip past a lane already holding `badid`, which is the same identity after stripping.
    id=$(printf '%s' "$HARNESS_LANE_ID" | tr -d ' \t\n\r|;[]')
    _lane_id_bound_elsewhere "$id" && id=""
  fi
  [ -n "$id" ] || id=$( (cd "$_LI_ROOT" && uv run --quiet python tools/reservations.py mint-lane-id \
          --worktree "$_LI_WT") 2>/dev/null | tr -d ' \t\n\r|;[]' )
  # Fallback keeps the SAME shape as reservations.mint_lane_id (host-worktree-8hex) so a
  # lane minted without uv is indistinguishable downstream from one minted with it.
  # The fallback runs through the SAME sanitiser as the uv-minted id: the claim record is
  # space-delimited and a worktree basename with a space would make every later read
  # misparse the path — the same worktree would claim extra indices and teardown would
  # match none of them.
  [ -n "$id" ] || id="$(printf '%s-%s-%s' "$(hostname -s 2>/dev/null || echo host)" \
    "$(basename "$_LI_WT")" "$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')" | tr -d ' \t\n\r|;[]')"
  mkdir -p "$(dirname "$f")" 2>/dev/null
  # A ZERO-BYTE marker is a corpse, not a claim: only the pre-publication-protocol code
  # (or a stray `touch`) could produce one, and leaving it in place is unrecoverable —
  # `[ -s ]` never adopts it and an exclusive create can never replace it, so every later
  # session re-mints and none persists.
  #
  # Repair publishes by RENAME, never unlink-then-link. Unlinking first is check-then-act:
  # a second repairer that has already published a complete marker can have it deleted by a
  # first repairer still acting on its stale "it is empty" observation, and the two shells
  # then hold different ids. `mv` replaces atomically — concurrent repairers simply order,
  # the last one wins, and BOTH re-read the published file below and converge on one id.
  local corpse_repair=""
  if [ -e "$f" ] && _li_marker_blank "$f"; then
    if _lane_repair_lock "$f"; then
      # RECHECK under the lock. The observation that sent us here was made BEFORE the wait,
      # and the repairer we waited for may have published in the meantime — replacing its
      # marker now would give this worktree a second identity after the first was exported.
      if ! _li_marker_blank "$f"; then
        IFS= read -r id < "$f"
        _lane_repair_unlock "$f"
        printf '%s' "$id"
        return 0
      fi
      corpse_repair=1
    else
      # Another repairer holds the lock. Whatever it published is authoritative; adopt it.
      if ! _li_marker_blank "$f"; then
        IFS= read -r id < "$f"
        printf '%s' "$id"
        return 0
      fi
      echo "lane-init: a stale repair lock blocks $f.repair — remove it and re-open the lane" >&2
      return 1
    fi
  fi
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
      if [ -n "$corpse_repair" ]; then
        mv -f "$tmp" "$f" 2>/dev/null || true      # atomic replace, under the repair lock
      else
        ln "$tmp" "$f" 2>/dev/null || true         # never clobbers a live marker
      fi
    fi
    rm -f "$tmp" 2>/dev/null
  fi
  [ -n "$corpse_repair" ] && _lane_repair_unlock "$f"
  # RE-READ after publication: if a concurrent session in this worktree won the race, ITS id
  # is the lane id — adopting our own would fork the identity.
  # FAIL LOUD if nothing is there to read. Returning the freshly minted id from an
  # unpersisted publication would hand this session an identity the NEXT session cannot
  # recover — it would mint a different one for the same worktree, which is precisely the
  # split identity the persisted marker exists to prevent. An unwritable `.harness/` is a
  # broken lane, not a lane with a temporary id.
  if _li_marker_blank "$f"; then
    echo "lane-init: could not persist a lane id at $f — refusing to continue with an unrecoverable identity" >&2
    return 1
  fi
  IFS= read -r id < "$f"
  # Final gate: an empty id would be exported, written into claims, and matched by nothing.
  if [ -z "$id" ]; then
    echo "lane-init: the persisted lane id at $f is empty — refusing to continue" >&2
    return 1
  fi
  printf '%s' "$id"
}
if ! _LI_ID="$(_lane_init_id)"; then
  unset _LI_ROOT _LI_Q _LI_WT _LI_ID
  unset -f _lane_init_id
  return 1 2>/dev/null || exit 1
fi
export HARNESS_LANE_ID="$_LI_ID"
unset _LI_ID
# Every failure PAST this point unsets the export again. An id left in a failed shell would
# be inherited by the next worktree that shell enters, and because the failed lane holds no
# claim, nothing binds it elsewhere — the bind check would accept it and two worktrees would
# persist one reservation identity.

# ── lane index ───────────────────────────────────────────────────────────────────────
# ── lane index ───────────────────────────────────────────────────────────────────────
# ONE rule governs every path below: a worktree holds AT MOST ONE claim, and an index is
# usable only when a claim positively names this worktree. HARNESS_LANE_INDEX is the single
# knob — it asks for a specific index rather than the next free one; it is not an escape
# from the rule, and a lane that already holds a different index is refused.

# The index becomes a FILENAME under QUEUE_DIR/lanes and the input to the port formula, so
# it is validated before it can be either. `00` and `08` parse as integers but are DIFFERENT
# filenames from `0` and `8` while mapping to the same Compose project, and `../…` would
# publish a claim outside the registry.
if [ -n "${HARNESS_LANE_INDEX:-}" ]; then
  case "$HARNESS_LANE_INDEX" in
    ''|*[!0-9]*)
      echo "lane-init: HARNESS_LANE_INDEX must be an integer 0..349, got '$HARNESS_LANE_INDEX'" >&2
      unset HARNESS_LANE_ID _LI_ROOT _LI_Q _LI_WT; return 1 2>/dev/null || exit 1 ;;
    0) ;;
    0*)
      echo "lane-init: HARNESS_LANE_INDEX must be canonical (no leading zeros), got '$HARNESS_LANE_INDEX'" >&2
      unset HARNESS_LANE_ID _LI_ROOT _LI_Q _LI_WT; return 1 2>/dev/null || exit 1 ;;
  esac
  # Bound the LENGTH before the comparison: a digit string too large for the shell's integer
  # type makes `test -ge` exit 2, which `if` reads as false — and a 30-digit index would then
  # be published as a claim filename. Every valid index is at most three digits.
  if [ "${#HARNESS_LANE_INDEX}" -gt 3 ] || [ "$HARNESS_LANE_INDEX" -ge 350 ]; then
    echo "lane-init: HARNESS_LANE_INDEX must be < 350 (no port block exists above it), got '$HARNESS_LANE_INDEX'" >&2
    unset HARNESS_LANE_ID _LI_ROOT _LI_Q _LI_WT; return 1 2>/dev/null || exit 1
  fi
fi

mkdir -p "$_LI_Q/lanes" 2>/dev/null
# What this worktree already holds, resolved ONCE and used by both paths below.
_li_have=""
for _li_f in "$_LI_Q"/lanes/*; do
  [ -f "$_li_f" ] || continue
  IFS=' ' read -r _li_id _li_path < "$_li_f"
  if [ "${_li_path:-}" = "$_LI_WT" ]; then
    _li_have="$(basename "$_li_f")"
    # A claim recorded under a DIFFERENT lane id at this path belongs to a previous occupant
    # (a worktree reaped whose teardown could not fence the index, then recreated at the same
    # path). Reuse is by path, so it is adopted — but its stack is unaccounted for, and the
    # missing fence is written now rather than letting this lane adopt those containers.
    if [ -n "${_li_id:-}" ] && [ "${_li_id:-}" != "$HARNESS_LANE_ID" ]; then
      # The fence must LAND before the claim is rebound. Rebinding first and failing to write
      # the marker would leave the new lane owning an index whose stack is unaccounted for —
      # with nothing left to say so.
      if ! printf '%s inherited-claim %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${_li_id:-}" \
           > "$_LI_Q/lanes/.orphaned-$_li_have" 2>/dev/null; then
        echo "lane-init: cannot fence inherited lane index $_li_have (marker unwritable) — refusing to adopt a stack this lane cannot account for" >&2
        unset HARNESS_LANE_ID
        unset _LI_ROOT _LI_Q _LI_WT _li_have _li_f _li_id _li_path
        return 1 2>/dev/null || exit 1
      fi
      # ATOMIC rebind, and checked. Truncating the authoritative claim in place opens a
      # window in which a concurrent initializer reads an empty claim (and allocates a
      # second index for this same worktree), and an unchecked write can leave it that way.
      if ! { _li_tmp=$(mktemp "$_LI_Q/lanes/.claim.XXXXXXXX" 2>/dev/null) && [ -n "$_li_tmp" ] \
             && printf '%s %s\n' "$HARNESS_LANE_ID" "$_LI_WT" > "$_li_tmp" 2>/dev/null \
             && mv -f "$_li_tmp" "$_li_f" 2>/dev/null; }; then
        rm -f "${_li_tmp:-}" 2>/dev/null
        echo "lane-init: could not rebind inherited lane index $_li_have to this lane — refusing rather than running on a claim that names someone else" >&2
        unset HARNESS_LANE_ID
        unset _LI_ROOT _LI_Q _LI_WT _li_have _li_f _li_id _li_path _li_tmp
        return 1 2>/dev/null || exit 1
      fi
      unset _li_tmp
      echo "lane-init: adopted lane index $_li_have from a previous occupant of this path (${_li_id:-unknown}) — its stack is fenced until cleanup succeeds" >&2
    fi
    break
  fi
done
unset _li_f _li_id _li_path

if [ -n "${HARNESS_LANE_INDEX:-}" ]; then
  if [ -n "$_li_have" ] && [ "$_li_have" != "$HARNESS_LANE_INDEX" ]; then
    echo "lane-init: this worktree already holds lane index $_li_have — refusing to also take $HARNESS_LANE_INDEX" >&2
    unset HARNESS_LANE_ID
    unset _LI_ROOT _LI_Q _LI_WT _li_have; return 1 2>/dev/null || exit 1
  fi
  _li_published=""
  if [ -z "$_li_have" ]; then
    # TAKE the requested index — a preset that claims nothing lets two worktrees name the
    # same free index and both proceed onto one Compose project. Published as a complete
    # temp file linked into place, so the claim is never observable without its owner.
    if _li_tmp=$(mktemp "$_LI_Q/lanes/.claim.XXXXXXXX" 2>/dev/null) && [ -n "$_li_tmp" ] \
       && printf '%s %s\n' "$HARNESS_LANE_ID" "$_LI_WT" > "$_li_tmp" 2>/dev/null \
       && ln "$_li_tmp" "$_LI_Q/lanes/$HARNESS_LANE_INDEX" 2>/dev/null; then
      _li_published=1     # WE created it — only then may the withdrawal below remove it
    fi
    rm -f "${_li_tmp:-}" 2>/dev/null; unset _li_tmp
  fi
  # POSITIVE verification, never absence-of-objection: a missing, empty or malformed claim
  # would put this lane on a project no one is recorded as owning — a state a concurrent
  # caller can walk into just as easily.
  _li_ok=""
  if [ -f "$_LI_Q/lanes/$HARNESS_LANE_INDEX" ]; then
    IFS=' ' read -r _li_id _li_path < "$_LI_Q/lanes/$HARNESS_LANE_INDEX"
    [ "${_li_path:-}" = "$_LI_WT" ] && _li_ok=1
  fi
  if [ -z "$_li_ok" ]; then
    echo "lane-init: HARNESS_LANE_INDEX=$HARNESS_LANE_INDEX could not be claimed for this worktree (claim: [$(cat "$_LI_Q/lanes/$HARNESS_LANE_INDEX" 2>/dev/null)]) — refusing to run on a project this lane does not own" >&2
    unset HARNESS_LANE_ID
    unset _LI_ROOT _LI_Q _LI_WT _li_have _li_id _li_path _li_ok
    return 1 2>/dev/null || exit 1
  fi
  unset _li_id _li_path _li_ok
  # POST-VERIFY: the scan above and the create below are not one atomic step, so two
  # concurrent sources in THIS worktree asking for different indices can both pass the scan
  # and both link a claim. Re-scanning afterwards catches that; the newer claim (ours) is
  # withdrawn and the peer's stands, so the lane converges on one index instead of two.
  for _li_f in "$_LI_Q"/lanes/*; do
    [ -f "$_li_f" ] || continue
    IFS=' ' read -r _li_id _li_path < "$_li_f"
    if [ "${_li_path:-}" = "$_LI_WT" ] && [ "$(basename "$_li_f")" != "$HARNESS_LANE_INDEX" ]; then
      # Withdraw ONLY a claim this source published. Adopting a peer's claim and then deleting
      # it on our way out would strip a lane that has already returned success — it would run
      # unclaimed while another worktree is free to take its index, ports and volumes.
      if [ -n "$_li_published" ]; then
        rm -f "$_LI_Q/lanes/$HARNESS_LANE_INDEX" 2>/dev/null
        echo "lane-init: raced a concurrent init of this worktree, which holds lane index $(basename "$_li_f") — withdrew the duplicate claim on $HARNESS_LANE_INDEX" >&2
      else
        echo "lane-init: this worktree holds lane index $(basename "$_li_f"); the claim on $HARNESS_LANE_INDEX was published by another source and is left alone" >&2
      fi
    unset HARNESS_LANE_ID
      unset _LI_ROOT _LI_Q _LI_WT _li_have _li_f _li_id _li_path
      return 1 2>/dev/null || exit 1
    fi
  done
  unset _li_f _li_id _li_path
elif [ -n "$_li_have" ]; then
  export HARNESS_LANE_INDEX="$_li_have"
else
  _li_k=0
  while :; do
    # SAME publication protocol as the lane-id marker, for the same reason: a bare noclobber
    # redirect makes the claim visible EMPTY between open() and the payload write, and a
    # concurrent initializer reading it there sees no owner and takes the next index — one
    # lane, two indices, two stacks.
    if _li_tmp=$(mktemp "$_LI_Q/lanes/.claim.XXXXXXXX" 2>/dev/null) && [ -n "$_li_tmp" ] \
       && printf '%s %s\n' "$HARNESS_LANE_ID" "$_LI_WT" > "$_li_tmp" 2>/dev/null \
       && ln "$_li_tmp" "$_LI_Q/lanes/$_li_k" 2>/dev/null; then
      rm -f "$_li_tmp" 2>/dev/null
      break
    fi
    rm -f "${_li_tmp:-}" 2>/dev/null
    # Lost the create. Adopt it if it is ours (a concurrent init of this same lane);
    # otherwise a ZERO-BYTE occupant is a corpse the current protocol cannot produce (a
    # pre-protocol crash, or a stray touch), repaired ONCE under an exclusive lock.
    IFS=' ' read -r _li_id _li_path < "$_LI_Q/lanes/$_li_k" 2>/dev/null
    [ "${_li_path:-}" = "$_LI_WT" ] && break
    if [ -e "$_LI_Q/lanes/$_li_k" ] && [ ! -s "$_LI_Q/lanes/$_li_k" ] && [ -z "${_li_retried:-}" ]; then
      _li_retried=1
      if _lane_repair_lock "$_LI_Q/lanes/$_li_k"; then
        # RECHECK under the lock: the claim may have been published while we waited, and
        # replacing it now would put two worktrees on one index.
        if [ -s "$_LI_Q/lanes/$_li_k" ]; then
          IFS=' ' read -r _li_id _li_path < "$_LI_Q/lanes/$_li_k"
          _lane_repair_unlock "$_LI_Q/lanes/$_li_k"
          [ "${_li_path:-}" = "$_LI_WT" ] && break
          _li_k=$((_li_k + 1)); _li_retried=""; continue
        fi
        if _li_tmp=$(mktemp "$_LI_Q/lanes/.claim.XXXXXXXX" 2>/dev/null) && [ -n "$_li_tmp" ] \
           && printf '%s %s\n' "$HARNESS_LANE_ID" "$_LI_WT" > "$_li_tmp" 2>/dev/null \
           && mv -f "$_li_tmp" "$_LI_Q/lanes/$_li_k" 2>/dev/null; then
          IFS=' ' read -r _li_id _li_path < "$_LI_Q/lanes/$_li_k" 2>/dev/null
          _lane_repair_unlock "$_LI_Q/lanes/$_li_k"
          [ "${_li_path:-}" = "$_LI_WT" ] && break
          rm -f "${_li_tmp:-}" 2>/dev/null
          _li_k=$((_li_k + 1)); _li_retried=""; continue
        fi
        _lane_repair_unlock "$_LI_Q/lanes/$_li_k"
      else
        # The lock stayed held for the whole wait. Incrementing is the one thing not to do:
        # the delayed repairer may publish THIS worktree's claim a moment later, and a
        # concurrent init of the same lane would then hold a different index.
        if [ -s "$_LI_Q/lanes/$_li_k" ]; then
          IFS=' ' read -r _li_id _li_path < "$_LI_Q/lanes/$_li_k"
          [ "${_li_path:-}" = "$_LI_WT" ] && break
        else
          echo "lane-init: a stale repair lock blocks $_LI_Q/lanes/$_li_k.repair — remove it and re-open the lane" >&2
    unset HARNESS_LANE_ID
          unset _li_k _li_id _li_path _li_tmp _li_retried _li_have
          return 1 2>/dev/null || exit 1
        fi
      fi
      rm -f "${_li_tmp:-}" 2>/dev/null
    fi
    _li_retried=""
    _li_k=$((_li_k + 1))
    if [ "$_li_k" -ge 350 ]; then
      # Never fall through with an unset index: every consumer defaults to lane 0, so a
      # silent miss puts this lane on lane 0's project name, ports and volumes.
      echo "lane-init: no free lane index < 350 in $_LI_Q/lanes — refusing to continue" >&2
    unset HARNESS_LANE_ID
      unset _li_k _li_id _li_path _li_tmp _li_retried _li_have
      return 1 2>/dev/null || exit 1
    fi
  done
  # SAME post-verify the preset branch does, for the same reason: the scan that found no
  # existing claim and the link below are not one atomic step, so a concurrent preset init
  # of this worktree could have taken a different index in between. One lane, one claim —
  # the newer claim (ours) is withdrawn and the peer's stands.
  for _li_f in "$_LI_Q"/lanes/*; do
    [ -f "$_li_f" ] || continue
    IFS=' ' read -r _li_id _li_path < "$_li_f"
    if [ "${_li_path:-}" = "$_LI_WT" ] && [ "$(basename "$_li_f")" != "$_li_k" ]; then
      rm -f "$_LI_Q/lanes/$_li_k" 2>/dev/null
      echo "lane-init: raced a concurrent init of this worktree, which holds lane index $(basename "$_li_f") — withdrew the duplicate claim on $_li_k" >&2
    unset HARNESS_LANE_ID
      unset _LI_ROOT _LI_Q _LI_WT _li_have _li_k _li_f _li_id _li_path _li_tmp _li_retried
      return 1 2>/dev/null || exit 1
    fi
  done
  export HARNESS_LANE_INDEX="$_li_k"
  unset _li_k _li_f _li_id _li_path _li_tmp _li_retried
fi
unset _li_have

# ── deferred stack cleanup (C-HE-11 §1) ──────────────────────────────────────────────
# A lane reaped while the Docker daemon was unreachable cannot have its stack taken down at
# that moment, so the release leaves `lanes/.orphaned-<k>` behind (a dotfile: invisible to
# the `lanes/*` scans). Cleanup then happens HERE — at the one point where it matters, just
# before a new lane uses that index, and where the daemon is far more likely to be up.
# While the marker survives, this lane's stack stays ABSENT rather than risking `up`
# ADOPTING the dead lane's containers and volumes.
_lane_clear_orphaned_stack() {
  local k="${HARNESS_LANE_INDEX:-}" marker
  [ -n "$k" ] || return 0
  marker="$_LI_ORPHAN_DIR/.orphaned-$k"
  [ -f "$marker" ] || return 0
  # The check and the DESTRUCTIVE `down --volumes` must be one critical section. Unlocked,
  # two sources both see the marker; the first cleans it, clears it and brings its stack up,
  # and the second — still acting on its stale observation — tears that new stack and its
  # volumes down. Same exclusive primitive the corpse repairs use, same rules: no unlocked
  # fallback, and RE-CHECK inside the lock, because the holder may have just cleared it.
  if ! _lane_repair_lock "$marker"; then
    echo "lane-init: another init holds the cleanup lock for lane $k — keeping the stack absent this round rather than racing its teardown" >&2
    return 1
  fi
  if [ ! -f "$marker" ]; then
    _lane_repair_unlock "$marker"      # the holder cleaned it while we waited
    return 0
  fi
  if _hook_lane_stack_down "$k"; then
    # The removal is checked. A marker that survives a successful cleanup is worse than one
    # that was never written: the NEXT source of lane-init sees it and runs `down --volumes`
    # against THIS lane's live stack. Refusing keeps the stack absent instead.
    if ! rm -f "$marker" 2>/dev/null || [ -e "$marker" ]; then
      echo "lane-init: cleaned lane $k but could NOT remove its orphan marker $marker — keeping the stack absent, since a later init would tear down a stack started now" >&2
      _lane_repair_unlock "$marker"
      return 1
    fi
    _lane_repair_unlock "$marker"
    return 0
  fi
  echo "lane-init: lane $k inherits an UNCLEANED stack from a previously reaped lane (marker $marker) — its stack stays absent until Docker can remove it" >&2
  _lane_repair_unlock "$marker"
  return 1
}
_LI_ORPHAN_DIR="$_LI_Q/lanes"
# NOT called at source time. Sourcing is what `just r420-self-hosted-stack-status` does, and
# clearing a fence runs `down --volumes` — which would make a read-only status command delete
# an orphaned project's containers and volumes before printing anything. The fence is honoured
# where it matters instead: inside lane_stack_allowed, which only a lane bringing a stack UP
# calls.

# ── git gc ───────────────────────────────────────────────────────────────────────────
# Repo-wide and idempotent: `extensions.worktreeConfig` is unset, so `git config` already
# writes the shared config — the read guard is what keeps it to ONE value, not a per-source
# duplicate that `--get-all` would return twice.
if [ "$(git config --get gc.auto 2>/dev/null)" != "0" ]; then
  # A discarded failure here silently leaves automatic GC enabled — the very concurrency
  # hazard §2 exists to remove — with nothing to notice. The lane still opens (gc.auto is
  # hygiene, not a correctness invariant of the lane), but never quietly.
  if ! git config gc.auto 0 2>/dev/null; then
    echo "lane-init: could NOT set gc.auto=0 (C-HE-11 §2) — automatic git gc stays enabled for this repo" >&2
  fi
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
  # An index still carrying a dead lane's stack is refused at ANY k, including 0 and 1:
  # `up` would adopt those containers rather than fail, which is the silent outcome.
  # 3, not 1: an uncleaned inherited stack is a FAULT, while the RAM skip below is a
  # designed degradation the contract asks for (the lane builds, stack=absent). Collapsing
  # them lets the recipe exit 0 on a fault and downstream automation proceed as if the stack
  # were merely skipped.
  if ! _lane_clear_orphaned_stack; then
    return 3
  fi
  [ "$k" -ge 2 ] || return 0
  if [ "$(uname)" = "Darwin" ]; then
    mem_gb=$(( $(sysctl -n hw.memsize) / 1073741824 ))
  else
    mem_gb=$(( $(awk '/MemTotal/{print $2}' /proc/meminfo) / 1048576 ))
  fi
  [ "$mem_gb" -ge "$floor_gb" ] && return 0          # at or above the floor: no probe owed
  # The contract names "available memory / Docker-VM headroom", and on macOS those are
  # different numbers: the containers live inside Docker Desktop's VM, whose ceiling is set
  # independently of host RAM. When a daemon answers, ITS total is the figure that decides
  # whether three containers fit; host availability is the fallback when it cannot.
  # `docker info` reports the VM's TOTAL capacity, not its free headroom — a VM sized large
  # but already full would pass a ceiling-only test and then OOM opaquely, which is the
  # failure this probe exists to replace. So the ceiling is a NECESSARY condition checked
  # alongside host availability, never a substitute for it: both must clear the bar.
  local vm_gb=""
  if command -v docker >/dev/null 2>&1 && hook_bounded 10 docker info >/dev/null 2>&1; then
    vm_gb=$(hook_bounded 10 docker info --format '{{.MemTotal}}' 2>/dev/null \
      | awk '/^[0-9]+$/ { printf "%d", $1 / 1073741824 }')
    if [ -n "$vm_gb" ] && [ "$vm_gb" -lt "$need_gb" ]; then
      if ! loop_log_structured NOTIFY "${HARNESS_LANE_ID:--}" "lane-env:transient-retry:ram_floor" \
          "lane $k: Docker VM total ${vm_gb}GB < ${need_gb}GB needed; self-hosted stack skipped (stack=absent)"; then
        echo "lane-init: Docker VM too small for lane $k, and the NOTIFY row could NOT be written" >&2
      fi
      return 1
    fi
  fi
  avail_gb="$(_lane_available_gb)"
  if [ -n "$avail_gb" ] && [ "$avail_gb" -ge "$need_gb" ]; then
    return 0
  fi
  # The skip stands whatever the ledger does — but SAYING a NOTIFY was emitted when the
  # write failed is a lie the operator acts on (they would look for a row that is not there).
  if ! loop_log_structured NOTIFY "${HARNESS_LANE_ID:--}" "lane-env:transient-retry:ram_floor" \
      "lane $k: ${mem_gb}GB machine < floor ${floor_gb}GB and ${avail_gb:-unknown}GB available < ${need_gb}GB needed; self-hosted stack skipped (stack=absent)"; then
    echo "lane-init: RAM shortfall at lane $k, and the NOTIFY row could NOT be written — this skip leaves no durable record" >&2
  fi
  return 1
}

unset _LI_ROOT _LI_Q _LI_WT
unset -f _lane_init_id

#!/usr/bin/env bash
# Loop-mode ledger library (U-HK-11) — the Wave-2 autonomy substrate.
#
# Sourced by the Wave-2 autonomy hooks (permission-guard, stop-loop, resolve) and
# the /loop-start | /loop-stop skills. Provides the loop-mode marker toggle and an
# append-only status ledger at the SHARED venue `loop_status_path()` (C-HE-09 §2 --
# one file for every lane, outside every worktree) that records the things a
# human will want to review after an unattended run: deferred genuinely-blocking
# HILs (creds / vendor / paid calls), what the loop completed AROUND them, hard-stop
# denials, Codex+Advisor decision splits, and resume state.
#
# Depends on lib.sh (hook_project_dir, loop_mode_active). Source lib.sh FIRST, then
# this. Pure library — no `set -e` (would surprise the sourcing script). The only
# side-effects are the explicit file ops in loop_activate / loop_deactivate / loop_log.
# Test with tools/hooks/test_loop_lib.sh.

# Path to the loop-mode marker file (presence === loop active, alongside HARNESS_LOOP=1).
# Echoes empty if the project dir cannot be resolved (caller should treat as off).
loop_marker_path() {
  local d; d=$(hook_project_dir)
  [ -n "$d" ] && printf '%s' "$d/.harness/.loop-active"
}

# Path to the append-only status ledger -- the SHARED venue (C-HE-09 §2): ONE file for
# every lane and every caller, hook or raw shell. QUEUE_DIR-adjacent (outside every
# worktree), never per-worktree: DEFERRED-HIL / RESOLVED-HIL / NOTIFY / COALESCE-DELIVERED
# rows must reduce to one answer for every lane (X6/E10). A per-worktree venue split the
# ledger so lane B could not see lane A's open deferral and re-attempted a gated item.
# CONTROL markers (the .loop-active marker, .loop-iter, .loop-halt) deliberately stay
# per-lane under hook_project_dir() -- they scope one lane's run, not the shared queue.
loop_status_path() {
  local p
  if [ -n "${HARNESS_LOOP_STATUS_PATH:-}" ]; then
    p="$HARNESS_LOOP_STATUS_PATH"
  else
    local q="${ARC_METRICS_QUEUE_DIR:-$HOME/.gstack/projects/arhugula-v2/arc-metrics-queue}"
    p="$(dirname "$q")/loop_status.md"
  fi
  # A RELATIVE override would silently defeat the whole contract: each lane would resolve
  # the same string against its own CWD and write a DIFFERENT physical file, while any
  # test comparing the returned strings still sees them as equal. Absolutizing against
  # CWD would not help (it is the CWD that differs), so a non-absolute venue is rejected
  # as the misconfiguration it is -- echo nothing and say why. Every caller already treats
  # an empty path as "no venue": the reducers return empty and loop_log_structured fails
  # closed with a message, which is the correct outcome for an unusable venue.
  case "$p" in
    /*) ;;
    *) echo "loop_status_path: venue must be an absolute path, got '$p'" >&2; return 1 ;;
  esac
  printf '%s' "$p"
}

# Path to the Stop-continue iteration counter (U-HK-14 bound). Presence + integer
# value cap the number of auto-continued turns per run.
loop_iter_path() {
  local d; d=$(hook_project_dir)
  [ -n "$d" ] && printf '%s' "$d/.harness/.loop-iter"
}

# Path to the halt marker (U-HK-14). When present, the next Stop stops the loop — the
# explicit "we hit a genuine gate, stand down" signal Claude/skills drop at a gate.
loop_halt_path() {
  local d; d=$(hook_project_dir)
  [ -n "$d" ] && printf '%s' "$d/.harness/.loop-halt"
}

# A UTC ISO-8601 timestamp (second precision). Isolated so tests can stub it.
loop_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# Ensure the ledger exists, creating it from the canonical header if absent.
# Idempotent. Echoes the path (empty if unresolvable).
loop_status_ensure() {
  local p; p=$(loop_status_path)
  [ -z "$p" ] && return 0
  if [ ! -f "$p" ]; then
    mkdir -p "$(dirname "$p")" 2>/dev/null
    # PUBLICATION PROTOCOL (codex r1 P2, tightened at r2 P2). A plain `cat > "$p"` after
    # the -f test is a first-writer TOCTOU: two lanes both see the venue absent and the
    # loser's truncating redirect erases rows the winner already appended -- destroying a
    # durable DEFERRED-HIL / NOTIFY signal while the writer still reports success. Now that
    # the venue is SHARED this is reachable in normal operation.
    #
    # `set -o noclobber` alone (the r1 fix) does NOT close it: O_EXCL makes the file appear
    # at open() time, so a second lane's `-f` test passes and it starts appending while the
    # winner is still writing the header through a NON-append fd -- whose later writes go to
    # absolute offsets and can land on top of that appended row.
    #
    # So the header is written to a temp file FIRST and published by `ln`, which is atomic
    # and fails with EEXIST if the venue already exists. The venue therefore never exists in
    # a partially-written state: by the time any other lane can see it, the header is
    # complete and every subsequent write is an O_APPEND row. The loser of the link race is
    # a harmless no-op (the winner's header is equally valid -- there is nothing to merge).
    # EXCLUSIVE staging name (codex r6 P2). `$$` is shared by every subshell of one bash and
    # $RANDOM is 15 bits, so two concurrent callers could pick the SAME staging path, both
    # write it, and one could publish it while the other was still writing -- reintroducing
    # the partial-publication race this protocol exists to remove. mktemp creates with
    # O_EXCL and never returns a name it did not just create.
    # NO fallback to a guessable name (codex r16 P3): reverting to `$$`/`$RANDOM` would
    # reinstate exactly the shared-inode publication race this protocol exists to remove.
    # If mktemp cannot give us an exclusively-created staging file, we do not create the
    # venue at all -- callers already treat an absent venue as a hard write failure.
    local _tmp
    if ! _tmp=$(mktemp "${p}.XXXXXXXX" 2>/dev/null) || [ -z "$_tmp" ]; then
      echo "loop_status_ensure: cannot create an exclusive staging file for $p" >&2
      return 0
    fi
    (
      cat > "$_tmp" <<'EOF'
# Loop status ledger

*Append-only record of autonomous loop-mode activity (Wave 2, U-HK-11), SHARED by every
lane (C-HE-09 §1/§2 — one file, never a per-worktree copy). OFF by default: rows are
written only while loop mode is active (`HARNESS_LOOP=1` or a lane's `.loop-active`
marker). Review after an unattended run: each `DEFERRED-HIL` is a genuine gate (creds /
vendor / paid call / destructive op) the loop refused to auto-fire and worked around; a
later `RESOLVED-HIL` row for the same item-id is the ONLY thing that clears it (C-HE-09
§4 — a lane's `ACTIVATE` never resets another lane's row); `NOTIFY` is append-only
informational, rendered beside the pending summary and never part of it;
`COALESCE-DELIVERED` records one batched-prompt delivery (C-HE-10); `DENY` is a hard-stop
the permission guard blocked; `RESOLVE-SPLIT` is a Codex+Advisor disagreement where the
safer default was taken.*

| timestamp | kind | lane;cause | detail |
|---|---|---|---|
EOF
    ) 2>/dev/null
    local _staged=$?
    # Publish ONLY a COMPLETE staging file (codex r22 P2). Linking first and checking after
    # could publish a half-written header — and once the venue exists, later calls append to
    # it, concatenating the first durable row onto an incomplete line where the reducers
    # cannot see it. The whole point of staging is that nothing partial becomes visible.
    [ "$_staged" -eq 0 ] && { ln "$_tmp" "$p" 2>/dev/null || true; }  # lost race: winner's header stands
    rm -f "$_tmp" 2>/dev/null
    # HONOUR both outcomes (codex r21 P2). A partial staging write must not be published,
    # and if the link failed with NOBODY winning, returning `$p` anyway would let the next
    # append create a HEADERLESS ledger and report success. The venue is only usable if it
    # now exists -- whether this process created it or lost the race to one that did.
    if [ "$_staged" -ne 0 ] || [ ! -f "$p" ]; then
      echo "loop_status_ensure: could not publish a complete ledger header at $p" >&2
      return 0
    fi
  fi
  printf '%s' "$p"
}

# The structured column (C-HE-09 §3), built in ONE place so the writer and loop_resolve's
# own-write verification can never disagree about its spelling. Column separators and
# whitespace are stripped: the token must contain no `|` (it would split the row) and no
# space (the reducers' item-token split keys on whitespace). Usage: _loop_structured_col
# <lane> <cause> -> `lane=<lane>;cause=<cause>`, each defaulting to `-`.
_loop_structured_col() {
  local lane cause
  # NEWLINES must go too, not just spaces/tabs/pipes (codex r2 P2). A lane id inherits
  # arbitrary worktree-name text, and an embedded newline would split ONE row across two
  # physical lines: the reducer then reads a malformed detail and can drop the gate
  # entirely -- a silently lost operator obligation, the worst failure this ledger has.
  # \r is stripped for the same reason (a lone CR corrupts the row for line-oriented awk).
  # `;` goes too (codex r4 P2): rowparse terminates the lane at the FIRST semicolon, so a
  # lane id containing one would be silently truncated at read time -- two distinct lanes
  # could then render as the same id, and neither would match its persisted spelling.
  # `[` and `]` go too (codex r7 P2): pending rows are RENDERED as `[<lane>] <detail>`, and
  # every consumer that reads that form back -- the migration's own re-import parse among
  # them -- delimits on the brackets. A lane carrying one would make the bracketed prefix
  # bleed into the detail, losing the leading item token and with it the whole gate.
  lane=$(printf '%s' "${1:--}" | tr -d ' \t\n\r|;[]'); cause=$(printf '%s' "${2:--}" | tr -d ' \t\n\r|;[]')
  printf 'lane=%s;cause=%s' "${lane:--}" "${cause:--}"
}

# Escape pipes + collapse newlines so one logical row stays one table row. Shared by the
# writer and by loop_resolve, which must reproduce the exact bytes it wrote.
_loop_escape_detail() { printf '%s' "$*" | tr '\n' ' ' | sed 's/|/\\|/g'; }

# This lane's id for attribution purposes (C-HE-09 §3), or `-` when there is none.
# HARNESS_LANE_ID first, then the worktree-local PERSISTED marker (codex r4 P2). The env var
# alone is not enough: the canonical deferral wrapper `tools/04-loop/defer.sh` and the
# ordinary hooks never export it, so every row they wrote landed unattributed as `-` even in
# a worktree that has had a lane id on disk the whole time -- losing exactly the attribution
# §3 requires, and the attribution the arc-exit report reads.
_loop_lane_id() {
  local l="${HARNESS_LANE_ID:-}"
  if [ -z "$l" ]; then
    local d; d=$(hook_project_dir 2>/dev/null)
    [ -n "$d" ] && [ -f "$d/.harness/.lane-id" ] && l=$(cat "$d/.harness/.lane-id" 2>/dev/null)
  fi
  printf '%s' "${l:--}"
}

# Append a ledger row. Usage: loop_log <kind> <detail...>
# kind is a short uppercase token (ACTIVATE / DEACTIVATE / DEFERRED-HIL / RESOLVED-HIL /
# NOTIFY / COALESCE-DELIVERED / COMPLETED / DENY / RESOLVE-SPLIT / RESUME). detail is free
# text. The lane / cause_signature carried in the structured column come from the ambient
# HARNESS_LANE_ID / LOOP_CAUSE (`-` when unset) -- callers that know them explicitly should
# use loop_log_structured. Always exits 0: this is the HOOK contract (a ledger write must
# never break the calling hook), which is exactly why coordination callers must NOT use it.
loop_log() {
  local kind="$1"; shift
  loop_log_structured "$kind" "$(_loop_lane_id)" "${LOOP_CAUSE:--}" "$@" || true
  return 0
}

# The single ledger writer. Usage: loop_log_structured <kind> <lane_id> <cause> <detail...>
# Row shape (C-HE-09 §3): | ts | kind | lane=<lane_id>;cause=<cause|-> | detail |
# The structured column goes BEFORE detail deliberately: _loop_pending_hil_rows rejoins
# $start..NF-1 to restore escaped pipes, so ANY column appended after detail would be
# glued into the rendered reason (C7 verified this against a trailing-column draft).
# Returns 1 when the shared ledger cannot be written -- coordination callers
# (reservations.py, merge_door.py via emit_loop_row) MUST propagate: an unrecorded
# DEFERRED-HIL / NOTIFY is a lost operator recovery signal, not a cosmetic miss. Legacy
# hook callers go through loop_log above, which keeps its always-0 contract.
loop_log_structured() {
  local kind="$1" lane="$2" cause="$3"; shift 3
  local p; p=$(loop_status_ensure)
  [ -z "$p" ] && { echo "loop_log_structured: no ledger venue" >&2; return 1; }
  if ! printf '| %s | %s | %s | %s |\n' \
      "$(loop_now)" "$kind" "$(_loop_structured_col "$lane" "$cause")" "$(_loop_escape_detail "$@")" \
      >> "$p" 2>/dev/null; then
    echo "loop_log_structured: cannot write $p" >&2; return 1
  fi
  return 0
}

# ── Shared AWK preludes ───────────────────────────────────────────────────────
# ONE row parser for every reducer below. A second copy would be free to drift on the
# structured-vs-legacy detection, the escaped-pipe rejoin, or the item-token split -- the
# exact three rules the ledger's correctness rests on.
#
# rowparse() sets, for the current line:
#   k    -- the kind column ($3, trimmed). Matching the COLUMN (never a whole-row regex)
#           is what stops a reason CONTAINING the word "DEFERRED-HIL" from forging a row.
#   lane -- the lane id from the structured column, or "-" for a legacy 3-column row.
#   d    -- the detail, rejoined from $start..NF-1 with escaped pipes preserved.
#   tok  -- detail's LEADING whitespace token = the item id. Scanning the whole detail
#           would wrongly match an item merely MENTIONED in a reason.
_LOOP_AWK_ROW='
  function rowparse(   i, start) {
    k = $3; gsub(/^[ \t]+|[ \t]+$/, "", k)
    if ($4 ~ /^[ \t]*lane=/) { lane = $4; sub(/^[ \t]*lane=/, "", lane); sub(/;.*$/, "", lane); gsub(/^[ \t]+|[ \t]+$/, "", lane); start = 5 }
    else { lane = "-"; start = 4 }
    d = $start; for (i = start + 1; i < NF; i++) d = d "|" $i
    sub(/^[ \t]+/, "", d); sub(/[ \t]+$/, "", d)
    split(d, _a, /[ \t]/); tok = _a[1]
  }'

# epoch(ts): `YYYY-MM-DDTHH:MM:SSZ` -> seconds, or -1 if unparseable. Pure awk (Hinnant
# days-from-civil) so no `date` fork happens per row and macOS/Linux behave identically.
_LOOP_AWK_EPOCH='
  function dfc(y, m, d,   era, yoe, doy, doe) {
    if (m <= 2) y -= 1
    era = int((y >= 0 ? y : y - 399) / 400); yoe = y - era * 400
    doy = int((153 * (m + (m > 2 ? -3 : 9)) + 2) / 5) + d - 1
    doe = yoe * 365 + int(yoe / 4) - int(yoe / 100) + doy
    return era * 146097 + doe - 719468
  }
  function epoch(ts) {
    gsub(/^[ \t]+|[ \t]+$/, "", ts)
    if (ts !~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z$/) return -1
    return dfc(substr(ts,1,4)+0, substr(ts,6,2)+0, substr(ts,9,2)+0) * 86400 \
           + substr(ts,12,2)*3600 + substr(ts,15,2)*60 + substr(ts,18,2)
  }'

# Log a per-item deferral (the "worked AROUND a gate" disposition). The loop is designed
# to NEVER halt the whole run at a single gated item: it builds whatever slice does not
# need the gated input, records the deferral here with the item-ID as the leading token,
# and ADVANCES to the next forward item. `.loop-halt` is reserved for true exhaustion
# (every forward item deferred) or an operator stop — NOT a single gate.
# Usage: loop_defer <item-id> <what operator input is needed [+ what was built without it]>
loop_defer() {
  local item="$1"; shift
  loop_log DEFERRED-HIL "${item} — $*"
}

# Log that a previously-deferred item's gate was subsequently answered (ratified,
# selected, decided) OUTSIDE the append-only DEFERRED-HIL row itself — e.g. via a later
# council/dyad ratification or operator AskUserQuestion that this ledger never witnessed
# directly. Without this, loop_skip_set/loop_pending_hil_summary have no way to represent
# "resolved" and the SessionStart hook nags about an already-answered gate forever (until
# the next ACTIVATE row happens to reset the window by accident).
# Usage: loop_resolve <item-id> <how it was resolved + evidence pointer>
loop_resolve() {
  local item="$1"; shift
  local note="$*"
  # Byte offset BEFORE our append, so the verification below can look at our own write
  # rather than the whole shared history (see the tail -c note there). A missing/unreadable
  # venue gives 0, which degrades to the old whole-file search rather than failing here.
  local _before; _before=$(wc -c < "$(loop_status_path)" 2>/dev/null | tr -d ' ') || _before=0
  [ -n "$_before" ] || _before=0
  loop_log RESOLVED-HIL "${item} — ${note}"
  # loop_log ALWAYS exits 0 by design (a ledger write must never break the calling hook),
  # so an unwritable ledger would otherwise make this report success while the item stays
  # pending. Verify the EFFECT rather than trust loop_log's return — but verify OWN write
  # landed (grep the file for the exact row just appended), NOT recomputed global
  # skip-set membership. The latter was this function's first cut and is an unsound
  # check-then-act race against concurrent writers with no locking anywhere in this
  # library: a concurrent loop_defer/loop_resolve for the SAME item-id landing between
  # our write and our loop_skip_set read can flip the derived answer in EITHER direction
  # (merge-gate concurrency lens on this arc: own write succeeds but a concurrent
  # re-DEFERRED-HIL makes it look still-pending; or own write fails but a concurrent
  # process's resolve of the same item makes it look cleared). Checking for the specific
  # row we just wrote is monotonic — nothing in this codebase ever deletes a ledger row —
  # so it is unaffected by any OTHER process's concurrent activity.
  local p; p=$(loop_status_path)
  [ -n "$p" ] || return 1
  # Rebuild the EXACT row loop_log just wrote -- same column builder, same escaper, so the
  # structured column can never drift between the write and this check (C-HE-09 §3).
  local col escaped
  col=$(_loop_structured_col "$(_loop_lane_id)" "${LOOP_CAUSE:--}")
  escaped=$(_loop_escape_detail "${item} — ${note}")
  # Search ONLY the bytes appended since our own write began (codex r3 P2). Scanning the
  # whole file proves a matching row EXISTS, not that THIS call wrote one: on a shared,
  # cross-run, never-truncated venue an identical RESOLVED-HIL row from a previous run is
  # entirely plausible, and if the item was re-deferred since and our append then failed,
  # the whole-file grep would find that stale row and report success while the reducer
  # still (correctly) sees the item as pending -- a false "resolved" is the one answer this
  # function must never give. `$_before` is captured by the caller before loop_log runs.
  tail -c "+$(( ${_before:-0} + 1 ))" "$p" 2>/dev/null \
    | grep -qF "| RESOLVED-HIL | ${col} | ${escaped} |"
}

# The SKIP-SET: every item-ID with an open deferral across ALL lanes, i.e. deferred and not
# subsequently RESOLVED. This is the mechanical anti-re-loop guard — `stop-loop.sh` injects it so a
# fresh headless `claude -p` child (no memory of prior turns) does not re-attempt an item
# a prior turn already deferred against the single static dashboard pointer. Echoes
# space-separated item-IDs (unique), empty if none. The persistent ledger IS the
# cross-context memory.
loop_skip_set() {
  local p; p=$(loop_status_path)
  [ -f "$p" ] || return 0
  # The item key is rowparse()'s leading detail token (see _LOOP_AWK_ROW): scanning the
  # whole detail would wrongly match an item merely MENTIONED in a reason, e.g.
  # `loop_defer R-410 "blocked until R-300 decides"` must key on R-410 only, never R-300.
  # Accept BOTH canonical item-ID families: `R-*` (roadmap register, Project_Roadmap_v1.md)
  # and `B-*` (forward-register, .harness/forward-register.yaml) — a filter scoped to `R-`
  # alone silently dropped every real-world B-* deferral (codex [P2] round 2 on this arc;
  # e.g. the live `B-48-EXECUTOR-SELECTION` row was never actually in the skip-set).
  # Per-token LAST-WRITE-WINS across ALL lanes: a later RESOLVED-HIL row clears a prior
  # DEFERRED-HIL for the same item; a later re-DEFERRED-HIL row re-flags it. There is NO
  # ACTIVATE reset (C-HE-09 §4, option b): with one shared venue, honouring a lane's
  # ACTIVATE here would drop another lane's still-open deferral and the loop would
  # re-attempt a gated item. Over-skipping is safe; under-skipping re-loops.
  # NOTIFY / COALESCE-DELIVERED are informational kinds and never reach `state`.
  awk -F'|' "$_LOOP_AWK_ROW"'
    { rowparse() }
    k == "DEFERRED-HIL" || k == "RESOLVED-HIL" {
      state[tok] = (k == "DEFERRED-HIL") ? "PENDING" : "RESOLVED"
    }
    END { for (t in state) if (state[t] == "PENDING") print t }
  ' "$p" 2>/dev/null | grep -E '^(R|B)-[A-Za-z0-9._-]+$' | sort -u | tr '\n' ' ' | sed 's/ $//'
}

# THE ledger parse for still-PENDING deferrals — one line per pending item, carrying its
# FULL "<item-id> — <reason>" detail, sorted by item-id for a deterministic order. Private:
# both public consumers below (the bounded operator summary and the structured list) share
# this single extraction so the last-write-wins rule, the run-boundary reset and the
# leading-token keying can never diverge between them.
_loop_pending_hil_rows() {
  local p; p=$(loop_status_path)
  [ -f "$p" ] || return 0
  # awk runs FIRST, alone, so its exit status is preserved — a pipeline would return
  # sort's status and make an unreadable ledger indistinguishable from an empty one
  # (codex: the report must never render an UNKNOWN list as []). rowparse() rejoins the
  # detail across escaped pipes (loop_log_structured writes them as `\|`, which -F'|'
  # still splits) and the final sed unescapes them. Each item is rendered `[<lane_id>]
  # <detail>` (C-HE-09 §3) so an operator reading one shared ledger can tell WHICH lane
  # is gated; legacy 3-column rows render `[-]`. No ACTIVATE reset (§4) — same rule as
  # loop_skip_set, which is why they share this one extraction.
  local out
  out=$(awk -F'|' "$_LOOP_AWK_ROW"'
    { rowparse() }
    k == "DEFERRED-HIL" || k == "RESOLVED-HIL" {
      if (k == "DEFERRED-HIL") { state[tok] = "PENDING"; detail[tok] = "[" lane "] " d }
      else { state[tok] = "RESOLVED" }
    }
    END { for (t in state) if (state[t] == "PENDING") print detail[t] }
  ' "$p" 2>/dev/null) || return 1
  printf '%s\n' "$out" | sed 's/[ \t]*$//; s/\\|/|/g' | grep -v '^$' | sort
  return 0
}

# Structured sibling of loop_pending_hil_summary (U-WT-03): EVERY pending deferral, one
# full untruncated row each, nothing elided. The summary below is deliberately bounded to
# 3 details + a "+N more" tail for SessionStart context economy, which makes it unable to
# faithfully populate a machine-readable list — so `tools/arc_exit_report.py` consumes this
# instead for the exit report's `todo_for_human[]`. Same parse, different presentation:
# a second parser would be a second authority free to drift.
loop_pending_hil_list() {
  _loop_pending_hil_rows
}

# Generic "top-3 + (+N more)" cap (U-CTX-08): given a newline-separated list of items on
# stdin, echo them joined "; ", bounded to the first 3, with a "(+N more)" tail when the
# list is longer. Extracted from loop_pending_hil_summary below so every SessionStart-
# context list this hook family renders (pending HIL items, stale worktrees, ...) shares
# ONE cap implementation instead of re-deriving the "head -3 / N-3 more" arithmetic per
# caller — a second copy would be free to drift on the boundary (item #3 vs #4, off-by-
# one on the "more" count). Silent on an empty list (no items ⇒ no output, no "(+0 more)").
# Usage: CAP=$(printf '%s\n' "$rows" | loop_cap_list)
loop_cap_list() {
  local rows; rows=$(cat)
  [ -z "$rows" ] && return 0
  local n; n=$(printf '%s\n' "$rows" | grep -c .)
  local head3; head3=$(printf '%s\n' "$rows" | head -3 | paste -sd';' - | sed 's/;/; /g')
  local more=""; [ "$n" -gt 3 ] && more=" (+$((n-3)) more)"
  printf '%s%s' "$head3" "$more"
}

# Operator-facing summary of the LAST run's still-PENDING deferrals (a RESOLVED-HIL row
# clears an item per the same last-write-wins rule as loop_skip_set), for SessionStart
# surfacing ("clearly presented when they engage next"). Compact one line; empty when
# there are none. Lists up to 3 items + a "+N more" tail so the SessionStart context
# stays bounded (via loop_cap_list above). Item order is item-ID-sorted (the shared
# extraction sorts), so which 3 items head the summary is deterministic rather than
# awk-iteration-order dependent.
loop_pending_hil_summary() {
  local rows n
  rows=$(_loop_pending_hil_rows)
  [ -z "$rows" ] && return 0
  n=$(printf '%s\n' "$rows" | grep -c .)
  local cap; cap=$(printf '%s\n' "$rows" | loop_cap_list)
  printf '[loop] ⏸ %s item(s) await your input from the last loop run: %s. See %s' "$n" "$cap" "$(loop_status_path)"
}

# NOTIFY rows (C-HE-09 §5): append-only informational signals -- an aged reservation, a
# blocked lease tier, a RAM shortfall, a demoted reviewer. Rendered at SessionStart
# BESIDE the DEFERRED-HIL summary, never merged into it, and never in the skip-set: a
# NOTIFY is "you may want to know", not "the loop is gated on you". Newest 5 within the
# horizon (default 24 h, matching the C-HE-20 TTL that generates most of them), one line,
# each carrying its emitting lane. Empty when there is nothing recent. Always exits 0.
loop_notify_summary() {
  local p; p=$(loop_status_path); [ -f "$p" ] || return 0
  local rows
  rows=$(awk -F'|' -v now_ts="$(loop_now)" -v horizon="${HARNESS_NOTIFY_HORIZON_S:-86400}" \
    "$_LOOP_AWK_EPOCH$_LOOP_AWK_ROW"'
    BEGIN { now = epoch(now_ts) }
    { rowparse() }
    k == "NOTIFY" {
      ts = epoch($2)
      # An unparseable now/ts is not evidence of recency -- drop the row rather than
      # render a notice whose age is unknown.
      if (now < 0 || ts < 0 || now - ts > horizon) next
      print "[" lane "] " d
    }' "$p" 2>/dev/null | tail -5 | sed 's/\\|/|/g')
  [ -n "$rows" ] && printf '[loop] ℹ notify: %s' "$(printf '%s\n' "$rows" | paste -sd';' - | sed 's/;/; /g')"
  return 0
}

# C-HE-20: TTL is a NOTIFICATION threshold. Re-surface pending deferrals older than
# HARNESS_HIL_TTL_S (default 24h) as NOTIFY rows -- at most once per TTL window per item.
# This function MUST NOT resolve, reclaim, release, or transition anything (D8): it reads the
# ledger and appends NOTIFY rows, nothing else. Called once per SessionStart
# (tools/roadmap-audit/session-start.sh). Timestamps are parsed in pure awk (days-from-civil)
# so no `date` fork happens per row and macOS/Linux behave identically. Shape-aware for the
# structured column U-HE-29 introduces (`$4 ~ /^lane=/` -> detail is `$5`).
# Row written: `| <ts> | NOTIFY | ttl-expired <item> — pending > <ttl>s; re-surfaced, state unchanged |`
# The eligibility read and the NOTIFY append are ONE critical section under a kernel flock on
# `.harness/.loop-status.lock` (fd 8; the lib.sh worktree-mutex pattern) -- concurrent
# SessionStart hooks would otherwise each read "no NOTIFY yet" and all append (codex round 3:
# 20 hooks -> 20 notifications). The lock is released on process death; a lock that cannot be
# taken within the bounded wait skips this session's re-surface (a notification only -- nothing
# is lost; the next SessionStart retries).
loop_hil_ttl_resurface() {
  local p ttl now lock rc; p=$(loop_status_path); [ -f "$p" ] || return 0
  ttl="${HARNESS_HIL_TTL_S:-86400}"; now=$(loop_now)
  lock="$(dirname "$p")/.loop-status.lock"
  exec 8>> "$lock" 2>/dev/null || return 0
  if ! /usr/bin/python3 - 8 "${HARNESS_LOOP_STATUS_LOCK_TIMEOUT_SECONDS:-10}" <<'PY'
import fcntl, sys, time
fd = int(sys.argv[1]); deadline = time.monotonic() + float(sys.argv[2])
while True:
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); break
    except BlockingIOError:
        if time.monotonic() >= deadline:
            raise SystemExit(1)
        time.sleep(0.05)
PY
  then
    exec 8>&-; return 0
  fi
  _loop_hil_ttl_resurface_unlocked "$p" "$ttl" "$now"; rc=$?
  exec 8>&-
  return $rc
}

_loop_hil_ttl_resurface_unlocked() {
  local p="$1" ttl="$2" now="$3"
  # Shares the ONE row parser + epoch helper with every other reducer (see the preludes
  # above): the structured-vs-legacy detection and the item-token split must be identical
  # here or an aged deferral would be keyed differently than the skip-set keys it. No
  # ACTIVATE reset (C-HE-09 §4) -- honouring one here would let a sibling lane's ACTIVATE
  # silence another lane's aged deferral, which is precisely the notification the TTL exists
  # to deliver.
  awk -F'|' -v now_ts="$now" -v ttl="$ttl" "$_LOOP_AWK_EPOCH$_LOOP_AWK_ROW"'
    BEGIN { now = epoch(now_ts) }
    { rowparse() }
    k == "DEFERRED-HIL" || k == "RESOLVED-HIL" {
      if (k == "DEFERRED-HIL") { state[tok] = "PENDING"; at[tok] = epoch($2) } else { state[tok] = "RESOLVED" }
    }
    k == "NOTIFY" { split(d, b, /[ \t]+/); if (b[1] == "ttl-expired") last[b[2]] = epoch($2) }
    END {
      if (now < 0) exit 0
      for (t in state) {
        if (state[t] != "PENDING" || at[t] < 0) continue
        if (now - at[t] < ttl) continue
        if ((t in last) && now - last[t] < ttl) continue
        print t
      }
    }
  ' "$p" 2>/dev/null | sort | while IFS= read -r item; do
    [ -n "$item" ] && loop_log NOTIFY "ttl-expired ${item} — pending > ${ttl}s; re-surfaced, state unchanged"
  done
  return 0
}

# Turn loop mode ON: create the marker + log the activation. Usage: loop_activate [reason]
loop_activate() {
  local mp; mp=$(loop_marker_path)
  [ -z "$mp" ] && return 1
  mkdir -p "$(dirname "$mp")" 2>/dev/null
  : > "$mp" 2>/dev/null || return 1
  # Fresh run: clear any stale iteration counter / halt marker from a prior run.
  rm -f "$(loop_iter_path)" "$(loop_halt_path)" 2>/dev/null
  loop_log ACTIVATE "${1:-loop mode on}"
  # NOTE: worktree GC is intentionally NOT called here. `tools/04-loop/run.sh` installs its
  # `.loop-active`-cleanup EXIT/INT/TERM trap only AFTER loop_activate returns, so a slow
  # gh/GC step here would open a pre-trap interruption window that could leave loop mode
  # armed on Ctrl-C (codex P2). SessionStart only reports candidates; explicit
  # post-merge/closeout worktree disposition performs the removal after the runner trap
  # is installed and no active session owns the candidate.
}

# Turn loop mode OFF: remove the marker + log the deactivation. Usage: loop_deactivate [reason]
# Note: HARNESS_LOOP=1 in the environment still forces loop mode on even after this
# (env wins); deactivate clears the file marker only.
loop_deactivate() {
  local mp; mp=$(loop_marker_path)
  [ -z "$mp" ] && return 1
  rm -f "$mp" "$(loop_iter_path)" "$(loop_halt_path)" 2>/dev/null
  loop_log DEACTIVATE "${1:-loop mode off}"
}

# ── Worktree garbage collection (U-HK-26) ─────────────────────────────────────
# The autonomous loop ships PRs whose worktrees go stale after merge, and nothing
# reaps them (git-arc-guard checks commits/branches; session-end-cleanup is
# advisory-only; a hook can't remove the worktree it runs INSIDE). SessionStart reports
# candidates; explicit post-merge/closeout disposition calls loop_gc_worktrees reap.
#
# WORKTREES ONLY — never `git branch -d/-D`. `git worktree remove` on a clean tree is
# REVERSIBLE (branch + commits persist; `git worktree add` re-creates it); a merged
# branch ref is ~41 harmless bytes; and the irreversible force-delete that squash-merge
# would require (`-D`, because `git branch -d` does not recognize squash-merged work)
# is left to the operator via the advisory report.

# gh-availability probe: 0 iff `gh` can list merged PRs (installed + authed + reachable).
# A single upfront probe lets the GC distinguish "gh down → do nothing (fail-safe)" from
# per-branch "this branch is genuinely unmerged", and avoids N futile queries when offline.
# Runs gh INSIDE the repo dir ($1) — `gh` infers the repo from cwd, and the hook's cwd is
# not guaranteed to be the project root (codex P2 + [[bash-cwd-reverts-to-project-root]]).
_loop_gc_gh_ok() {
  command -v gh >/dev/null 2>&1 || return 1
  ( cd "$1" 2>/dev/null || exit 1
    hook_bounded 6 gh pr list --state merged --limit 1 --json number >/dev/null 2>&1 )
}

# The exact merged head SHA for ONE branch (empty if the branch has no merged PR).
# Queried PER-BRANCH via `--head` rather than a bounded recent list, so an OLD stale
# worktree whose PR is beyond the latest N merges is still found (codex P2). headRefOid
# is the pre-squash head SHA → an exact-SHA match is both precise and squash-merge-safe.
# Args: <branch> <repo_dir>. Runs gh inside <repo_dir> so the lookup targets THIS repo,
# not the caller's cwd (codex P2). Isolated so tests can stub it.
_loop_gc_merged_oid() {
  ( cd "$2" 2>/dev/null || exit 0
    hook_bounded 6 gh pr list --state merged --head "$1" --limit 5 --json headRefOid \
      --jq '.[0].headRefOid // empty' 2>/dev/null )
}

# Echo a worktree's reap-BLOCKING local state (empty = safe to reap). `--ignored`
# surfaces precious ignored entries that `git worktree remove` would delete. The
# canonical filter lives in lib.sh and is re-run under the removal mutex.
_loop_gc_local_state() {
  hook_worktree_local_state "$1"
}

# Decide the disposition of ONE worktree and act per MODE.
# Args: <path> <branch> <current_toplevel> <default_branch> <mode> <root>
#   mode=reap   → mutex-backed worktree removal + log to the ledger (loop mode).
#   mode=report → echo "<path> (<branch>)" for a reapable candidate (HIL, read-only).
# Safe-subset gate (ALL must hold): not the current worktree; has a branch (not
# detached); not the default branch; branch's PR merged at the worktree's exact HEAD
# SHA; clean working tree (ignored-aware).
_loop_gc_consider() {
  local path="$1" branch="$2" current="$3" default="$4" mode="$5" root="$6"
  [ -n "$path" ] || return 0
  # Canonicalize the candidate the same way as `current` before the self-exclude compare
  # (codex P2). git ops below use the ORIGINAL $path (as git recorded it).
  local cpath; cpath=$(cd "$path" 2>/dev/null && pwd -P || printf '%s' "$path")
  [ "$cpath" = "$current" ] && return 0                      # never the current worktree
  [ -n "$branch" ] || return 0                               # detached HEAD → skip
  [ "$branch" = "$default" ] && return 0                     # never the default branch
  # Branch must be merged AND the worktree HEAD must equal the EXACT SHA that was merged.
  # Name-only matching would reap a reused/renamed clean branch whose new commits were
  # never merged (codex P2). headRefOid ties identity to the merged commit; squash-safe.
  local want_oid; want_oid=$(_loop_gc_merged_oid "$branch" "$root")
  [ -n "$want_oid" ] || return 0                             # branch has no merged PR → skip
  local head_oid; head_oid=$(git -C "$path" rev-parse HEAD 2>/dev/null)
  if [ "$head_oid" != "$want_oid" ]; then                    # local branch advanced/reused → not this PR
    [ "$mode" = "reap" ] && loop_log GC "skipped $path ($branch) — HEAD ${head_oid:0:8} != merged ${want_oid:0:8} (name collision/reuse)"
    return 0
  fi
  local residue local_state_rc
  residue=$(_loop_gc_local_state "$path")                    # dirty / untracked / precious-ignored
  local_state_rc=$?
  case "$local_state_rc" in
    0)
      [ "$mode" = "reap" ] && loop_log GC "skipped $path ($branch) — has local state: $(printf '%s' "$residue" | tr '\n' ',' | sed 's/^,//;s/,$//' | cut -c1-160)"
      return 0
      ;;
    1) ;;
    *)
      [ "$mode" = "reap" ] && loop_log GC "skipped $path ($branch) — local state unavailable"
      return 0
      ;;
  esac
  if [ "$mode" = "report" ]; then
    worktree_has_live_session "$cpath" && return 0
    printf '%s (%s)\n' "$path" "$branch"
    return 0
  fi
  hook_safe_worktree_remove "$root" "$path" "$branch" "$head_oid" 2>/dev/null
  local remove_rc=$?
  case "$remove_rc" in
    0) loop_log GC "reaped worktree $path (branch $branch merged+clean; branch ref left for operator)" ;;
    3) loop_log GC "skipped $path ($branch) — live Claude/Codex session" ;;
    2) loop_log GC "skipped $path ($branch) — session/removal mutex unavailable" ;;
    4) loop_log GC "skipped $path ($branch) — local state appeared before removal" ;;
    5) loop_log GC "skipped $path ($branch) — local state unavailable under removal mutex" ;;
    6) loop_log GC "skipped $path ($branch) — quarantined worktree restore failed" ;;
    7) loop_log GC "skipped $path ($branch) — process retains a reference into the worktree" ;;
    8) loop_log GC "restored interrupted quarantine for $path ($branch); retry deferred" ;;
    9) loop_log GC "skipped $path ($branch) — process-reference state unavailable" ;;
    10) loop_log GC "skipped $path ($branch) — branch or HEAD changed after classification" ;;
    *) loop_log GC "skipped $path ($branch) — git worktree remove refused (locked/untracked)" ;;
  esac
}

# Garbage-collect stale worktrees only when invoked explicitly after merge/closeout.
# WORKTREES ONLY; fail-safe to zero removals when the merged set is unavailable.
# Deterministic bash (NOT a Claude tool call) → bypasses permission-guard; the
# safe-subset gate above is the backstop. Always returns 0.
#   mode=reap   (default) → remove + log each disposition.
#   mode=report           → echo "<path> (<branch>)" per reapable candidate (read-only).
# Usage: loop_gc_worktrees [reap|report]
loop_gc_worktrees() {
  local mode="${1:-reap}"
  command -v git >/dev/null 2>&1 || return 0
  local root; root=$(hook_project_dir); [ -n "$root" ] || return 0
  # Fail-safe: if gh can't reach the API (offline/unauth), do nothing rather than treat
  # every branch as unmerged-vs-merged ambiguously. One upfront probe, not N.
  if ! _loop_gc_gh_ok "$root"; then
    [ "$mode" = "reap" ] && loop_log GC "skipped — gh unavailable (offline/unauth/not-installed); zero removals"
    return 0
  fi
  local current default
  current=$(git -C "$root" rev-parse --show-toplevel 2>/dev/null)
  # Canonicalize to a physical path so self-exclusion can't be defeated by a symlink /
  # /var-vs-/private/var spelling difference between rev-parse and `worktree list`
  # (codex P2: a mismatch would let the CURRENT worktree be reaped).
  current=$(cd "$current" 2>/dev/null && pwd -P || printf '%s' "$current")
  default=$(hook_default_branch)
  local path="" branch=""
  while IFS= read -r line; do
    case "$line" in
      "worktree "*) path="${line#worktree }" ;;
      "branch refs/heads/"*) branch="${line#branch refs/heads/}" ;;
      "") _loop_gc_consider "$path" "$branch" "$current" "$default" "$mode" "$root"; path=""; branch="" ;;
    esac
  done < <(git -C "$root" worktree list --porcelain 2>/dev/null)
  # Trailing record safety-net (porcelain normally ends with a blank line).
  [ -n "$path" ] && _loop_gc_consider "$path" "$branch" "$current" "$default" "$mode" "$root"
  return 0
}

# ── Remote branch close-out (post-merge, per-arc) ──────────────────────────
# SCOPE (operator correction, 2026-07-15): the actual discipline is "delete
# THIS arc's own remote branch on GitHub right after its merge commit's
# post-merge CI on <default> is confirmed green" — not a local-ref scanning
# GC engine. An earlier version built a full local-branch-backlog scanner
# (bulk merged-PR index, per-branch CAS local delete, checked-out-worktree
# guard) cross-referenced against `git branch` — which reports on STALE
# LOCAL refs whose GitHub-side branch may already be long gone, producing
# misleading "N branches held" output entirely disconnected from the actual
# remote state (`.harness/post-phase-8-forward-register.md` and the
# session-level correction record it). Removed. The discipline operates on
# the REMOTE (GitHub) branch, is always a single named branch (the one just
# merged — no scanning/backlog concept applies), and is documented as a
# direct recipe in the `ship-pr` skill: verify CI green on the merge commit,
# then a LEASE-GUARDED `git push --force-with-lease=refs/heads/<branch>:<merged-oid>
# origin :refs/heads/<branch>` (never a bare `gh api -X DELETE`/`git push --delete`,
# which has no CAS guard and would silently destroy any new work pushed to the
# same branch name post-merge). Local branch refs are left alone entirely —
# they carry no unique value once merged (git reflog covers recovery for ~90
# days regardless) and are not what "branch hygiene" refers to in this
# workspace's discipline.

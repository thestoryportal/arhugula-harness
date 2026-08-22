#!/usr/bin/env bash
# Hermetic test for loop_lib.sh (U-HK-11). Exercises the marker toggle + ledger API
# against a throwaway project dir. Asserts: off by default, activate/deactivate flip
# loop_mode_active, ledger auto-creates with header, rows append + pipes escape, and
# HARNESS_LOOP=1 forces on regardless of the marker.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
mkdir -p "$REPO/.harness" "$REPO/shared"

# Source the libs against the fake project dir (lib.sh first, then loop_lib.sh).
export CLAUDE_PROJECT_DIR="$REPO"
# C-HE-09 §2: the ledger is a SHARED venue outside every worktree, so it is no longer
# reachable as "$CLAUDE_PROJECT_DIR/.harness/loop_status.md". Pin it hermetically here;
# every assertion below addresses it through loop_status_path().
export HARNESS_LOOP_STATUS_PATH="$REPO/shared/loop_status.md"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
# shellcheck source=loop_lib.sh
. "$SCRIPT_DIR/loop_lib.sh"

# 1) Off by default (no marker, no env).
unset HARNESS_LOOP
loop_mode_active && bad "loop active with no marker/env" || ok "off by default"

# 2) Paths resolve under the fake project dir.
[ "$(loop_marker_path)" = "$REPO/.harness/.loop-active" ] && ok "marker path correct" || bad "marker path: $(loop_marker_path)"
[ "$(loop_status_path)" = "$HARNESS_LOOP_STATUS_PATH" ] && ok "status path correct" || bad "status path: $(loop_status_path)"

# 3) activate → marker exists + loop_mode_active true + ledger created with header + ACTIVATE row.
loop_activate "test on"
[ -f "$REPO/.harness/.loop-active" ] && ok "activate creates marker" || bad "marker not created"
loop_mode_active && ok "loop_mode_active true after activate" || bad "still off after activate"
[ -f "$(loop_status_path)" ] && ok "ledger auto-created" || bad "ledger missing"
grep -q '^# Loop status ledger' "$(loop_status_path)" && ok "ledger has header" || bad "no header"
grep -q '| ACTIVATE | lane=-;cause=- | test on |' "$(loop_status_path)" && ok "ACTIVATE row appended" || bad "no ACTIVATE row"

# 4) loop_log appends a row; pipes in detail are escaped (one table row stays one row).
loop_log DEFERRED-HIL "needs ANTHROPIC_API_KEY | paid call"
grep -q '| DEFERRED-HIL | lane=-;cause=- | needs ANTHROPIC_API_KEY \\| paid call |' "$(loop_status_path)" \
  && ok "loop_log escapes pipes" || bad "pipe not escaped: $(grep DEFERRED "$(loop_status_path)")"

# 5) ledger is append-only (ensure does not clobber existing rows).
BEFORE=$(wc -l < "$(loop_status_path)")
loop_status_ensure >/dev/null
AFTER=$(wc -l < "$(loop_status_path)")
[ "$BEFORE" = "$AFTER" ] && ok "ensure is idempotent (no clobber)" || bad "ensure clobbered: $BEFORE -> $AFTER"

# 6) deactivate → marker gone + loop_mode_active false + DEACTIVATE row.
loop_deactivate "test off"
[ -f "$REPO/.harness/.loop-active" ] && bad "marker still present after deactivate" || ok "deactivate removes marker"
loop_mode_active && bad "still on after deactivate" || ok "off after deactivate"
grep -q '| DEACTIVATE | lane=-;cause=- | test off |' "$(loop_status_path)" && ok "DEACTIVATE row appended" || bad "no DEACTIVATE row"

# 7) HARNESS_LOOP=1 forces loop mode on even with no marker.
HARNESS_LOOP=1 loop_mode_active && ok "HARNESS_LOOP=1 forces on" || bad "env override failed"

# 8) loop_defer writes a parseable DEFERRED-HIL row with the item-id as the leading token.
: > "$(loop_status_path)"
loop_activate "skip-set test" >/dev/null
loop_defer R-410 "needs container runtime — built: design half"
grep -qE '\| DEFERRED-HIL \| lane=[^|]* \| R-410 — needs container' "$(loop_status_path)" && ok "loop_defer writes item-id-leading DEFERRED-HIL row" || bad "loop_defer row malformed"

# 9) loop_skip_set = sorted-unique item-ids deferred SINCE the last ACTIVATE.
loop_defer R-300 "needs OpenAI creds"
SKIP=$(loop_skip_set)
[ "$SKIP" = "R-300 R-410" ] && ok "loop_skip_set lists current-run deferrals ($SKIP)" || bad "skip_set wrong: [$SKIP]"

# 10) C-HE-09 §4 (option b): ACTIVATE is a PER-LANE control marker and MUST NOT reset
#     globally-visible HIL rows. The pre-U-HE-29 "since the last ACTIVATE" window is
#     struck: with one shared venue, lane B's ACTIVATE would otherwise hide lane A's open
#     deferral and the loop would re-attempt an item another lane is still gated on.
#     Over-skipping is safe; under-skipping re-loops (§4).
loop_activate "second run" >/dev/null
loop_defer R-815 "needs vendor pick"
SKIP=$(loop_skip_set)
[ "$SKIP" = "R-300 R-410 R-815" ] && ok "ACTIVATE does not reset the skip-set ($SKIP)" || bad "ACTIVATE reset HIL rows: [$SKIP]"

# 11) loop_pending_hil_summary: populated (with item + count) when deferrals exist.
SUM=$(loop_pending_hil_summary)
printf '%s' "$SUM" | grep -q "R-815" && printf '%s' "$SUM" | grep -q "await your input" \
  && ok "pending summary lists the deferral" || bad "pending summary missing/malformed: $SUM"
printf '%s' "$SUM" | grep -q '\[-\] R-300' && ok "summary renders [lane_id] per item (C-HE-09 §3)" || bad "no rendered [lane_id]: $SUM"

# 12) loop_pending_hil_summary empty when the current run has no deferrals.
: > "$(loop_status_path)"; loop_activate "clean run" >/dev/null
[ -z "$(loop_pending_hil_summary)" ] && ok "pending summary empty when no deferrals" || bad "pending summary not empty when clean"

# 13) skip-set extracts ONLY the leading item-id — an item merely MENTIONED in a reason
#     must NOT enter the skip-set (else the loop skips an item that was never deferred).
: > "$(loop_status_path)"; loop_activate "mention test" >/dev/null
loop_defer R-410 "blocked until R-300 vendor decision is made"
SKIP=$(loop_skip_set)
[ "$SKIP" = "R-410" ] && ok "skip-set = leading id only (R-300 in reason excluded)" || bad "over-matched reason id: [$SKIP]"

# 14) kind matched by COLUMN, not whole-row substring — a reason CONTAINING "ACTIVATE"
#     must not reset the run boundary and drop deferrals (would let the loop retry a gate).
: > "$(loop_status_path)"; loop_activate "kind-column test" >/dev/null
loop_defer R-410 "needs operator to ACTIVATE GitHub Pages"
loop_defer R-300 "needs creds"
SKIP=$(loop_skip_set)
[ "$SKIP" = "R-300 R-410" ] && ok "'ACTIVATE' in a reason does not drop deferrals ($SKIP)" || bad "kind whole-row match dropped a deferral: [$SKIP]"

# 14b) loop_skip_set accepts B-* item-IDs (forward-register), not just R-* (roadmap
#      register) — a filter scoped to R- alone silently drops every real-world B-*
#      deferral (codex [P2] round 2: the live ledger's B-48-EXECUTOR-SELECTION row was
#      never actually in the skip-set before this fix).
: > "$(loop_status_path)"; loop_activate "B-prefix test" >/dev/null
loop_defer B-48-EXECUTOR-SELECTION "operator selection of the B-48 executor design"
loop_defer R-410 "needs container runtime"
SKIP=$(loop_skip_set)
[ "$SKIP" = "B-48-EXECUTOR-SELECTION R-410" ] && ok "skip-set admits B-* alongside R-* ($SKIP)" || bad "B-* item dropped from skip-set: [$SKIP]"

# 15) loop_resolve clears a matching item from BOTH loop_skip_set and
#     loop_pending_hil_summary — an item whose gate was later answered must not nag
#     forever just because loop mode never re-ACTIVATEd.
: > "$(loop_status_path)"; loop_activate "resolve test" >/dev/null
loop_defer R-410 "needs container runtime"
loop_defer R-300 "needs OpenAI creds"
loop_resolve R-410 "ratified via council dyad, PR #1234"
RC=$?
[ "$RC" -eq 0 ] && ok "loop_resolve returns 0 on a verified write" || bad "loop_resolve returned $RC on a verified write"
SKIP=$(loop_skip_set)
[ "$SKIP" = "R-300" ] && ok "loop_resolve clears item from skip-set ($SKIP)" || bad "resolve did not clear skip-set: [$SKIP]"
SUM=$(loop_pending_hil_summary)
printf '%s' "$SUM" | grep -q "R-410" && bad "resolved item still in pending summary: $SUM" \
  || ok "loop_resolve clears item from pending summary"
printf '%s' "$SUM" | grep -q "R-300" && ok "unresolved item still in pending summary" || bad "unresolved item dropped: $SUM"

# 15b) loop_resolve returns FAILURE (not false success) when the ledger write doesn't
#      take effect — codex [P2] round 5: loop_log always exits 0 by design, so a write
#      failure must be caught by verifying the EFFECT, not the return code, in the
#      underlying function itself (this defect previously lived only in the now-removed
#      resolve.sh wrapper's own check — moving loop_resolve's write path here without
#      also moving that verification was the regression this test pins).
loop_defer R-888 "needs infra"
chmod 0444 "$(loop_status_path)"
loop_resolve R-888 "ratified" 2>/dev/null
RC=$?
chmod 0644 "$(loop_status_path)"
[ "$RC" -ne 0 ] && ok "loop_resolve returns nonzero when the ledger write does not take effect" || bad "loop_resolve returned 0 despite a failed write"
SKIP=$(loop_skip_set)
printf '%s' "$SKIP" | grep -q "R-888" && ok "R-888 remains pending after the failed resolve" || bad "R-888 unexpectedly cleared despite failed write: [$SKIP]"

# 15c) A ledger row is monotonic — a LATER write for the same item-id never deletes or
#      rewrites an earlier row (append-only). Basic sanity check, NOT a concurrency
#      reproduction: bash test execution is sequential, so a "concurrent" write issued
#      after loop_resolve already returned never actually races with its internal
#      write-then-check — the two operations can't interleave without true OS-level
#      concurrency, which isn't reproducible deterministically in a hermetic
#      single-process test. See 15d for the actual regression test on this fix.
: > "$(loop_status_path)"; loop_activate "monotonic-row test" >/dev/null
loop_defer R-410 "needs container runtime"
loop_resolve R-410 "ratified via council dyad"
RC=$?
loop_defer R-410 "a later re-deferral, e.g. from a sibling process"
[ "$RC" -eq 0 ] && ok "loop_resolve returns 0 at call-time regardless of what's written afterward" || bad "loop_resolve returned $RC on a call-time-successful write"
grep -qF '| RESOLVED-HIL | lane=-;cause=- | R-410 — ratified via council dyad |' "$(loop_status_path)" && ok "the RESOLVED-HIL row itself is still present (never deleted)" || bad "RESOLVED-HIL row missing after a later DEFERRED-HIL"

# 15d) STRUCTURAL invariant (merge-gate concurrency lens on this arc): loop_resolve's
#      body must verify its OWN write by grepping for the exact row, NOT by recomputing
#      loop_skip_set — the latter was this function's first cut and is an unsound
#      check-then-act race against concurrent writers (a concurrent loop_defer/
#      loop_resolve for the SAME item-id landing between the write and a loop_skip_set
#      re-read can flip the derived answer in either direction). Since true concurrent
#      interleaving can't be reproduced deterministically in this test harness (15c),
#      this pins the fix at the level that IS deterministically checkable: the
#      function's source no longer calls loop_skip_set at all.
BODY=$(declare -f loop_resolve)
printf '%s' "$BODY" | grep -q 'loop_skip_set' && bad "loop_resolve calls loop_skip_set (reintroduces the check-then-act race)" || ok "loop_resolve does not call loop_skip_set (self-checks its own row instead)"
printf '%s' "$BODY" | grep -q 'grep -qF' && ok "loop_resolve verifies its own write via a literal grep for the exact row" || bad "loop_resolve's own-write verification mechanism changed unexpectedly"

# 16) Re-deferring an already-resolved item re-flags it (last-write-wins, not sticky-resolved).
: > "$(loop_status_path)"; loop_activate "re-deferral test" >/dev/null
loop_defer R-300 "needs OpenAI creds"
loop_defer R-410 "needs container runtime"
loop_resolve R-410 "ratified" >/dev/null
loop_defer R-410 "regressed — needs container runtime again"
SKIP=$(loop_skip_set)
[ "$SKIP" = "R-300 R-410" ] && ok "re-deferral after resolve re-flags the item ($SKIP)" || bad "re-deferral not re-flagged: [$SKIP]"

# 17) loop_pending_hil_list (U-WT-03): EVERY pending deferral, one FULL row each — no
#     3-item cap, no "+N more" elision. This is what makes a machine-readable
#     todo_for_human[] possible; the bounded summary structurally cannot supply it.
: > "$(loop_status_path)"; loop_activate "list test" >/dev/null
loop_defer R-101 "needs creds A"
loop_defer R-102 "needs creds B"
loop_defer R-103 "needs creds C"
loop_defer R-104 "needs creds D"
loop_defer R-105 "needs creds E"
LIST=$(loop_pending_hil_list)
LN=$(printf '%s\n' "$LIST" | grep -c .)
[ "$LN" -eq 5 ] && ok "loop_pending_hil_list emits one row per pending item (5)" || bad "list row count $LN != 5"
printf '%s' "$LIST" | grep -q 'R-105 — needs creds E' && ok "list carries the FULL detail of the 5th item (uncapped)" || bad "list truncated/malformed: [$LIST]"
printf '%s' "$LIST" | grep -q 'more)' && bad "list carries the summary's '+N more' elision" || ok "list has no '+N more' elision"

# 17b) NO-REGRESSION: the bounded summary still caps at 3 + '+N more' over the SAME ledger.
SUM=$(loop_pending_hil_summary)
printf '%s' "$SUM" | grep -q '(+2 more)' && ok "summary still caps at 3 details + '+2 more'" || bad "summary cap regressed: $SUM"
printf '%s' "$SUM" | grep -q '⏸ 5 item(s) await your input' && ok "summary still reports the full pending count (5)" || bad "summary count regressed: $SUM"

# 17c) STRUCTURAL: both consumers go through the ONE shared extraction — the plan forbids
#      forking a second ledger parser (a second parser is a second authority free to
#      drift on the last-write-wins / run-boundary / leading-token rules).
LIST_BODY=$(declare -f loop_pending_hil_list)
SUM_BODY=$(declare -f loop_pending_hil_summary)
printf '%s' "$LIST_BODY" | grep -q '_loop_pending_hil_rows' && ok "loop_pending_hil_list uses the shared extraction" || bad "loop_pending_hil_list does not call _loop_pending_hil_rows"
printf '%s' "$SUM_BODY" | grep -q '_loop_pending_hil_rows' && ok "loop_pending_hil_summary uses the shared extraction" || bad "loop_pending_hil_summary does not call _loop_pending_hil_rows"
printf '%s' "$SUM_BODY" | grep -q 'awk' && bad "loop_pending_hil_summary still carries its own awk parser (forked parse)" || ok "loop_pending_hil_summary carries no second awk parser"

# 17c-bis) loop_cap_list (U-CTX-08): the generic "top-3 + (+N more)" cap extracted out of
#     loop_pending_hil_summary so a second caller (loop-gc.sh's stale-worktree hygiene
#     block) can reuse the SAME cap arithmetic instead of re-deriving it.
CAP3=$(printf 'a\nb\nc\n' | loop_cap_list)
[ "$CAP3" = "a; b; c" ] && ok "loop_cap_list: exactly 3 items, no '+N more' tail" || bad "loop_cap_list 3-item form: [$CAP3]"
CAP5=$(printf 'a\nb\nc\nd\ne\n' | loop_cap_list)
[ "$CAP5" = "a; b; c (+2 more)" ] && ok "loop_cap_list: 5 items caps to 3 + '(+2 more)'" || bad "loop_cap_list 5-item form: [$CAP5]"
CAP0=$(printf '' | loop_cap_list)
[ -z "$CAP0" ] && ok "loop_cap_list: empty input yields empty output (no '(+0 more)')" || bad "loop_cap_list empty-input form: [$CAP0]"
GC_BODY=$(cat "$SCRIPT_DIR/loop-gc.sh" 2>/dev/null)
printf '%s' "$GC_BODY" | grep -q 'loop_cap_list' && ok "loop-gc.sh reuses loop_cap_list (no duplicated cap logic)" || bad "loop-gc.sh does not call loop_cap_list"

# 17d) The list obeys the SAME semantics as the summary/skip-set: RESOLVED clears, a new
#      ACTIVATE scopes to the current run, and only the leading token keys the item.
loop_resolve R-103 "answered" >/dev/null
LIST=$(loop_pending_hil_list)
printf '%s' "$LIST" | grep -q 'R-103' && bad "resolved item still in the list: [$LIST]" || ok "loop_pending_hil_list drops a RESOLVED item"
[ "$(printf '%s\n' "$LIST" | grep -c .)" -eq 4 ] && ok "list count drops to 4 after the resolve" || bad "list count after resolve: $(printf '%s\n' "$LIST" | grep -c .)"
loop_activate "list run 2" >/dev/null
[ "$(loop_pending_hil_list | grep -c .)" -eq 4 ] && ok "ACTIVATE does not reset the pending list either (C-HE-09 §4)" || bad "ACTIVATE reset the list: [$(loop_pending_hil_list)]"

# 17e) Empty ledger → empty list (the exit report must then emit `todo_for_human: []`,
#      not a phantom row).
: > "$(loop_status_path)"
[ -z "$(loop_pending_hil_list)" ] && ok "loop_pending_hil_list empty on an empty ledger" || bad "list non-empty on an empty ledger"

# 17d) A deferral reason containing a literal pipe survives intact (codex round-2: awk -F'|'
#      split the escaped \| and truncated everything after it).
: > "$(loop_status_path)"
loop_status_ensure; loop_log ACTIVATE "run"
loop_log DEFERRED-HIL "R-PIPE — choose A | B carefully"
LP=$(loop_pending_hil_list)
[ "$LP" = "[-] R-PIPE — choose A | B carefully" ] \
  && ok "escaped pipe in a deferral detail round-trips intact" \
  || bad "pipe detail truncated or mangled: [$LP]"

# 17e) An unreadable ledger propagates FAILURE (rc!=0), never a confident empty list
#      (codex round-2: pipefail-less pipeline returned sort's 0).
P=$(loop_status_path)
chmod 000 "$P" 2>/dev/null
if loop_pending_hil_list >/dev/null 2>&1; then
  bad "unreadable ledger reported success (unknown rendered as empty)"
else
  ok "unreadable ledger propagates nonzero from the parser"
fi
chmod 644 "$P" 2>/dev/null

# 18) C-HE-20 (U-HE-09): the HITL TTL re-surfaces, never reclaims. Stub loop_now so the ledger
#     carries deterministic timestamps; the reducer must key on the HIL item token and emit at
#     most one NOTIFY per TTL window per item; the skip-set (state) is untouched.
: > "$(loop_status_path)"; loop_activate "ttl test" >/dev/null
loop_now() { echo "2026-08-17T00:00:00Z"; }; loop_defer B-1 "old deferral"
loop_now() { echo "2026-08-17T23:00:00Z"; }; loop_defer B-2 "young deferral"
loop_now() { echo "2026-08-18T00:00:01Z"; }
HARNESS_HIL_TTL_S=86400 loop_hil_ttl_resurface
grep -q '| NOTIFY | lane=[^|]* | ttl-expired B-1 .*state unchanged' "$(loop_status_path)" && ok "TTL expiry emits NOTIFY for the aged item" || bad "no NOTIFY on TTL expiry"
grep -q '| NOTIFY | lane=[^|]* | ttl-expired B-2 ' "$(loop_status_path)" && bad "young deferral re-surfaced early" || ok "young deferral (< TTL) not re-surfaced"
[ "$(loop_skip_set)" = "B-1 B-2" ] && ok "TTL does not resolve/reclaim the deferral (skip-set unchanged)" || bad "TTL changed skip-set: $(loop_skip_set)"
n_before=$(grep -c '| NOTIFY |' "$(loop_status_path)"); HARNESS_HIL_TTL_S=86400 loop_hil_ttl_resurface
[ "$(grep -c '| NOTIFY |' "$(loop_status_path)")" = "$n_before" ] && ok "second pass within the window is idempotent" || bad "duplicate NOTIFY within one TTL window"
loop_now() { echo "2026-08-19T00:00:02Z"; }; HARNESS_HIL_TTL_S=86400 loop_hil_ttl_resurface
[ "$(grep -c '| NOTIFY | lane=[^|]* | ttl-expired B-1 ' "$(loop_status_path)")" = "2" ] && ok "next TTL window re-surfaces the still-pending item again" || bad "no re-surface in the next window: $(grep -c '| NOTIFY | lane=[^|]* | ttl-expired B-1 ' "$(loop_status_path)")"
[ "$(grep -c '| NOTIFY | lane=[^|]* | ttl-expired B-2 ' "$(loop_status_path)")" = "1" ] && ok "B-2 re-surfaced once its own TTL elapsed" || bad "B-2 count: $(grep -c '| NOTIFY | lane=[^|]* | ttl-expired B-2 ' "$(loop_status_path)")"
loop_resolve B-1 "answered" >/dev/null
loop_now() { echo "2026-08-21T00:00:00Z"; }; HARNESS_HIL_TTL_S=86400 loop_hil_ttl_resurface
[ "$(grep -c '| NOTIFY | lane=[^|]* | ttl-expired B-1 ' "$(loop_status_path)")" = "2" ] && ok "a resolved item is never re-surfaced" || bad "resolved item re-surfaced"
# structured-column shape (U-HE-29 forward-compat): detail in $5 when $4 is `lane=...`
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | lane=h-w-1 | B-3 — structured row |\n' >> "$(loop_status_path)"
HARNESS_HIL_TTL_S=86400 loop_hil_ttl_resurface
grep -q '| NOTIFY | lane=[^|]* | ttl-expired B-3 ' "$(loop_status_path)" && ok "structured-column DEFERRED-HIL row is keyed on its item token" || bad "structured row not re-surfaced"
# 19) Concurrent SessionStart hooks: the eligibility read + NOTIFY append are one critical
#     section (codex round 3 on S1: 20 unlocked processes emitted 20 notifications for one item).
: > "$(loop_status_path)"; loop_activate "ttl race" >/dev/null
loop_now() { echo "2026-08-17T00:00:00Z"; }; loop_defer B-9 "raced deferral"
loop_now() { echo "2026-08-18T00:00:01Z"; }
for _ in 1 2 3 4 5 6 7 8 9 10 11 12; do ( HARNESS_HIL_TTL_S=86400 loop_hil_ttl_resurface ) & done; wait
[ "$(grep -c '| NOTIFY | lane=[^|]* | ttl-expired B-9 ' "$(loop_status_path)")" = "1" ] && ok "12 concurrent re-surface passes emit exactly one NOTIFY" || bad "concurrent NOTIFY count: $(grep -c '| NOTIFY | lane=[^|]* | ttl-expired B-9 ' "$(loop_status_path)")"
unset -f loop_now; loop_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# ── U-HE-29 / C-HE-09 ────────────────────────────────────────────────────────────────
# 20) §2 venue determinism: two worktrees, hook and raw-shell contexts, resolve the HIL
#     ledger to ONE path; control markers stay per-lane under hook_project_dir().
mkdir -p "$REPO/wt-a" "$REPO/wt-b"
( cd "$REPO/wt-a" && git init -q . 2>/dev/null ); ( cd "$REPO/wt-b" && git init -q . 2>/dev/null )
P1=$(CLAUDE_PROJECT_DIR="$REPO/wt-a" bash -c '. "$1"; . "$2"; loop_status_path' _ "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh")
P2=$(cd "$REPO/wt-b" && env -u CLAUDE_PROJECT_DIR bash -c '. "$1"; . "$2"; loop_status_path' _ "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh")
{ [ "$P1" = "$P2" ] && [ "$P1" = "$HARNESS_LOOP_STATUS_PATH" ]; } \
  && ok "venue resolves to one shared path across worktrees + contexts" || bad "venue split: [$P1] vs [$P2]"
M1=$(CLAUDE_PROJECT_DIR="$REPO/wt-a" bash -c '. "$1"; . "$2"; loop_marker_path' _ "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh")
[ "$M1" = "$REPO/wt-a/.harness/.loop-active" ] && ok "control marker stays per-lane" || bad "marker not per-lane: $M1"
# The default (no override) is QUEUE_DIR-adjacent, never per-worktree.
PD=$(env -u HARNESS_LOOP_STATUS_PATH ARC_METRICS_QUEUE_DIR="$REPO/q/arc-metrics-queue" \
  bash -c '. "$1"; . "$2"; loop_status_path' _ "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh")
[ "$PD" = "$REPO/q/loop_status.md" ] && ok "default venue is QUEUE_DIR-adjacent" || bad "default venue: $PD"

# 21) §3 row shape: the structured column goes BEFORE detail. A trailing column would be
#     glued into the rendered reason by _loop_pending_hil_rows' escaped-pipe rejoin (C7).
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
loop_log_structured DEFERRED-HIL lane-1 'merge-door-lease-acquire:transient-retry:lease_contended' 'B-9 — waiting on the door | pipe in reason'
ROW=$(tail -1 "$(loop_status_path)")
[[ "$ROW" == '| '*' | DEFERRED-HIL | lane=lane-1;cause=merge-door-lease-acquire:transient-retry:lease_contended | B-9 — waiting on the door \| pipe in reason |' ]] \
  && ok "structured column sits before detail" || bad "row shape: $ROW"
LIST=$(loop_pending_hil_list)
[ "$LIST" = '[lane-1] B-9 — waiting on the door | pipe in reason' ] \
  && ok "rendered [lane_id] + unescaped pipe, no stray column" || bad "render: [$LIST]"
# 21b) legacy 3-column rows still parse (both shapes reduce together).
printf '| 2026-08-18T00:00:00Z | DEFERRED-HIL | B-10 — legacy row |\n' >> "$(loop_status_path)"
SKIP=$(loop_skip_set)
[ "$SKIP" = "B-10 B-9" ] && ok "legacy + structured rows both reduce ($SKIP)" || bad "skip-set: [$SKIP]"
printf '%s\n' "$(loop_pending_hil_list)" | grep -q '^\[-\] B-10 — legacy row$' \
  && ok "legacy row renders with lane '-'" || bad "legacy render: [$(loop_pending_hil_list)]"
# 21c) loop_log carries the ambient lane/cause into the structured column.
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
HARNESS_LANE_ID='lane one|x' LOOP_CAUSE='g:f:c' loop_log DEFERRED-HIL "B-11 — ambient"
ROW=$(tail -1 "$(loop_status_path)")
[[ "$ROW" == *'| lane=laneonex;cause=g:f:c |'* ]] \
  && ok "loop_log carries ambient lane/cause; separators stripped from the column" || bad "ambient column: $ROW"

# 22) §4 ACTIVATE scoping (option b): one lane's ACTIVATE never hides another's deferral,
#     and RESOLVED-HIL is the only exit.
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
HARNESS_LANE_ID=L1 loop_defer B-1 "lane one deferred"
HARNESS_LANE_ID=L2 loop_activate "lane two starts" >/dev/null
[ "$(loop_skip_set)" = "B-1" ] && ok "a lane's ACTIVATE does not reset another lane's HIL row" || bad "ACTIVATE reset skip-set: [$(loop_skip_set)]"
[[ "$(loop_pending_hil_list)" == '[L1] B-1 — lane one deferred' ]] && ok "the deferring lane is rendered" || bad "lane render: [$(loop_pending_hil_list)]"
HARNESS_LANE_ID=L2 loop_resolve B-1 "resolved by lane two" >/dev/null
RC=$?
{ [ "$RC" -eq 0 ] && [ -z "$(loop_skip_set)" ]; } && ok "RESOLVED-HIL is the only exit (cross-lane resolve verified)" || bad "cross-lane resolve failed (rc=$RC, skip=[$(loop_skip_set)])"

# 23) §5 NOTIFY: append-only, rendered BESIDE the HIL summary, never in the skip-set.
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
loop_log_structured NOTIFY L1 'reservation-stale:HITL-recoverable:pending_aged' 'B-2 pending > 24h'
[ -z "$(loop_skip_set)" ] && ok "NOTIFY never enters the skip-set" || bad "NOTIFY leaked into skip-set: [$(loop_skip_set)]"
[ -z "$(loop_pending_hil_list)" ] && ok "NOTIFY is not a pending HIL row" || bad "NOTIFY in pending list: [$(loop_pending_hil_list)]"
NS=$(loop_notify_summary)
{ printf '%s' "$NS" | grep -q 'B-2 pending > 24h' && printf '%s' "$NS" | grep -q '\[L1\]'; } \
  && ok "NOTIFY rendered with its lane" || bad "NOTIFY not rendered: [$NS]"
# 23b) the horizon bounds it: a NOTIFY older than 24 h is not re-rendered.
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
printf '| 2026-08-01T00:00:00Z | NOTIFY | lane=L1;cause=g:f:c | B-3 stale notice |\n' >> "$(loop_status_path)"
loop_now() { echo "2026-08-20T00:00:00Z"; }
[ -z "$(loop_notify_summary)" ] && ok "NOTIFY outside the 24 h horizon is not rendered" || bad "stale NOTIFY rendered: [$(loop_notify_summary)]"
# 23c) ... and the newest 5 within the horizon are, escaped pipes restored.
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
for i in 1 2 3 4 5 6; do loop_log_structured NOTIFY L1 'g:f:c' "B-$i note | with pipe"; done
NS=$(loop_notify_summary)
[ "$(printf '%s' "$NS" | grep -c 'with pipe')" = "1" ] && ok "notify summary is one line" || bad "notify summary shape: [$NS]"
printf '%s' "$NS" | grep -q 'B-1 note' && bad "6th-oldest NOTIFY not dropped: [$NS]" || ok "notify summary keeps the newest 5"
printf '%s' "$NS" | grep -q 'B-6 note | with pipe' && ok "notify summary unescapes pipes" || bad "notify escape: [$NS]"
unset -f loop_now; loop_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# 24) Write failure: the STRUCTURED writer propagates (an unrecorded DEFERRED-HIL/NOTIFY
#     is a lost operator signal) while loop_log keeps its always-0 hook contract.
( HARNESS_LOOP_STATUS_PATH=/nonexistent-dir/x.md loop_log_structured NOTIFY L1 g:f:c "detail" ) 2>/dev/null
[ $? -eq 1 ] && ok "loop_log_structured returns 1 when the shared ledger cannot be written" || bad "structured write failure not propagated"
( HARNESS_LOOP_STATUS_PATH=/nonexistent-dir/x.md loop_log NOTIFY "detail" ) 2>/dev/null
[ $? -eq 0 ] && ok "loop_log preserves its always-0 hook contract" || bad "loop_log broke its always-0 contract"

# 25) §2 pointer sweep: no live carrier still cites the per-worktree ledger path.
SWEEP=$(cd "$SCRIPT_DIR/../.." && grep -rl '\.harness/loop_status\.md' \
  tools/hooks/loop_lib.sh tools/roadmap-audit/session-start.sh tools/arc_exit_report.py \
  .claude/skills/loop-start/SKILL.md .claude/skills/loop-stop/SKILL.md \
  .claude/skills/resolve/SKILL.md .claude/skills/ship-pr/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
[ "$SWEEP" = "0" ] && ok "pointer sweep: 0 literal .harness/loop_status.md hits in live carriers" || bad "stale pointers remain in $SWEEP file(s)"

# 26) codex r1 P2 — first-writer TOCTOU on the SHARED venue. N lanes racing to log into a
#     venue that does not exist yet must ALL keep their rows: a truncating create by a
#     loser would erase a row the winner already appended, silently destroying a durable
#     operator signal while the writer still reported success.
RACE="$REPO/race/loop_status.md"
for round in 1 2 3; do
  rm -rf "$REPO/race"
  for i in 1 2 3 4 5 6 7 8 9 10 11 12; do
    ( HARNESS_LOOP_STATUS_PATH="$RACE" loop_log_structured DEFERRED-HIL "L$i" g:f:c "B-$i — racer $i" ) &
  done
  wait
  N=$(grep -c '| DEFERRED-HIL |' "$RACE" 2>/dev/null || echo 0)
  [ "$N" = "12" ] || break
done
[ "$N" = "12" ] && ok "12 lanes racing to create the venue keep all 12 rows" || bad "create race lost rows: $N/12"
[ "$(grep -c '^# Loop status ledger$' "$RACE" 2>/dev/null)" = "1" ] && ok "exactly one header survives the create race" || bad "header count: $(grep -c '^# Loop status ledger$' "$RACE" 2>/dev/null)"

# 27) codex r1 P2 — a RELATIVE venue is rejected, not silently resolved per-CWD. Returning
#     the relative text unchanged would make two lanes with different CWDs write different
#     physical files while every string comparison still reported them equal.
REL=$(HARNESS_LOOP_STATUS_PATH="rel/loop_status.md" loop_status_path 2>/dev/null); RC=$?
{ [ "$RC" -ne 0 ] && [ -z "$REL" ]; } && ok "relative HARNESS_LOOP_STATUS_PATH is rejected" || bad "relative venue accepted: rc=$RC [$REL]"
RELQ=$(env -u HARNESS_LOOP_STATUS_PATH ARC_METRICS_QUEUE_DIR="rel/queue" bash -c '. "$1"; . "$2"; loop_status_path' _ "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh" 2>/dev/null)
[ -z "$RELQ" ] && ok "relative ARC_METRICS_QUEUE_DIR is rejected" || bad "relative queue dir accepted: [$RELQ]"
( HARNESS_LOOP_STATUS_PATH="rel/loop_status.md" loop_log_structured NOTIFY L1 g:f:c "d" ) 2>/dev/null
[ $? -eq 1 ] && ok "an unusable venue fails the structured write closed" || bad "structured write succeeded on an unusable venue"

echo "----"
echo "loop_lib: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

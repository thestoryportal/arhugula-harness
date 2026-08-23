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

# 25) §2 pointer sweep: no live carrier — code, recipe, skill, or operator INSTRUCTION —
#     still points a reader or a writer at the per-worktree ledger path. The list covers
#     live carriers only: historical records (fork docs, clearance markers, the next-action
#     archive, this arc's own plan/spec prose) legitimately describe the pre-U-HE-29 venue
#     and must NOT be rewritten — a record of what was true then is not a stale pointer.
#     `.harness/wave2-hooks-status.md` is in the list because it is a live operator
#     instruction ("Review ... after any run"), and following it would have missed every
#     shared row (codex r9 P3). Nothing in a live carrier legitimately names the old path
#     any more, so the count must be exactly zero.
SWEEP=$(cd "$SCRIPT_DIR/../.." && grep -rn '\.harness/loop_status\.md' \
  tools/hooks/loop_lib.sh tools/roadmap-audit/session-start.sh tools/arc_exit_report.py \
  tools/04-loop/run.sh justfile \
  .claude/skills/loop-start/SKILL.md .claude/skills/loop-stop/SKILL.md \
  .claude/skills/resolve/SKILL.md .claude/skills/ship-pr/SKILL.md \
  .agents/skills/ship-pr/SKILL.md .harness/wave2-hooks-status.md 2>/dev/null \
  | wc -l | tr -d ' ')
[ "$SWEEP" = "0" ] && ok "pointer sweep: 0 literal .harness/loop_status.md hits in live carriers" || bad "stale pointers remain ($SWEEP line(s))"
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

# 26b) STRUCTURAL invariant, and the load-bearing half. The 12-lane race above is an
#      end-to-end sanity check, NOT a reproduction: it was mutation-probed with the
#      `set -o noclobber` line removed and stayed GREEN, because forked subshells rarely
#      interleave inside the few microseconds between the `-f` test and the redirect. Same
#      situation as 15c/15d above — true concurrent interleaving is not deterministically
#      reproducible in this harness, so the fix is pinned at the level that IS checkable:
#      the creating redirect must run under noclobber (O_EXCL), never as a bare truncating
#      `>`. Tuning the race until it flakes red would be pinning luck, not the mechanism.
ENSURE_BODY=$(declare -f loop_status_ensure)
# LITERAL only (merge-gate witness lens, pre-merge round). A looser `ln .*_tmp` alternative
# also matches `ln -f "$_tmp" "$p"` — and `-f` unlinks an existing target, which defeats the
# EEXIST/O_EXCL guarantee this whole protocol rests on: a losing lane would replace the
# winner's already-published venue, including rows already appended to it. The regression
# that matters most here is precisely the one the loose form let through.
printf '%s' "$ENSURE_BODY" | grep -qF 'ln "$_tmp" "$p"' \
  && ok "loop_status_ensure publishes a COMPLETE header atomically via ln" \
  || bad "loop_status_ensure does not publish atomically (partial-header window)"
printf '%s' "$ENSURE_BODY" | grep -qE 'cat > "\$p"' \
  && bad "loop_status_ensure still writes the header directly to the venue" \
  || ok "the venue is never opened for a truncating/non-append write"

# 26c) The published venue is COMPLETE the instant it exists (codex r2 P2): noclobber alone
#      let the file appear at open() while the header was still being written, so a second
#      lane could append into the gap and have the winner's absolute-offset writes land on
#      top of it. Witness the property that rules the whole class out — no writer ever
#      appends to a venue carrying a partial header.
rm -rf "$REPO/pub"; PUB="$REPO/pub/loop_status.md"
HARNESS_LOOP_STATUS_PATH="$PUB" loop_status_ensure >/dev/null
{ head -1 "$PUB" | grep -q '^# Loop status ledger$' && tail -1 "$PUB" | grep -q '^|---|---|---|---|$'; } \
  && ok "the venue's header is whole at publication (first + last header line present)" \
  || bad "published venue has a partial header: $(wc -l < "$PUB") line(s)"
[ -z "$(find "$REPO/pub" -name '*.tmp' 2>/dev/null)" ] && ok "no staging temp file is left behind" || bad "staging temp leaked: $(find "$REPO/pub" -name '*.tmp')"

# 26d) codex r2 P2 — an embedded NEWLINE in a lane id must never split one row into two.
#      Lane ids inherit worktree-name text; a split row makes the reducer read a malformed
#      detail and drop the gate, silently losing an operator obligation.
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
BEFORE_LINES=$(wc -l < "$(loop_status_path)")
loop_log_structured DEFERRED-HIL "$(printf 'lane\nbroken')" "$(printf 'g:f\n:c')" "B-13 — newline lane"
[ "$(( $(wc -l < "$(loop_status_path)") - BEFORE_LINES ))" -eq 1 ] \
  && ok "a newline-bearing lane id still writes exactly ONE physical row" || bad "row split across lines"
[ "$(loop_skip_set)" = "B-13" ] && ok "the gate survives a newline-bearing lane id" || bad "gate lost: [$(loop_skip_set)]"
[[ "$(loop_pending_hil_list)" == '[lanebroken] B-13 — newline lane' ]] \
  && ok "the newline is stripped from the rendered lane" || bad "lane render: [$(loop_pending_hil_list)]"

# 27) codex r1 P2 — a RELATIVE venue is rejected, not silently resolved per-CWD. Returning
#     the relative text unchanged would make two lanes with different CWDs write different
#     physical files while every string comparison still reported them equal.
# Run every relative-venue probe from a scratch CWD: if this guard ever regresses, the
# relative path resolves against the CALLER's cwd, and a bare invocation here would write
# a stray ledger into the repo root (witnessed exactly that way while mutation-probing
# this guard). The scratch dir contains the blast radius to the temp tree.
mkdir -p "$REPO/relcwd"
REL=$(cd "$REPO/relcwd" && HARNESS_LOOP_STATUS_PATH="rel/loop_status.md" loop_status_path 2>/dev/null); RC=$?
{ [ "$RC" -ne 0 ] && [ -z "$REL" ]; } && ok "relative HARNESS_LOOP_STATUS_PATH is rejected" || bad "relative venue accepted: rc=$RC [$REL]"
RELQ=$(cd "$REPO/relcwd" && env -u HARNESS_LOOP_STATUS_PATH ARC_METRICS_QUEUE_DIR="rel/queue" bash -c '. "$1"; . "$2"; loop_status_path' _ "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh" 2>/dev/null)
[ -z "$RELQ" ] && ok "relative ARC_METRICS_QUEUE_DIR is rejected" || bad "relative queue dir accepted: [$RELQ]"
( cd "$REPO/relcwd" && HARNESS_LOOP_STATUS_PATH="rel/loop_status.md" loop_log_structured NOTIFY L1 g:f:c "d" ) 2>/dev/null
[ $? -eq 1 ] && ok "an unusable venue fails the structured write closed" || bad "structured write succeeded on an unusable venue"

# 31) codex r3 P2 — loop_resolve must verify its OWN write, not a byte-identical historical
#     row. On a shared never-truncated venue the same RESOLVED-HIL text can already exist
#     from a previous run; if the item was re-deferred since and this append fails, a
#     whole-file grep would report a false "resolved" while the reducer still sees it pending.
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
loop_defer R-555 "needs a decision"
loop_resolve R-555 "answered" >/dev/null
loop_defer R-555 "re-deferred after the answer went stale"
chmod 0444 "$(loop_status_path)"
loop_resolve R-555 "answered" 2>/dev/null
RC=$?
chmod 0644 "$(loop_status_path)"
[ "$RC" -ne 0 ] && ok "a failed resolve does not match the identical historical row" || bad "stale row produced a false 'resolved'"
[ "$(loop_skip_set)" = "R-555" ] && ok "the re-deferred item stays pending after the failed resolve" || bad "item wrongly cleared: [$(loop_skip_set)]"

# 32) codex r4/r5 P2 — the lane must come from the PERSISTED marker when the env var is
#     unset. defer.sh and the ordinary hooks never export HARNESS_LANE_ID, so without this
#     every row they write lands unattributed even in a worktree that has had a lane id on
#     disk all along — losing the §3 attribution the arc-exit report reads.
mkdir -p "$REPO/.harness"; printf 'L-persisted\n' > "$REPO/.harness/.lane-id"
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
( unset HARNESS_LANE_ID; loop_log DEFERRED-HIL "B-15 — no env lane" )
[[ "$(loop_pending_hil_list)" == '[L-persisted] B-15 — no env lane' ]] \
  && ok "the persisted .lane-id attributes a row when the env var is unset" || bad "lane fallback: [$(loop_pending_hil_list)]"
# the env var still wins when both are present
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
HARNESS_LANE_ID=L-env loop_log DEFERRED-HIL "B-16 — env wins"
[[ "$(loop_pending_hil_list)" == '[L-env] B-16 — env wins' ]] && ok "HARNESS_LANE_ID wins over the persisted marker" || bad "env precedence: [$(loop_pending_hil_list)]"
rm -f "$REPO/.harness/.lane-id"

# 38) codex r6 P2 — the staging file is created EXCLUSIVELY. `$$` is shared across a bash's
#     subshells and $RANDOM is 15 bits, so a guessable name lets two callers write one inode
#     and publish it half-written — the very race the ln protocol removes.
printf '%s' "$(declare -f loop_status_ensure)" | grep -q 'mktemp' \
  && ok "the staging file is created exclusively (mktemp)" || bad "staging name is guessable"
# BEHAVIOURAL (codex r16 P3): when mktemp cannot supply an exclusive name the venue must NOT
# be created through a guessable fallback — that fallback was the very race this removes.
printf '%s' "$(declare -f loop_status_ensure)" | grep -qE '\$\$[-._].*RANDOM|RANDOM.*\$\$' \
  && bad "loop_status_ensure still falls back to a guessable staging name" \
  || ok "no guessable staging fallback remains"
MKFAIL="$REPO/mkfail"; rm -rf "$MKFAIL"; mkdir -p "$MKFAIL/bin"
printf '#!/bin/sh\nexit 1\n' > "$MKFAIL/bin/mktemp"; chmod +x "$MKFAIL/bin/mktemp"
MKV="$MKFAIL/venue/loop_status.md"
( PATH="$MKFAIL/bin:$PATH" HARNESS_LOOP_STATUS_PATH="$MKV" loop_status_ensure ) >/dev/null 2>&1
[ ! -e "$MKV" ] && ok "a failed mktemp creates no venue instead of using a guessable name" || bad "venue created via the unsafe fallback"

# 40) codex r7 P2 — `[`/`]` must not survive into a lane id. Pending rows are RENDERED as
#     `[<lane>] <detail>` and every consumer reading that form back delimits on the brackets,
#     so a bracket-bearing lane would bleed into the detail and lose the item token.
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
loop_log_structured DEFERRED-HIL 'la]ne[x' 'g:f:c' "B-17 — bracket lane"
[[ "$(loop_pending_hil_list)" == '[lanex] B-17 — bracket lane' ]] \
  && ok "brackets are stripped from the lane id" || bad "bracket lane: [$(loop_pending_hil_list)]"
[ "$(loop_skip_set)" = "B-17" ] && ok "the gate survives a bracket-bearing lane id" || bad "gate lost: [$(loop_skip_set)]"

# 41) codex r7 P2 — the writer and the arc-exit reader must resolve the lane in the SAME
#     order (env, then persisted marker). Opposite orders would make an arc classify its own
#     freshly-written rows as foreign whenever both sources exist and differ.
# BEHAVIOURAL cross-check, not a substring pin (merge-gate witness lens on the re-gate): the
# old form grepped both bodies for a token, which cannot see PRECEDENCE — reversing the
# env/marker order on either side would have stayed green. Feed the SAME two inputs to the
# bash writer and the python reader and require the SAME answer; that is the property whose
# violation makes an arc classify its own rows as foreign.
LANEDIR="$REPO/lane-xcheck"; rm -rf "$LANEDIR"; mkdir -p "$LANEDIR/.harness"
printf 'L-marker
' > "$LANEDIR/.harness/.lane-id"
W_BOTH=$(CLAUDE_PROJECT_DIR="$LANEDIR" HARNESS_LANE_ID=L-env bash -c '. "$1"; . "$2"; _loop_lane_id' _ "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh")
R_BOTH=$(cd "$SCRIPT_DIR/../.." && HARNESS_LANE_ID=L-env uv run python -c "
import sys; sys.path.insert(0, 'tools')
import arc_exit_report as aer
from pathlib import Path
print(aer._lane_id(Path('$LANEDIR')))
" 2>/dev/null)
[ -n "$W_BOTH" ] && [ "$W_BOTH" = "$R_BOTH" ] && ok "writer and reader agree with BOTH sources set ($W_BOTH)" || bad "lane precedence diverged with both set: writer=[$W_BOTH] reader=[$R_BOTH]"
W_MARK=$(CLAUDE_PROJECT_DIR="$LANEDIR" env -u HARNESS_LANE_ID bash -c '. "$1"; . "$2"; _loop_lane_id' _ "$SCRIPT_DIR/lib.sh" "$SCRIPT_DIR/loop_lib.sh")
R_MARK=$(cd "$SCRIPT_DIR/../.." && env -u HARNESS_LANE_ID uv run python -c "
import sys; sys.path.insert(0, 'tools')
import arc_exit_report as aer
from pathlib import Path
print(aer._lane_id(Path('$LANEDIR')))
" 2>/dev/null)
[ "$W_MARK" = "$R_MARK" ] && [ "$W_MARK" = "L-marker" ] && ok "writer and reader agree on the marker-only case ($W_MARK)" || bad "marker-only case diverged: writer=[$W_MARK] reader=[$R_MARK]"

# 62) codex r22 P2 — a PARTIAL header must never be published. Staging exists precisely so
#     nothing incomplete becomes visible; once the venue exists, later calls append to it and
#     a durable row can be concatenated onto a broken line where the reducers cannot see it.
EBODY=$(declare -f loop_status_ensure)
printf '%s' "$EBODY" | grep -q '_staged.*-eq 0.*ln \|\[ "\$_staged" -eq 0 \]' \
  && ok "the venue is published only when the staging write SUCCEEDED" \
  || bad "ln can publish a partially-written header"


# 63) U-HE-30 / C-HE-10 — gate coalescing by `cause_signature`, windowed, pull-based.
#     Lanes only APPEND deferrals; `loop_hil_deliver` is the single place a group becomes
#     a prompt, and only once `first_seen + window` has elapsed. The claims dir is
#     QUEUE_DIR-adjacent, so ARC_METRICS_QUEUE_DIR is pinned into the throwaway repo.
#     Delivery serialises on the SAME .loop-status.lock loop_hil_ttl_resurface uses, so
#     the whole mechanism is hermetic under the pinned HARNESS_LOOP_STATUS_PATH -- there
#     is no side-car claim directory to reset, and nothing is written under the real HOME.
export ARC_METRICS_QUEUE_DIR="$REPO/queue"
mkdir -p "$ARC_METRICS_QUEUE_DIR"
_coalesce_reset() { : > "$(loop_status_path)"; loop_status_ensure >/dev/null; }

_coalesce_reset
loop_now() { echo "2026-08-18T00:00:00Z"; }
loop_log_structured DEFERRED-HIL L1 'merge-door-lease-acquire:transient-retry:lease_contended' 'B-1 — waiting'
loop_log_structured DEFERRED-HIL L2 'merge-door-lease-acquire:transient-retry:lease_contended' 'B-2 — waiting'
loop_log_structured DEFERRED-HIL L3 'reviewer:permanent-fail-exit:codex_login' 'B-3 — login'
G=$(loop_hil_groups)
[ "$(printf '%s\n' "$G" | grep -c .)" = "2" ] && ok "two cause groups" || bad "groups: $G"
printf '%s\n' "$G" | grep -qF $'lease_contended\t2\t' \
  && ok "equal signatures within window -> one group of 2" || bad "no 2-group: $G"

loop_now() { echo "2026-08-18T00:05:00Z"; }
[ -z "$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)" ] \
  && ok "inside window: nothing delivered yet" || bad "delivered early"

loop_now() { echo "2026-08-18T00:11:00Z"; }
OUT=$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)
[[ "$OUT" == *"[L1] B-1"* && "$OUT" == *"[L2] B-2"* ]] \
  && ok "one batched prompt per cause after window" || bad "deliver: $OUT"
[ "$(grep -c '| COALESCE-DELIVERED |' "$(loop_status_path)")" = "2" ] \
  && ok "delivery rows appended (one per due group)" || bad "no delivery rows"
[ -z "$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)" ] \
  && ok "second SessionStart does not re-prompt" || bad "double delivery"

# The ledger is the SOLE delivered-authority (codex r1 P1): no side-car claim file exists,
# so no scratch-dir cleanup can resurrect a prompt the operator already received, and no
# cause_signature is ever squeezed through a filename character set where two distinct
# valid triples could collide.
[ ! -d "$ARC_METRICS_QUEUE_DIR/hil-deliveries" ] \
  && ok "no side-car claim directory is created (ledger is the sole authority)" \
  || bad "a claims directory was created"
rm -rf "$ARC_METRICS_QUEUE_DIR"
[ -z "$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)" ] \
  && ok "a wiped queue dir does not re-prompt (ledger is the durable authority)" \
  || bad "queue-dir wipe resurrected a delivered prompt"
mkdir -p "$ARC_METRICS_QUEUE_DIR"


# A LATER same-signature generation is a NEW group and must still be delivered -- the
# claim is keyed by the exact generation, never by "any delivery at or after first_seen".
loop_now() { echo "2026-08-18T00:30:00Z"; }
loop_log_structured DEFERRED-HIL L4 'merge-door-lease-acquire:transient-retry:lease_contended' 'B-4 — later'
[ "$(loop_hil_groups | grep -c lease_contended)" = "2" ] \
  && ok "same signature outside window -> separate group" || bad "window merge wrong: $(loop_hil_groups)"
loop_now() { echo "2026-08-18T00:45:00Z"; }
[[ "$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)" == *"B-4"* ]] \
  && ok "later same-signature generation is delivered (not suppressed by the earlier one)" \
  || bad "later generation suppressed"

# Two cause signatures that a filename-safe sanitisation would collapse onto each other
# (`:` and `_` both becoming `_`) must stay DISTINCT groups and both be delivered, even
# when they share a first_seen second. This is the collision the claim-file design had.
_coalesce_reset
loop_now() { echo "2026-08-18T08:00:00Z"; }
loop_log_structured DEFERRED-HIL L1 'gate_a:fail:b' 'B-70 — underscore then colon'
loop_log_structured DEFERRED-HIL L2 'gate:a_fail:b' 'B-71 — colon then underscore'
[ "$(loop_hil_groups | grep -c .)" = "2" ] \
  && ok "signatures differing only in : vs _ stay two groups" || bad "sanitisation-collision groups: $(loop_hil_groups)"
loop_now() { echo "2026-08-18T08:11:00Z"; }
OUT_C=$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)
[[ "$OUT_C" == *"B-70"* && "$OUT_C" == *"B-71"* ]] \
  && ok "neither colliding-when-sanitised signature suppresses the other" \
  || bad "one cause group suppressed the other: $OUT_C"

# Atomic claim: two CONCURRENT deliverers -> exactly one prompt. The ledger check alone
# cannot close this (both read "not delivered" before either appends); the exclusive
# create does.
_coalesce_reset
loop_now() { echo "2026-08-18T01:00:00Z"; }; loop_log_structured DEFERRED-HIL L1 'x:y:z' 'B-7 — a'
loop_now() { echo "2026-08-18T01:11:00Z"; }
OUT_A=$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver & HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver & wait)
[ "$(printf '%s\n' "$OUT_A" | grep -c 'need you')" = "1" ] \
  && ok "concurrent deliverers: exactly one prompt" || bad "double prompt under concurrency: $OUT_A"

# The window anchor is the first ARRIVAL, not the lexically-first item id: a lexically
# earlier item deferred 20 min LATER must open its own group, not re-anchor the first.
_coalesce_reset
loop_now() { echo "2026-08-18T02:00:00Z"; }; loop_log_structured DEFERRED-HIL L1 'x:y:z' 'B-9 — first'
loop_now() { echo "2026-08-18T02:20:00Z"; }; loop_log_structured DEFERRED-HIL L1 'x:y:z' 'B-1 — later but lexically first'
[ "$(loop_hil_groups | grep -c .)" = "2" ] \
  && ok "groups keyed by arrival time (20 min apart -> 2 groups)" || bad "timestamp ordering wrong: $(loop_hil_groups)"

# A RESOLVED-HIL row clears its item from grouping under the same last-write-wins rule
# the skip-set uses -- the grouper must not batch an already-answered gate into a prompt.
_coalesce_reset
loop_now() { echo "2026-08-18T03:00:00Z"; }
loop_log_structured DEFERRED-HIL L1 'x:y:z' 'B-20 — waiting'
loop_log_structured DEFERRED-HIL L2 'x:y:z' 'B-21 — waiting'
loop_log_structured RESOLVED-HIL L1 'x:y:z' 'B-20 — answered'
G3=$(loop_hil_groups)
[ "$(printf '%s\n' "$G3" | grep -c .)" = "1" ] && [[ "$G3" == *"B-21"* && "$G3" != *"B-20 — waiting"* ]] \
  && ok "a RESOLVED item leaves the group (last-write-wins, shared with loop_skip_set)" \
  || bad "resolved item still grouped: $G3"

# The generation id is (signature, first_seen) and MUST NOT carry the member count. If it
# did, one more lane deferring into an already-delivered window at the boundary second
# would mint a second generation and re-prompt items the operator already received --
# C-HE-10 §2 says rows covered by a delivery at/after their first_seen ARE delivered.
_coalesce_reset
loop_now() { echo "2026-08-18T04:00:00Z"; }; loop_log_structured DEFERRED-HIL L1 'x:y:z' 'B-30 — a'
loop_now() { echo "2026-08-18T04:10:00Z"; }
[[ "$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)" == *"B-30"* ]] \
  && ok "boundary case: the first generation delivers" || bad "boundary generation not delivered"
loop_log_structured DEFERRED-HIL L2 'x:y:z' 'B-31 — joined at the boundary second'
[ "$(loop_hil_groups | grep -c .)" = "1" ] \
  && ok "a boundary-second arrival joins the SAME group (e - first == w)" || bad "boundary row opened a new group"
[ -z "$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)" ] \
  && ok "generation id carries no member count: a boundary join does not re-prompt" \
  || bad "member-count-keyed generation re-prompted a delivered group"

# Legacy / signature-less rows reduce as their OWN singleton group (C-HE-10 §1).
# Collapsing them under a shared `-` would batch unrelated gates into one prompt.
_coalesce_reset
loop_now() { echo "2026-08-18T05:00:00Z"; }
loop_log DEFERRED-HIL "B-40 — no cause"
loop_log DEFERRED-HIL "B-41 — also no cause"
printf '| 2026-08-18T05:00:00Z | DEFERRED-HIL | B-42 — three-column legacy row |\n' >> "$(loop_status_path)"
[ "$(loop_hil_groups | grep -c .)" = "3" ] \
  && ok "signature-less rows are singleton groups, never one merged no-cause batch" \
  || bad "legacy grouping wrong: $(loop_hil_groups)"

# A NON-NUMERIC window override must fall back to the default, never reach `[ -lt ]` and
# leave garbage in place: awk would read that as w == 0 and prompt on EVERY deferral --
# silently disabling the whole contract.
[ "$(HARNESS_HIL_COALESCE_WINDOW_S=abc _loop_coalesce_window)" = "600" ] \
  && ok "non-numeric window falls back to the 600 s default" \
  || bad "bad window value not rejected: $(HARNESS_HIL_COALESCE_WINDOW_S=abc _loop_coalesce_window)"
[ "$(HARNESS_HIL_COALESCE_WINDOW_S=60 _loop_coalesce_window)" = "300" ] \
  && ok "window clamps up to the 300 s floor" || bad "floor clamp wrong"
[ "$(HARNESS_HIL_COALESCE_WINDOW_S=99999 _loop_coalesce_window)" = "900" ] \
  && ok "window clamps down to the 900 s ceiling" || bad "ceiling clamp wrong"

# first_seen is the FIRST arrival, not the latest (codex r1 P2). The session-start
# reservation reconcile pass RE-EMITS the same unresolved deferral every session; with a
# latest-wins anchor, sessions closer together than the window postpone delivery forever.
_coalesce_reset
loop_now() { echo "2026-08-18T06:00:00Z"; }; loop_log_structured DEFERRED-HIL L1 'x:y:z' 'B-50 — waiting'
loop_now() { echo "2026-08-18T06:05:00Z"; }; loop_log_structured DEFERRED-HIL L1 'x:y:z' 'B-50 — waiting'
loop_now() { echo "2026-08-18T06:09:00Z"; }; loop_log_structured DEFERRED-HIL L1 'x:y:z' 'B-50 — waiting'
loop_now() { echo "2026-08-18T06:10:00Z"; }
[[ "$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)" == *"B-50"* ]] \
  && ok "a re-emitted deferral does not postpone delivery (first_seen is the FIRST arrival)" \
  || bad "re-emission pushed the window anchor forward"
# ...but a genuinely NEW deferral after a RESOLVED-HIL does re-anchor: that is a fresh gate.
loop_log_structured RESOLVED-HIL L1 'x:y:z' 'B-50 — answered'
loop_now() { echo "2026-08-18T06:11:00Z"; }; loop_log_structured DEFERRED-HIL L1 'x:y:z' 'B-50 — deferred again'
[ -z "$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)" ] \
  && ok "a NEW deferral after RESOLVED re-anchors the window" || bad "re-deferral did not re-anchor"

# Resolving the EARLIEST member of a delivered group must not re-prompt the members that
# were already in that batch (codex r3 P2). A generation id is recomputed from the earliest
# still-PENDING member, so id-matching re-prompts here; comparing the delivery TIMESTAMP
# against the group's first_seen -- C-HE-10 §2's literal rule -- does not.
_coalesce_reset
loop_now() { echo "2026-08-18T10:00:00Z"; }; loop_log_structured DEFERRED-HIL L1 'q:r:s' 'B-95 — earliest member'
loop_now() { echo "2026-08-18T10:00:30Z"; }; loop_log_structured DEFERRED-HIL L2 'q:r:s' 'B-96 — later member'
loop_now() { echo "2026-08-18T10:11:00Z"; }
OUT_R=$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)
[[ "$OUT_R" == *"B-95"* && "$OUT_R" == *"B-96"* ]] \
  && ok "both members ride the one batch" || bad "batch incomplete: $OUT_R"
loop_log_structured RESOLVED-HIL L1 'q:r:s' 'B-95 — answered'
loop_now() { echo "2026-08-18T10:12:00Z"; }
[ -z "$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)" ] \
  && ok "resolving the earliest member does not re-prompt the rest of a delivered batch" \
  || bad "delivered member re-prompted after an earlier member resolved"

# Two DUE generations of one cause in a single pass are two genuinely undelivered
# generations: both must be prompted, so the pass must not stamp itself into the map.
_coalesce_reset
loop_now() { echo "2026-08-18T11:00:00Z"; }; loop_log_structured DEFERRED-HIL L1 'u:v:w' 'B-97 — gen one'
loop_now() { echo "2026-08-18T11:30:00Z"; }; loop_log_structured DEFERRED-HIL L2 'u:v:w' 'B-98 — gen two'
loop_now() { echo "2026-08-18T11:45:00Z"; }
OUT_T=$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)
[[ "$OUT_T" == *"B-97"* && "$OUT_T" == *"B-98"* ]] \
  && ok "two due generations of one cause both deliver in a single pass" \
  || bad "one due generation suppressed the other in-pass: $OUT_T"

# A CHANGED cause is a new gate and re-anchors the window (codex r2 P2). Without this the
# item keeps cause A's first arrival while grouping under cause B, so B can be instantly
# eligible instead of receiving its own coalescing window.
_coalesce_reset
loop_now() { echo "2026-08-18T09:00:00Z"; }; loop_log_structured DEFERRED-HIL L1 'cause:a:one' 'B-90 — first cause'
loop_now() { echo "2026-08-18T09:09:00Z"; }; loop_log_structured DEFERRED-HIL L1 'cause:b:two' 'B-90 — different cause now'
G5=$(loop_hil_groups)
[[ "$G5" == *"cause:b:two"* ]] && ok "a re-deferral under a new cause groups under the NEW signature" || bad "cause not updated: $G5"
loop_now() { echo "2026-08-18T09:10:00Z"; }
[ -z "$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)" ] \
  && ok "the new cause gets its OWN window (not the old cause's anchor)" \
  || bad "changed cause inherited the previous anchor and delivered early"
loop_now() { echo "2026-08-18T09:20:00Z"; }
[[ "$(HARNESS_HIL_COALESCE_WINDOW_S=600 loop_hil_deliver)" == *"B-90"* ]] \
  && ok "the new cause delivers once ITS window closes" || bad "new cause never delivered"

# Detail is free text and the writer preserves TABS, while the inter-pass stream is
# tab-delimited: an unneutralised tab splits into extra fields and the renderer, which
# keeps only $5, truncates the operator-facing gate detail (codex r1 P3).
_coalesce_reset
loop_now() { echo "2026-08-18T07:00:00Z"; }
loop_log_structured DEFERRED-HIL L1 'x:y:z' "$(printf 'B-60 — reason\twith a tab after it')"
G4=$(loop_hil_groups)
[[ "$G4" == *"with a tab after it"* ]] \
  && ok "a tab in the detail does not truncate the rendered gate" || bad "tab truncated the detail: $G4"

# ONE epoch authority: the grouper must use the same awk implementation every other
# reducer uses, not a second `date`-forking copy free to drift on the edges.
[ "$(_loop_epoch_of '1970-01-01T00:00:00Z')" = "0" ] && ok "epoch helper agrees with the shared awk implementation" || bad "epoch helper wrong: $(_loop_epoch_of '1970-01-01T00:00:00Z')"
[ "$(_loop_epoch_of 'not-a-timestamp')" = "-1" ] && ok "epoch helper reports unparseable as -1" || bad "epoch helper did not reject garbage"

echo "----"
echo "loop_lib: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

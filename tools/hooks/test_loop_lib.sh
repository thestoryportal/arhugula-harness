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
#     shared row (codex r9 P3). `loop_status_migrate` is the ONE legitimate mention -- it
#     exists precisely to drain those files -- so lines belonging to it are excluded by
#     their `legacy` marker; everything else must be zero.
SWEEP=$(cd "$SCRIPT_DIR/../.." && grep -rn '\.harness/loop_status\.md' \
  tools/hooks/loop_lib.sh tools/roadmap-audit/session-start.sh tools/arc_exit_report.py \
  tools/04-loop/run.sh justfile \
  .claude/skills/loop-start/SKILL.md .claude/skills/loop-stop/SKILL.md \
  .claude/skills/resolve/SKILL.md .claude/skills/ship-pr/SKILL.md \
  .agents/skills/ship-pr/SKILL.md .harness/wave2-hooks-status.md 2>/dev/null \
  | grep -v 'legacy' | wc -l | tr -d ' ')
[ "$SWEEP" = "0" ] && ok "pointer sweep: 0 literal .harness/loop_status.md hits in live carriers" || bad "stale pointers remain ($SWEEP line(s))"
# ... and the migration's own mention is genuinely there (the exclusion above must not be
# silently covering an empty set — that would make this whole sweep vacuous).
MIGREF=$(cd "$SCRIPT_DIR/../.." && grep -c 'legacy="\$wt/\.harness/loop_status\.md"' tools/hooks/loop_lib.sh 2>/dev/null)
[ "$MIGREF" = "1" ] && ok "the excluded mention is the migration's legacy path (sweep is not vacuous)" || bad "migration legacy path not found: $MIGREF"

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
printf '%s' "$ENSURE_BODY" | grep -qE 'ln "\$_tmp" "\$p"|ln .*_tmp' \
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

# 28) codex r2 P2 — the U-HE-29 cutover must not STRAND still-open deferrals held in the
#     pre-U-HE-29 per-worktree ledgers. Import them, verbatim, exactly once.
# wt1/wt2 must be REAL linked worktrees: the migration enumerates them through
# `git worktree list`, which is the only thing that sees a pre-U-HE-29 ledger sitting in a
# checkout nobody is currently in. Plain directories would make this fixture pass a scan it
# never actually exercised. Git identity is passed inline -- CI has none configured.
MIG="$REPO/mig"; rm -rf "$MIG"; mkdir -p "$MIG"
( cd "$MIG" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b wt1br wt1 && git worktree add -q -b wt2br wt2 ) >/dev/null 2>&1
mkdir -p "$MIG/wt1/.harness" "$MIG/wt2/.harness"
cat > "$MIG/wt1/.harness/loop_status.md" <<'EOF'
# Loop status ledger
| timestamp | kind | detail |
|---|---|---|
| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-124 — still open in the old venue |
| 2026-08-01T00:01:00Z | DEFERRED-HIL | B-137 — also still open |
| 2026-08-01T00:02:00Z | DEFERRED-HIL | B-140 — this one was answered |
| 2026-08-01T00:03:00Z | RESOLVED-HIL | B-140 — answered before the cutover |
EOF
MIGV="$MIG/shared/loop_status.md"
OUT=$(cd "$MIG" && CLAUDE_PROJECT_DIR="$MIG" HARNESS_LOOP_STATUS_PATH="$MIGV" loop_status_migrate 2>&1)
SKIP=$(HARNESS_LOOP_STATUS_PATH="$MIGV" loop_skip_set)
[ "$SKIP" = "B-124 B-137" ] && ok "migration carries the still-open deferrals across ($SKIP)" || bad "stranded/extra rows: [$SKIP] — $OUT"
[ -f "$MIG/wt1/.harness/loop_status.md" ] && bad "legacy ledger left in place (can still collect writes)" || ok "legacy ledger retired after import"
[ -n "$(find "$MIG/wt1/.harness" -name 'loop_status.md.migrated-*' 2>/dev/null)" ] && ok "legacy ledger retained under a .migrated- name (nothing destroyed)" || bad "legacy ledger not preserved"
# idempotent: a second pass finds nothing to import and cannot double-count
OUT2=$(cd "$MIG" && CLAUDE_PROJECT_DIR="$MIG" HARNESS_LOOP_STATUS_PATH="$MIGV" loop_status_migrate 2>&1)
printf '%s' "$OUT2" | grep -q '0 file(s) imported' && ok "a second migration pass imports nothing" || bad "migration not idempotent: $OUT2"
[ "$(HARNESS_LOOP_STATUS_PATH="$MIGV" loop_skip_set)" = "B-124 B-137" ] && ok "skip-set unchanged after the second pass" || bad "second pass altered the skip-set"
# --dry-run reports without importing or retiring
cat > "$MIG/wt2/.harness/loop_status.md" <<'EOF'
| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-200 — a second worktree's open gate |
EOF
DRY=$(cd "$MIG" && CLAUDE_PROJECT_DIR="$MIG" HARNESS_LOOP_STATUS_PATH="$MIGV" loop_status_migrate --dry-run 2>&1)
printf '%s' "$DRY" | grep -q 'would import' && ok "--dry-run reports what it would import" || bad "--dry-run silent: $DRY"
[ -f "$MIG/wt2/.harness/loop_status.md" ] && ok "--dry-run retires nothing" || bad "--dry-run retired a legacy ledger"
printf '%s' "$(HARNESS_LOOP_STATUS_PATH="$MIGV" loop_skip_set)" | grep -q 'B-200' && bad "--dry-run imported rows" || ok "--dry-run imports nothing"

# 29) codex r4 P2 — the migration must FAIL CLOSED. "Could not read" and "nothing to read"
#     are different claims: swallowing the first archives a legacy ledger and reports a
#     completed cutover while its open gates disappear for good.
MIG2="$REPO/mig2"; rm -rf "$MIG2"; mkdir -p "$MIG2"
( cd "$MIG2" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b m2wt wt1 ) >/dev/null 2>&1
mkdir -p "$MIG2/wt1/.harness"
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-900 — unreadable gate |\n' > "$MIG2/wt1/.harness/loop_status.md"
chmod 000 "$MIG2/wt1/.harness/loop_status.md"
MIG2V="$MIG2/shared/loop_status.md"
( cd "$MIG2" && CLAUDE_PROJECT_DIR="$MIG2" HARNESS_LOOP_STATUS_PATH="$MIG2V" loop_status_migrate ) >/dev/null 2>&1
[ $? -ne 0 ] && ok "an unreadable legacy ledger fails the migration closed" || bad "unreadable ledger reported a successful migration"
chmod 644 "$MIG2/wt1/.harness/loop_status.md"
[ -f "$MIG2/wt1/.harness/loop_status.md" ] && ok "the unreadable ledger was NOT retired" || bad "ledger retired despite an unread import"
# ... and a git-enumeration failure must not read as "no worktrees, all done".
NOGIT=$(cd "$REPO" && CLAUDE_PROJECT_DIR="$REPO/definitely-not-a-repo" HARNESS_LOOP_STATUS_PATH="$MIG2V" loop_status_migrate 2>&1); RC=$?
[ "$RC" -ne 0 ] && ok "a worktree-enumeration failure fails the migration closed" || bad "enumeration failure reported success: $NOGIT"

# 30) codex r4 P2 — `;` terminates the lane in rowparse, so it must never survive into the
#     column: two distinct lanes would otherwise render as the same truncated id.
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
loop_log_structured DEFERRED-HIL 'lane;evil' 'g:f:c' "B-14 — semicolon lane"
[[ "$(loop_pending_hil_list)" == '[laneevil] B-14 — semicolon lane' ]] \
  && ok "a semicolon in the lane id is stripped, not truncated at read time" || bad "semicolon lane: [$(loop_pending_hil_list)]"
[ "$(loop_skip_set)" = "B-14" ] && ok "the gate survives a semicolon-bearing lane id" || bad "gate lost: [$(loop_skip_set)]"

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

# 33) codex r5 P2 — the migration CLAIMS a legacy ledger by rename before reading it. Reading
#     first left a window where a still-running pre-U-HE-29 writer's new deferral was carried
#     into the archive without ever reaching the shared venue, and later passes look only at
#     the original filename — so it would never be seen again.
MIG3="$REPO/mig3"; rm -rf "$MIG3"; mkdir -p "$MIG3"
( cd "$MIG3" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b m3wt wt1 ) >/dev/null 2>&1
mkdir -p "$MIG3/wt1/.harness"
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-301 — claimed gate |\n' > "$MIG3/wt1/.harness/loop_status.md"
MIG3V="$MIG3/shared/loop_status.md"
MBODY=$(declare -f loop_status_migrate)
printf '%s' "$MBODY" | grep -q 'migrating-' && ok "the migration claims by rename before reading" || bad "no claim-before-read rename"
( cd "$MIG3" && CLAUDE_PROJECT_DIR="$MIG3" HARNESS_LOOP_STATUS_PATH="$MIG3V" loop_status_migrate ) >/dev/null 2>&1
[ "$(HARNESS_LOOP_STATUS_PATH="$MIG3V" loop_skip_set)" = "B-301" ] && ok "the claimed ledger's gate reaches the shared venue" || bad "claimed gate lost"
[ -z "$(find "$MIG3/wt1/.harness" -name '*.migrating-*' 2>/dev/null)" ] && ok "no claim file is left behind on success" || bad "claim file leaked"

# 34) codex r5 P2 — a retry must not RE-OPEN a gate the operator resolved between passes.
#     A legacy ledger that reappears with the same item, after the operator answered the
#     imported row, must not be re-imported as a fresh DEFERRED-HIL.
HARNESS_LOOP_STATUS_PATH="$MIG3V" loop_resolve B-301 "operator answered it after the import" >/dev/null
[ -z "$(HARNESS_LOOP_STATUS_PATH="$MIG3V" loop_skip_set)" ] && ok "the imported gate is resolvable" || bad "could not resolve the imported gate"
# BYTE-IDENTICAL to the row already imported above — that is what makes it a retry rather
# than a new gate (r6 narrowed the dedupe from the item to the row; see test 37).
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-301 — claimed gate |\n' > "$MIG3/wt1/.harness/loop_status.md"
( cd "$MIG3" && CLAUDE_PROJECT_DIR="$MIG3" HARNESS_LOOP_STATUS_PATH="$MIG3V" loop_status_migrate ) >/dev/null 2>&1
[ -z "$(HARNESS_LOOP_STATUS_PATH="$MIG3V" loop_skip_set)" ] \
  && ok "a re-seen legacy row does not reopen a RESOLVED gate" || bad "retry reopened a resolved gate: [$(HARNESS_LOOP_STATUS_PATH="$MIG3V" loop_skip_set)]"

# 35) codex r5 P2 — the cutover residue must be gitignored, or hook_worktree_local_state
#     treats it as precious untracked state and the worktree GC refuses disposition forever.
IGN=$(cd "$SCRIPT_DIR/../.." && cat .gitignore)
printf '%s' "$IGN" | grep -q 'loop_status\.md\.migrated-\*' && ok "the .migrated- archive is gitignored" || bad "archive residue not ignored"
printf '%s' "$IGN" | grep -q 'loop_status\.md\.migrating-\*' && ok "the .migrating- claim is gitignored" || bad "claim residue not ignored"

# 36) codex r6 P2 — an ORPHANED claim must be recovered. A crash between the claim rename
#     and the retire leaves a `.migrating-*` file that later passes never inspect (they look
#     only at the original name), so the sole legacy ledger would be permanently invisible.
MIG4="$REPO/mig4"; rm -rf "$MIG4"; mkdir -p "$MIG4"
( cd "$MIG4" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b m4wt wt1 ) >/dev/null 2>&1
mkdir -p "$MIG4/wt1/.harness"
MIG4V="$MIG4/shared/loop_status.md"
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-401 — orphaned by a crash |\n' \
  > "$MIG4/wt1/.harness/loop_status.md.migrating-2026-08-01T00:00:00Z"
( cd "$MIG4" && CLAUDE_PROJECT_DIR="$MIG4" HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_status_migrate ) >/dev/null 2>&1
[ "$(HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_skip_set)" = "B-401" ] && ok "an orphaned claim is recovered and imported" || bad "orphaned claim stranded"
[ -z "$(find "$MIG4/wt1/.harness" -name '*.migrating-*' 2>/dev/null)" ] && ok "the recovered claim is not left behind" || bad "claim still present after recovery"
# ... and when a concurrent old writer already recreated the live path, NEITHER file's rows
# may be discarded.
printf '| 2026-08-02T00:00:00Z | DEFERRED-HIL | B-402 — orphan rows |\n' \
  > "$MIG4/wt1/.harness/loop_status.md.migrating-2026-08-02T00:00:00Z"
printf '| 2026-08-02T00:01:00Z | DEFERRED-HIL | B-403 — live rows |\n' \
  > "$MIG4/wt1/.harness/loop_status.md"
( cd "$MIG4" && CLAUDE_PROJECT_DIR="$MIG4" HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_status_migrate ) >/dev/null 2>&1
SK=$(HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_skip_set)
{ printf '%s' "$SK" | grep -q 'B-402' && printf '%s' "$SK" | grep -q 'B-403'; } \
  && ok "an orphan colliding with a recreated live ledger loses neither's rows" || bad "rows lost in the collision path: [$SK]"

# 37) codex r5->r6->r7 P2 — STALENESS decides, not text similarity. Imported rows are
#     appended LAST and the reducers key on physical order, so an old legacy DEFERRED-HIL
#     would land after a newer shared RESOLVED-HIL and reopen an answered gate. Both dedupe
#     heuristics tried before this broke the other direction (by item: every future legacy
#     deferral suppressed forever; by detail text: a real re-deferral that repeated its
#     reason suppressed). The timestamps settle it exactly.
loop_now() { echo "2026-08-10T00:00:00Z"; }
HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_resolve B-403 "answered at 08-10" >/dev/null
# (a) a legacy row written BEFORE the resolution is stale — it must NOT reopen the gate,
#     even though its text differs from anything imported so far.
printf '| 2026-08-03T00:00:00Z | DEFERRED-HIL | B-403 — written before the answer |\n' \
  > "$MIG4/wt1/.harness/loop_status.md"
( cd "$MIG4" && CLAUDE_PROJECT_DIR="$MIG4" HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_status_migrate ) >/dev/null 2>&1
printf '%s' "$(HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_skip_set)" | grep -q 'B-403' \
  && bad "a legacy row older than the resolution reopened the gate" || ok "a legacy row older than the resolution is stale and skipped"
# (b) a legacy row written AFTER the resolution is a genuinely NEW gate — last-write-wins
#     says it reopens, and it must be imported even though the item was resolved.
printf '| 2026-08-20T00:00:00Z | DEFERRED-HIL | B-403 — a new gate raised after the answer |\n' \
  > "$MIG4/wt1/.harness/loop_status.md"
( cd "$MIG4" && CLAUDE_PROJECT_DIR="$MIG4" HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_status_migrate ) >/dev/null 2>&1
printf '%s' "$(HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_skip_set)" | grep -q 'B-403' \
  && ok "a legacy row newer than the resolution reopens the gate (last-write-wins)" || bad "a genuinely newer legacy deferral was suppressed"
# (b2) codex r10 P2 — EQUAL timestamps must IMPORT. loop_now has one-second precision, so a
#      legacy deferral written just after a resolution can carry the same stamp; skipping on
#      equality would archive a genuinely newer gate. Importing on equality at worst reopens
#      an answered one, which is §4's safe direction.
printf '| 2026-08-10T00:00:00Z | DEFERRED-HIL | B-403 — raised in the SAME second as the answer |\n' \
  > "$MIG4/wt1/.harness/loop_status.md"
HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_resolve B-403 "answered again at 08-10" >/dev/null
( cd "$MIG4" && CLAUDE_PROJECT_DIR="$MIG4" HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_status_migrate ) >/dev/null 2>&1
printf '%s' "$(HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_skip_set)" | grep -q 'B-403' \
  && ok "a same-second legacy deferral is imported, not skipped as stale" || bad "equal timestamps skipped a gate"

# (c) an unresolved item is imported regardless of age — staleness is only about resolutions.
printf '| 2026-01-01T00:00:00Z | DEFERRED-HIL | B-404 — ancient but never answered |\n' \
  > "$MIG4/wt1/.harness/loop_status.md"
( cd "$MIG4" && CLAUDE_PROJECT_DIR="$MIG4" HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_status_migrate ) >/dev/null 2>&1
printf '%s' "$(HARNESS_LOOP_STATUS_PATH="$MIG4V" loop_skip_set)" | grep -q 'B-404' \
  && ok "an old but never-answered gate is imported" || bad "an unresolved legacy gate was dropped as stale"
unset -f loop_now; loop_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# 38) codex r6 P2 — the staging file is created EXCLUSIVELY. `$$` is shared across a bash's
#     subshells and $RANDOM is 15 bits, so a guessable name lets two callers write one inode
#     and publish it half-written — the very race the ln protocol removes.
printf '%s' "$(declare -f loop_status_ensure)" | grep -q 'mktemp' \
  && ok "the staging file is created exclusively (mktemp)" || bad "staging name is guessable"
# BEHAVIOURAL (codex r16 P3): when mktemp cannot supply an exclusive name the venue must NOT
# be created through a guessable fallback — that fallback was the very race this removes.
printf '%s' "$(declare -f loop_status_ensure)" | grep -q '\$\$-\${RANDOM}' \
  && bad "loop_status_ensure still falls back to a guessable staging name" \
  || ok "no guessable staging fallback remains"
MKFAIL="$REPO/mkfail"; rm -rf "$MKFAIL"; mkdir -p "$MKFAIL/bin"
printf '#!/bin/sh\nexit 1\n' > "$MKFAIL/bin/mktemp"; chmod +x "$MKFAIL/bin/mktemp"
MKV="$MKFAIL/venue/loop_status.md"
( PATH="$MKFAIL/bin:$PATH" HARNESS_LOOP_STATUS_PATH="$MKV" loop_status_ensure ) >/dev/null 2>&1
[ ! -e "$MKV" ] && ok "a failed mktemp creates no venue instead of using a guessable name" || bad "venue created via the unsafe fallback"

# 39) codex r7 P2 — an orphaned claim's rows are OLDER than a recreated live ledger's, so
#     they must be folded in FIRST. Appended last, an old RESOLVED-HIL in the orphan would
#     clear a NEWER DEFERRED-HIL in the live file and both would be archived with the real
#     gate unimported.
MIG5="$REPO/mig5"; rm -rf "$MIG5"; mkdir -p "$MIG5"
( cd "$MIG5" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b m5wt wt1 ) >/dev/null 2>&1
mkdir -p "$MIG5/wt1/.harness"
MIG5V="$MIG5/shared/loop_status.md"
# The orphan RESOLVED B-501 at 08-01; the live file re-DEFERRED it at 08-05. Correct order
# leaves B-501 PENDING; the wrong order (orphan appended last) would clear it.
printf '| 2026-08-01T00:00:00Z | RESOLVED-HIL | B-501 — answered long ago |\n' \
  > "$MIG5/wt1/.harness/loop_status.md.migrating-2026-08-01T00:00:00Z"
printf '| 2026-08-05T00:00:00Z | DEFERRED-HIL | B-501 — raised again, still open |\n' \
  > "$MIG5/wt1/.harness/loop_status.md"
( cd "$MIG5" && CLAUDE_PROJECT_DIR="$MIG5" HARNESS_LOOP_STATUS_PATH="$MIG5V" loop_status_migrate ) >/dev/null 2>&1
[ "$(HARNESS_LOOP_STATUS_PATH="$MIG5V" loop_skip_set)" = "B-501" ] \
  && ok "an orphan folds in BEFORE the recreated live rows (newer gate survives)" || bad "orphan ordering cleared a newer gate: [$(HARNESS_LOOP_STATUS_PATH="$MIG5V" loop_skip_set)]"
[ -z "$(find "$MIG5/wt1/.harness" -name '*.merge-*' 2>/dev/null)" ] && ok "no merge temp is left behind" || bad "merge temp leaked"

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

# 42) codex r8 P2 — MULTIPLE orphaned claims must fold in CHRONOLOGICAL order. Folding them
#     one at a time (each prepended) reversed the order, letting an older RESOLVED-HIL follow
#     and clear a newer DEFERRED-HIL.
MIG6="$REPO/mig6"; rm -rf "$MIG6"; mkdir -p "$MIG6"
( cd "$MIG6" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b m6wt wt1 ) >/dev/null 2>&1
mkdir -p "$MIG6/wt1/.harness"
MIG6V="$MIG6/shared/loop_status.md"
# The fixture must DISCRIMINATE, which the first cut of this test did not (merge-gate
# witness lens on this PR): with DEFER/RESOLVE/DEFER on one item, a FULL reversal still
# leaves a DEFERRED-HIL row physically last, so the reducer returned the same skip-set under
# both the correct fold AND the exact prepend bug — the test would have stayed green through
# the regression it names. This shape discriminates: the RESOLVE is NEWEST, so correct
# chronology clears B-601 and leaves only B-602, while the prepend bug puts B-601's DEFER
# last and wrongly reopens it.
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-601 — raised first |\n' \
  > "$MIG6/wt1/.harness/loop_status.md.migrating-2026-08-01T00:00:00Z-999999-1"
printf '| 2026-08-02T00:00:00Z | DEFERRED-HIL | B-602 — a second, still-open item |\n' \
  > "$MIG6/wt1/.harness/loop_status.md.migrating-2026-08-02T00:00:00Z-999999-2"
printf '| 2026-08-03T00:00:00Z | RESOLVED-HIL | B-601 — answered LAST |\n' \
  > "$MIG6/wt1/.harness/loop_status.md.migrating-2026-08-03T00:00:00Z-999999-3"
( cd "$MIG6" && CLAUDE_PROJECT_DIR="$MIG6" HARNESS_LOOP_STATUS_PATH="$MIG6V" loop_status_migrate ) >/dev/null 2>&1
[ "$(HARNESS_LOOP_STATUS_PATH="$MIG6V" loop_skip_set)" = "B-602" ] \
  && ok "three orphaned claims fold oldest-first (newest RESOLVE wins; only B-602 stays open)" \
  || bad "orphan chronology wrong: [$(HARNESS_LOOP_STATUS_PATH="$MIG6V" loop_skip_set)] (expected B-602; B-601 present means the fold reversed)"
[ -z "$(find "$MIG6/wt1/.harness" -name '*.migrating-*' 2>/dev/null)" ] && ok "every folded claim is consumed" || bad "a claim survived the fold"

# 43) codex r8 P3 — an unreadable ledger must PROPAGATE, not read as empty, even when the
#     caller has not enabled pipefail (this library documents direct raw-shell use, and the
#     migration retires a file it believes it has fully read).
UNREAD="$REPO/unreadable-loop_status.md"
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-700 — hidden |\n' > "$UNREAD"
chmod 000 "$UNREAD"
( set +o pipefail; _loop_pending_rows_with_ts "$UNREAD" >/dev/null 2>&1 )
[ $? -ne 0 ] && ok "an unreadable ledger propagates failure without pipefail" || bad "unreadable ledger read as empty"
chmod 644 "$UNREAD"; rm -f "$UNREAD"

# 44) codex r9 P2 — `--dry-run` must mutate NOTHING. It previously fell through the orphan
#     fold (which rewrites the live legacy file and deletes claims) before reaching its own
#     check, and called loop_status_ensure, which materializes the shared venue — so the
#     read-only mode rewrote exactly the state an operator runs it to inspect.
MIG7="$REPO/mig7"; rm -rf "$MIG7"; mkdir -p "$MIG7"
( cd "$MIG7" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b m7wt wt1 ) >/dev/null 2>&1
mkdir -p "$MIG7/wt1/.harness"
MIG7V="$MIG7/shared/loop_status.md"
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-801 — live row |\n' > "$MIG7/wt1/.harness/loop_status.md"
printf '| 2026-08-02T00:00:00Z | DEFERRED-HIL | B-802 — orphan row |\n' \
  > "$MIG7/wt1/.harness/loop_status.md.migrating-2026-08-02T00:00:00Z"
LIVE_BEFORE=$(cat "$MIG7/wt1/.harness/loop_status.md")
DRY=$(cd "$MIG7" && CLAUDE_PROJECT_DIR="$MIG7" HARNESS_LOOP_STATUS_PATH="$MIG7V" loop_status_migrate --dry-run 2>&1)
printf '%s' "$DRY" | grep -q 'would import' && ok "--dry-run reports what it would do" || bad "--dry-run silent: $DRY"
[ ! -e "$MIG7V" ] && ok "--dry-run does not create the shared venue" || bad "--dry-run created the venue"
[ "$(cat "$MIG7/wt1/.harness/loop_status.md")" = "$LIVE_BEFORE" ] && ok "--dry-run leaves the live legacy ledger byte-identical" || bad "--dry-run rewrote the legacy ledger"
[ -f "$MIG7/wt1/.harness/loop_status.md.migrating-2026-08-02T00:00:00Z" ] && ok "--dry-run leaves orphaned claims in place" || bad "--dry-run consumed an orphaned claim"
# and the real pass still works afterwards
( cd "$MIG7" && CLAUDE_PROJECT_DIR="$MIG7" HARNESS_LOOP_STATUS_PATH="$MIG7V" loop_status_migrate ) >/dev/null 2>&1
SK=$(HARNESS_LOOP_STATUS_PATH="$MIG7V" loop_skip_set)
{ printf '%s' "$SK" | grep -q 'B-801' && printf '%s' "$SK" | grep -q 'B-802'; } \
  && ok "a real pass after a dry-run imports both the live and orphaned rows" || bad "post-dry-run pass incomplete: [$SK]"

# 45) codex r11 P3 — a worktree path containing a SPACE must not break orphan recovery. The
#     live ledger used to join the fold list through an unquoted expansion, which word-split
#     such a path into several `cat` arguments and failed every retry.
MIG8="$REPO/mig 8"; rm -rf "$MIG8"; mkdir -p "$MIG8"
( cd "$MIG8" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b m8wt "wt one" ) >/dev/null 2>&1
mkdir -p "$MIG8/wt one/.harness"
MIG8V="$MIG8/shared/loop_status.md"
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-901 — orphan on a spaced path |\n' \
  > "$MIG8/wt one/.harness/loop_status.md.migrating-2026-08-01T00:00:00Z"
printf '| 2026-08-02T00:00:00Z | DEFERRED-HIL | B-902 — live on a spaced path |\n' \
  > "$MIG8/wt one/.harness/loop_status.md"
( cd "$MIG8" && CLAUDE_PROJECT_DIR="$MIG8" HARNESS_LOOP_STATUS_PATH="$MIG8V" loop_status_migrate ) >/dev/null 2>&1
SK=$(HARNESS_LOOP_STATUS_PATH="$MIG8V" loop_skip_set)
{ printf '%s' "$SK" | grep -q 'B-901' && printf '%s' "$SK" | grep -q 'B-902'; } \
  && ok "orphan recovery works on a worktree path containing a space" || bad "spaced path broke the fold: [$SK]"

# 46) codex r11 P3 — `--dry-run` must not turn an UNREADABLE ledger into "nothing to do".
UNREAD2="$MIG8/wt one/.harness/loop_status.md"
printf '| 2026-08-03T00:00:00Z | DEFERRED-HIL | B-903 — hidden |\n' > "$UNREAD2"
chmod 000 "$UNREAD2"
DRYOUT=$(cd "$MIG8" && CLAUDE_PROJECT_DIR="$MIG8" HARNESS_LOOP_STATUS_PATH="$MIG8V" loop_status_migrate --dry-run 2>&1); DRC=$?
chmod 644 "$UNREAD2"
[ "$DRC" -ne 0 ] && ok "--dry-run fails on an unreadable ledger instead of reporting clean" || bad "--dry-run reported clean over an unreadable ledger: $DRYOUT"

# 47) codex r11 P2 — `git worktree list`'s OWN status must be captured, not the pipeline's.
MBODY2=$(declare -f loop_status_migrate)
printf '%s' "$MBODY2" | grep -q 'wt_rc=$?' \
  && ok "git's own exit status is captured, not a pipeline's" || bad "git status masked by a pipeline"
printf '%s' "$MBODY2" | grep -q 'worktree list --porcelain -z' \
  && ok "worktrees are enumerated NUL-delimited" || bad "line-oriented porcelain still in use"
printf '%s' "$MBODY2" | grep -q 'read -r -d' \
  && ok "NUL records are read without command substitution (which drops NULs)" || bad "NUL output read through a NUL-dropping path"
# BEHAVIOURAL companion (merge-gate witness lens on this PR): the two greps above are text
# pins. git emits a newline-bearing worktree path RAW in non-`-z` porcelain (verified with
# `od -c` on git 2.39), so a line-oriented parse splits it into two nonexistent paths and
# that worktree's legacy ledger is silently skipped. A worktree literally named with a
# newline is the regression test the flag-grep cannot be.
NLR="$REPO/nlrepo"; rm -rf "$NLR"; mkdir -p "$NLR"
( cd "$NLR" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b nlwt "$(printf 'wt\nbroken')" ) >/dev/null 2>&1
NLWT="$NLR/$(printf 'wt\nbroken')"
if [ -d "$NLWT" ]; then
  mkdir -p "$NLWT/.harness"
  printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-995 — behind a newline-named worktree |\n' \
    > "$NLWT/.harness/loop_status.md"
  NLV="$NLR/shared/loop_status.md"
  ( cd "$NLR" && CLAUDE_PROJECT_DIR="$NLR" HARNESS_LOOP_STATUS_PATH="$NLV" loop_status_migrate ) >/dev/null 2>&1
  [ "$(HARNESS_LOOP_STATUS_PATH="$NLV" loop_skip_set)" = "B-995" ] \
    && ok "a newline-named worktree's legacy ledger is still drained" || bad "newline-named worktree skipped: [$(HARNESS_LOOP_STATUS_PATH="$NLV" loop_skip_set)]"
else
  ok "newline-named worktree not creatable on this filesystem — behavioural case skipped"
fi

# 48) codex r12 P2 — an UNREADABLE shared venue must not read as "nothing was ever
#     resolved". That would let every imported row reopen an answered gate, and the claim
#     must be restored so the next pass retries rather than archiving it unread.
MIG9="$REPO/mig9"; rm -rf "$MIG9"; mkdir -p "$MIG9"
( cd "$MIG9" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b m9wt wt1 ) >/dev/null 2>&1
mkdir -p "$MIG9/wt1/.harness" "$MIG9/shared"
MIG9V="$MIG9/shared/loop_status.md"
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-950 — pending |\n' > "$MIG9/wt1/.harness/loop_status.md"
printf '# Loop status ledger\n' > "$MIG9V"; chmod 000 "$MIG9V"
( cd "$MIG9" && CLAUDE_PROJECT_DIR="$MIG9" HARNESS_LOOP_STATUS_PATH="$MIG9V" loop_status_migrate ) >/dev/null 2>&1
RC=$?
chmod 644 "$MIG9V"
[ "$RC" -ne 0 ] && ok "an unreadable shared venue fails the import closed" || bad "unreadable shared venue treated as no-resolutions"
[ -f "$MIG9/wt1/.harness/loop_status.md" ] && ok "the claim is restored for the next pass" || bad "legacy ledger archived despite the failed import"

# 49) codex r12 P2 — the shared venue's resolutions are scanned ONCE per migration, not once
#     per imported row. The per-row form was O(rows x ledger), and SessionStart runs this
#     inside an 8 s bounded slice that swallows a timeout — a large cutover could have cost
#     the operator the entire SessionStart emit.
# BEHAVIOURAL, not textual (codex r15 P2 caught the earlier version of this test counting
# call SITES — which stayed green while the map was rebuilt once per WORKTREE inside the
# loop). Stub the map builder to count invocations and migrate across THREE worktrees that
# each hold a legacy ledger: a correct pass reads the shared venue exactly once.
MIGC="$REPO/migc"; rm -rf "$MIGC"; mkdir -p "$MIGC"
( cd "$MIGC" && git init -q .   && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init   && git worktree add -q -b mc1 wt1 && git worktree add -q -b mc2 wt2 && git worktree add -q -b mc3 wt3 ) >/dev/null 2>&1
MIGCV="$MIGC/shared/loop_status.md"
for n in 1 2 3; do
  mkdir -p "$MIGC/wt$n/.harness"
  printf '| 2026-08-0%s T00:00:00Z | DEFERRED-HIL | B-98%s — from wt%s |
' "$n" "$n" "$n"     | sed 's/ T/T/' > "$MIGC/wt$n/.harness/loop_status.md"
done
MAP_CALLS="$REPO/map-calls"; : > "$MAP_CALLS"
_orig_map=$(declare -f _loop_resolved_map)
_loop_resolved_map() { echo x >> "$MAP_CALLS"; return 0; }
( cd "$MIGC" && CLAUDE_PROJECT_DIR="$MIGC" HARNESS_LOOP_STATUS_PATH="$MIGCV" loop_status_migrate ) >/dev/null 2>&1
eval "$_orig_map"
[ "$(grep -c . "$MAP_CALLS")" = "1" ]   && ok "the shared venue's resolutions are read ONCE for the whole migration"   || bad "resolved-map rebuilt per worktree: $(grep -c . "$MAP_CALLS") call(s)"
SKC=$(HARNESS_LOOP_STATUS_PATH="$MIGCV" loop_skip_set)
{ printf '%s' "$SKC" | grep -q 'B-981' && printf '%s' "$SKC" | grep -q 'B-983'; }   && ok "all three worktrees' gates still import under the single-scan form" || bad "a worktree was skipped: [$SKC]"

# 50) codex r12 P2 — the claim name is unique per ATTEMPT, so two migrations in the same
#     second cannot overwrite each other's claim and discard the loser's rows unread.
printf '%s' "$(declare -f loop_status_migrate)" | grep -q 'migrating-$(loop_now)-\$\$-' \
  && ok "the claim name carries a per-attempt suffix" || bad "claim name is only second-resolution"

# 51) codex r13 P2 — the ARCHIVE name is unique per attempt too. Two migrators retiring
#     successive recreations of one legacy ledger inside a single second would otherwise
#     `mv` to the same `.migrated-<ts>` path and the later would overwrite the first,
#     destroying the retained history the archive exists to keep.
printf '%s' "$(declare -f loop_status_migrate)" | grep -q 'migrated-$(loop_now)-\$\$-' \
  && ok "the archive name carries a per-attempt suffix" || bad "archive name is only second-resolution"
# two retirements in the same stubbed second must leave TWO archives, not one
MIGA="$REPO/miga"; rm -rf "$MIGA"; mkdir -p "$MIGA"
( cd "$MIGA" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b mawt wt1 ) >/dev/null 2>&1
mkdir -p "$MIGA/wt1/.harness"
MIGAV="$MIGA/shared/loop_status.md"
loop_now() { echo "2026-08-11T00:00:00Z"; }
printf '| 2026-08-11T00:00:00Z | DEFERRED-HIL | B-960 — first recreation |\n' > "$MIGA/wt1/.harness/loop_status.md"
( cd "$MIGA" && CLAUDE_PROJECT_DIR="$MIGA" HARNESS_LOOP_STATUS_PATH="$MIGAV" loop_status_migrate ) >/dev/null 2>&1
printf '| 2026-08-11T00:00:00Z | DEFERRED-HIL | B-961 — second recreation, same second |\n' > "$MIGA/wt1/.harness/loop_status.md"
( cd "$MIGA" && CLAUDE_PROJECT_DIR="$MIGA" HARNESS_LOOP_STATUS_PATH="$MIGAV" loop_status_migrate ) >/dev/null 2>&1
[ "$(find "$MIGA/wt1/.harness" -name '*.migrated-*' | wc -l | tr -d ' ')" = "2" ] \
  && ok "two same-second retirements keep BOTH archives" || bad "an archive was overwritten: $(find "$MIGA/wt1/.harness" -name '*.migrated-*' | wc -l | tr -d ' ')"
SKA=$(HARNESS_LOOP_STATUS_PATH="$MIGAV" loop_skip_set)
{ printf '%s' "$SKA" | grep -q 'B-960' && printf '%s' "$SKA" | grep -q 'B-961'; } \
  && ok "both recreations' gates reach the shared venue" || bad "a same-second recreation was lost: [$SKA]"
unset -f loop_now; loop_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# 52) codex r14 P2 — LEGACY files are reduced under LEGACY semantics. Those rows were written
#     when ACTIVATE cleared prior-run state, so a DEFERRED-HIL followed by an ACTIVATE was
#     already not pending. Reducing with the new no-reset rule would RESURRECT it into the
#     shared skip-set and make the loop refuse an item nobody was ever gated on.
LEG="$REPO/legacy-semantics.md"
cat > "$LEG" <<'EOF'
| ts | kind | detail |
|---|---|---|
| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-970 — deferred in a PRIOR run |
| 2026-08-02T00:00:00Z | ACTIVATE | a new run begins |
| 2026-08-03T00:00:00Z | DEFERRED-HIL | B-971 — deferred in THIS run |
EOF
LEGOUT=$(_loop_pending_rows_with_ts "$LEG")
printf '%s' "$LEGOUT" | grep -q 'B-971' && ok "a post-ACTIVATE legacy deferral is still pending" || bad "post-ACTIVATE row lost: [$LEGOUT]"
printf '%s' "$LEGOUT" | grep -q 'B-970' && bad "a pre-ACTIVATE legacy deferral was resurrected: [$LEGOUT]" || ok "a pre-ACTIVATE legacy deferral is NOT resurrected"
# ... while the SHARED venue keeps the new semantics (C-HE-09 §4): ACTIVATE resets nothing.
: > "$(loop_status_path)"; loop_status_ensure >/dev/null
loop_defer B-972 "deferred before the activate"
loop_activate "new run" >/dev/null
[ "$(loop_skip_set)" = "B-972" ] && ok "the SHARED venue still ignores ACTIVATE (§4 unchanged)" || bad "shared-venue semantics regressed: [$(loop_skip_set)]"
# and the migration honours the legacy boundary end-to-end
MIGB="$REPO/migb"; rm -rf "$MIGB"; mkdir -p "$MIGB"
( cd "$MIGB" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b mbwt wt1 ) >/dev/null 2>&1
mkdir -p "$MIGB/wt1/.harness"
MIGBV="$MIGB/shared/loop_status.md"
cp "$LEG" "$MIGB/wt1/.harness/loop_status.md"
( cd "$MIGB" && CLAUDE_PROJECT_DIR="$MIGB" HARNESS_LOOP_STATUS_PATH="$MIGBV" loop_status_migrate ) >/dev/null 2>&1
[ "$(HARNESS_LOOP_STATUS_PATH="$MIGBV" loop_skip_set)" = "B-971" ] \
  && ok "migration imports only what was pending under the OLD rule" || bad "migration resurrected a pre-ACTIVATE row: [$(HARNESS_LOOP_STATUS_PATH="$MIGBV" loop_skip_set)]"

# 53) codex r16 P2 — a claim whose OWNER IS ALIVE is not an orphan. Two concurrent
#     migrations would otherwise fold and delete each other's in-flight claim, duplicating
#     rows and breaking the first migrator's retirement. A real background process stands in
#     for "another migrator, still running" — a pid we own, alive, and not this shell.
MIGD="$REPO/migd"; rm -rf "$MIGD"; mkdir -p "$MIGD"
( cd "$MIGD" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b mdwt wt1 ) >/dev/null 2>&1
mkdir -p "$MIGD/wt1/.harness"
MIGDV="$MIGD/shared/loop_status.md"
sleep 30 & LIVEPID=$!
LIVE_CLAIM="$MIGD/wt1/.harness/loop_status.md.migrating-2026-08-02T00:00:00Z-${LIVEPID}-7"
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-991 — in flight elsewhere |\n' > "$LIVE_CLAIM"
( cd "$MIGD" && CLAUDE_PROJECT_DIR="$MIGD" HARNESS_LOOP_STATUS_PATH="$MIGDV" loop_status_migrate ) >/dev/null 2>&1
[ -f "$LIVE_CLAIM" ] && ok "a claim owned by a LIVE pid is left for its owner" || bad "a live migrator's claim was stolen"
[ -z "$(HARNESS_LOOP_STATUS_PATH="$MIGDV" loop_skip_set)" ] && ok "the live claim's rows are not double-imported" || bad "live claim imported behind its owner's back"
# ... while a claim from a DEAD pid is genuinely orphaned and IS recovered.
kill "$LIVEPID" 2>/dev/null; wait "$LIVEPID" 2>/dev/null
DEAD_CLAIM="$MIGD/wt1/.harness/loop_status.md.migrating-2026-08-03T00:00:00Z-999999-7"
mv "$LIVE_CLAIM" "$DEAD_CLAIM"
( cd "$MIGD" && CLAUDE_PROJECT_DIR="$MIGD" HARNESS_LOOP_STATUS_PATH="$MIGDV" loop_status_migrate ) >/dev/null 2>&1
[ "$(HARNESS_LOOP_STATUS_PATH="$MIGDV" loop_skip_set)" = "B-991" ] \
  && ok "a claim from a DEAD pid is recovered and imported" || bad "dead-owner claim not recovered: [$(HARNESS_LOOP_STATUS_PATH="$MIGDV" loop_skip_set)]"

# 54) codex r16 P3 — orphan claims are sorted by BASENAME, so a worktree path containing a
#     newline cannot split the fold list into nonexistent filenames.
printf '%s' "$(declare -f loop_status_migrate)" | grep -q '{orphan##\*/}' \
  && ok "orphans sort by basename, never by full path" || bad "orphan sort still round-trips full paths through newlines"

# 55) codex re-gate P2 — "nothing to drain" and "a sibling is mid-drain" must be
#     DISTINGUISHABLE. The shared venue is INCOMPLETE while another migrator holds a claim,
#     and a closure record published from it would freeze a short todo list forever.
MIGE="$REPO/mige"; rm -rf "$MIGE"; mkdir -p "$MIGE"
( cd "$MIGE" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init \
  && git worktree add -q -b mewt wt1 ) >/dev/null 2>&1
mkdir -p "$MIGE/wt1/.harness"
MIGEV="$MIGE/shared/loop_status.md"
# clean pass over a worktree with nothing to drain -> 0
( cd "$MIGE" && CLAUDE_PROJECT_DIR="$MIGE" HARNESS_LOOP_STATUS_PATH="$MIGEV" loop_status_migrate ) >/dev/null 2>&1
[ $? -eq 0 ] && ok "a complete pass exits 0" || bad "clean pass did not exit 0"
# a claim held by a LIVE sibling -> 2 (incomplete), not 0 and not 1
sleep 30 & SIBPID=$!
printf '| 2026-08-01T00:00:00Z | DEFERRED-HIL | B-970 — sibling is importing this |\n' \
  > "$MIGE/wt1/.harness/loop_status.md.migrating-2026-08-01T00:00:00Z-${SIBPID}-1"
( cd "$MIGE" && CLAUDE_PROJECT_DIR="$MIGE" HARNESS_LOOP_STATUS_PATH="$MIGEV" loop_status_migrate ) >/dev/null 2>&1
[ $? -eq 2 ] && ok "a live sibling's claim makes the pass report INCOMPLETE (exit 2)" || bad "incomplete drain not distinguishable from a clean pass"
kill "$SIBPID" 2>/dev/null; wait "$SIBPID" 2>/dev/null
# once the sibling is gone the claim is recoverable and the pass completes -> 0
( cd "$MIGE" && CLAUDE_PROJECT_DIR="$MIGE" HARNESS_LOOP_STATUS_PATH="$MIGEV" loop_status_migrate ) >/dev/null 2>&1
[ $? -eq 0 ] && ok "the pass completes once the sibling is gone" || bad "pass still incomplete after the sibling exited"
[ "$(HARNESS_LOOP_STATUS_PATH="$MIGEV" loop_skip_set)" = "B-970" ] && ok "the sibling's row is drained by the later pass" || bad "row lost: [$(HARNESS_LOOP_STATUS_PATH="$MIGEV" loop_skip_set)]"

echo "----"
echo "loop_lib: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

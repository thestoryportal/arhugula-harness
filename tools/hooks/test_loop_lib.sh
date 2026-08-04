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
mkdir -p "$REPO/.harness"

# Source the libs against the fake project dir (lib.sh first, then loop_lib.sh).
export CLAUDE_PROJECT_DIR="$REPO"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
# shellcheck source=loop_lib.sh
. "$SCRIPT_DIR/loop_lib.sh"

# 1) Off by default (no marker, no env).
unset HARNESS_LOOP
loop_mode_active && bad "loop active with no marker/env" || ok "off by default"

# 2) Paths resolve under the fake project dir.
[ "$(loop_marker_path)" = "$REPO/.harness/.loop-active" ] && ok "marker path correct" || bad "marker path: $(loop_marker_path)"
[ "$(loop_status_path)" = "$REPO/.harness/loop_status.md" ] && ok "status path correct" || bad "status path: $(loop_status_path)"

# 3) activate → marker exists + loop_mode_active true + ledger created with header + ACTIVATE row.
loop_activate "test on"
[ -f "$REPO/.harness/.loop-active" ] && ok "activate creates marker" || bad "marker not created"
loop_mode_active && ok "loop_mode_active true after activate" || bad "still off after activate"
[ -f "$REPO/.harness/loop_status.md" ] && ok "ledger auto-created" || bad "ledger missing"
grep -q '^# Loop status ledger' "$REPO/.harness/loop_status.md" && ok "ledger has header" || bad "no header"
grep -q '| ACTIVATE | test on |' "$REPO/.harness/loop_status.md" && ok "ACTIVATE row appended" || bad "no ACTIVATE row"

# 4) loop_log appends a row; pipes in detail are escaped (one table row stays one row).
loop_log DEFERRED-HIL "needs ANTHROPIC_API_KEY | paid call"
grep -q '| DEFERRED-HIL | needs ANTHROPIC_API_KEY \\| paid call |' "$REPO/.harness/loop_status.md" \
  && ok "loop_log escapes pipes" || bad "pipe not escaped: $(grep DEFERRED "$REPO/.harness/loop_status.md")"

# 5) ledger is append-only (ensure does not clobber existing rows).
BEFORE=$(wc -l < "$REPO/.harness/loop_status.md")
loop_status_ensure >/dev/null
AFTER=$(wc -l < "$REPO/.harness/loop_status.md")
[ "$BEFORE" = "$AFTER" ] && ok "ensure is idempotent (no clobber)" || bad "ensure clobbered: $BEFORE -> $AFTER"

# 6) deactivate → marker gone + loop_mode_active false + DEACTIVATE row.
loop_deactivate "test off"
[ -f "$REPO/.harness/.loop-active" ] && bad "marker still present after deactivate" || ok "deactivate removes marker"
loop_mode_active && bad "still on after deactivate" || ok "off after deactivate"
grep -q '| DEACTIVATE | test off |' "$REPO/.harness/loop_status.md" && ok "DEACTIVATE row appended" || bad "no DEACTIVATE row"

# 7) HARNESS_LOOP=1 forces loop mode on even with no marker.
HARNESS_LOOP=1 loop_mode_active && ok "HARNESS_LOOP=1 forces on" || bad "env override failed"

# 8) loop_defer writes a parseable DEFERRED-HIL row with the item-id as the leading token.
: > "$(loop_status_path)"
loop_activate "skip-set test" >/dev/null
loop_defer R-410 "needs container runtime — built: design half"
grep -qE '\| DEFERRED-HIL \| R-410 — needs container' "$(loop_status_path)" && ok "loop_defer writes item-id-leading DEFERRED-HIL row" || bad "loop_defer row malformed"

# 9) loop_skip_set = sorted-unique item-ids deferred SINCE the last ACTIVATE.
loop_defer R-300 "needs OpenAI creds"
SKIP=$(loop_skip_set)
[ "$SKIP" = "R-300 R-410" ] && ok "loop_skip_set lists current-run deferrals ($SKIP)" || bad "skip_set wrong: [$SKIP]"

# 10) A new ACTIVATE scopes the skip-set to the NEW run (prior deferrals excluded).
loop_activate "second run" >/dev/null
loop_defer R-815 "needs vendor pick"
SKIP=$(loop_skip_set)
[ "$SKIP" = "R-815" ] && ok "skip-set scoped to current run (excludes pre-ACTIVATE)" || bad "scoping wrong: [$SKIP]"

# 11) loop_pending_hil_summary: populated (with item + count) when deferrals exist.
SUM=$(loop_pending_hil_summary)
printf '%s' "$SUM" | grep -q "R-815" && printf '%s' "$SUM" | grep -q "await your input" \
  && ok "pending summary lists current-run deferral" || bad "pending summary missing/malformed: $SUM"

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
grep -qF '| RESOLVED-HIL | R-410 — ratified via council dyad |' "$(loop_status_path)" && ok "the RESOLVED-HIL row itself is still present (never deleted)" || bad "RESOLVED-HIL row missing after a later DEFERRED-HIL"

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

# 17d) The list obeys the SAME semantics as the summary/skip-set: RESOLVED clears, a new
#      ACTIVATE scopes to the current run, and only the leading token keys the item.
loop_resolve R-103 "answered" >/dev/null
LIST=$(loop_pending_hil_list)
printf '%s' "$LIST" | grep -q 'R-103' && bad "resolved item still in the list: [$LIST]" || ok "loop_pending_hil_list drops a RESOLVED item"
[ "$(printf '%s\n' "$LIST" | grep -c .)" -eq 4 ] && ok "list count drops to 4 after the resolve" || bad "list count after resolve: $(printf '%s\n' "$LIST" | grep -c .)"
loop_activate "list run 2" >/dev/null
[ -z "$(loop_pending_hil_list)" ] && ok "a new ACTIVATE scopes the list to the new run (empty)" || bad "list not run-scoped: [$(loop_pending_hil_list)]"

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
[ "$LP" = "R-PIPE — choose A | B carefully" ] \
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

echo "----"
echo "loop_lib: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

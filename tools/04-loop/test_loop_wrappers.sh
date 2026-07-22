#!/usr/bin/env bash
# Hermetic test for the loop-control wrappers (U-HK-14/15): tools/04-loop/defer.sh +
# tools/04-loop/resolve.sh + tools/04-loop/halt.sh. These are the allowlisted,
# single-invocation entry points the autonomous loop uses to record a per-item
# deferral/resolution and to stand the run down — the executable path that replaced the
# denied/malformed raw `source … && loop_defer …`.
# Asserts they source BOTH libs correctly (functions defined), write the ledger, raise
# the halt marker, and reject a no-arg defer/resolve.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFER="$SCRIPT_DIR/defer.sh"
RESOLVE="$SCRIPT_DIR/resolve.sh"
HALT="$SCRIPT_DIR/halt.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"; { [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL mktemp"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
mkdir -p "$REPO/.harness"
LEDGER="$REPO/.harness/loop_status.md"

# 1) defer.sh writes a DEFERRED-HIL row with the item-id leading — even when the reason
#    mentions "credentials" (the wrapper only logs; it must not be self-censored).
CLAUDE_PROJECT_DIR="$REPO" bash "$DEFER" R-410 "needs container runtime — built: design half" >/dev/null 2>&1
CLAUDE_PROJECT_DIR="$REPO" bash "$DEFER" R-300 "needs OpenAI credentials" >/dev/null 2>&1
grep -qE '\| DEFERRED-HIL \| R-410 — needs container' "$LEDGER" && ok "defer.sh writes R-410 row" || bad "R-410 row missing"
grep -qE '\| DEFERRED-HIL \| R-300 — needs OpenAI credentials' "$LEDGER" && ok "defer.sh writes a 'credentials' reason verbatim" || bad "R-300 credentials row missing"

# 2) the skip-set reads back both item-ids (functions were actually defined → libs sourced).
SKIP=$(cd "$REPO" && . "$SCRIPT_DIR/../hooks/lib.sh" && . "$SCRIPT_DIR/../hooks/loop_lib.sh" && CLAUDE_PROJECT_DIR="$REPO" loop_skip_set)
printf '%s' "$SKIP" | grep -q "R-410" && printf '%s' "$SKIP" | grep -q "R-300" \
  && ok "deferrals readable as skip-set ($SKIP)" || bad "skip-set wrong: [$SKIP]"

# 3) defer.sh with no args → usage error (exit 2), no malformed row.
CLAUDE_PROJECT_DIR="$REPO" bash "$DEFER" >/dev/null 2>&1 && bad "no-arg defer.sh did not error" || ok "no-arg defer.sh exits nonzero"

# 3b) defer.sh with an item but NO reason → error + no row (a reason-less deferral would
#     skip the item while giving the operator nothing actionable at SessionStart).
CLAUDE_PROJECT_DIR="$REPO" bash "$DEFER" R-555 >/dev/null 2>&1 && bad "reason-less defer.sh accepted" || ok "reason-less defer.sh exits nonzero"
CLAUDE_PROJECT_DIR="$REPO" bash "$DEFER" R-555 "" >/dev/null 2>&1 && bad "empty-reason defer.sh accepted" || ok "empty-reason defer.sh exits nonzero"
grep -q "R-555" "$LEDGER" && bad "reason-less R-555 row was written" || ok "no reason-less row written"

# 4) resolve.sh writes a RESOLVED-HIL row and clears the item from the skip-set —
#    matching loop_resolve's last-write-wins semantics, exercised through the actual
#    guard-allowlisted entry point rather than the sourced function directly.
CLAUDE_PROJECT_DIR="$REPO" bash "$RESOLVE" R-410 "ratified via council dyad — see PR #1234" >/dev/null 2>&1
grep -qE '\| RESOLVED-HIL \| R-410 — ratified via council dyad' "$LEDGER" && ok "resolve.sh writes R-410 row" || bad "R-410 resolved row missing"
SKIP=$(cd "$REPO" && . "$SCRIPT_DIR/../hooks/lib.sh" && . "$SCRIPT_DIR/../hooks/loop_lib.sh" && CLAUDE_PROJECT_DIR="$REPO" loop_skip_set)
[ "$SKIP" = "R-300" ] && ok "resolve.sh clears R-410 from skip-set ($SKIP)" || bad "skip-set not cleared: [$SKIP]"

# 4b) resolve.sh with no args / no note → usage error (exit 2), no malformed row.
CLAUDE_PROJECT_DIR="$REPO" bash "$RESOLVE" >/dev/null 2>&1 && bad "no-arg resolve.sh did not error" || ok "no-arg resolve.sh exits nonzero"
CLAUDE_PROJECT_DIR="$REPO" bash "$RESOLVE" R-999 >/dev/null 2>&1 && bad "note-less resolve.sh accepted" || ok "note-less resolve.sh exits nonzero"
CLAUDE_PROJECT_DIR="$REPO" bash "$RESOLVE" R-999 "" >/dev/null 2>&1 && bad "empty-note resolve.sh accepted" || ok "empty-note resolve.sh exits nonzero"
grep -q "R-999" "$LEDGER" && bad "note-less R-999 row was written" || ok "no note-less resolved row written"

# 5) halt.sh raises the halt marker + logs a STOP row.
CLAUDE_PROJECT_DIR="$REPO" bash "$HALT" "forward menu exhausted — 2 awaiting input" >/dev/null 2>&1
[ -f "$REPO/.harness/.loop-halt" ] && ok "halt.sh raises .loop-halt" || bad ".loop-halt not raised"
grep -q '| STOP | forward menu exhausted' "$LEDGER" && ok "halt.sh logs STOP reason" || bad "STOP not logged"

echo "----"
echo "loop_wrappers: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

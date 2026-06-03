#!/usr/bin/env bash
# Hermetic test for stop-loop.sh (U-HK-14). Asserts: inert off-mode, continue-with-
# next-action in loop mode, halt-marker stand-down, iteration-cap termination, and the
# counter increments per turn.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/stop-loop.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"; { [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL mktemp"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
mkdir -p "$REPO/.harness"
# Minimal dashboard with a Next action section carrying an R-id.
cat > "$REPO/.harness/roadmap_status.md" <<'EOF'
## Next action
Drive `R-410` next.
---
EOF

run_on()  { printf '{}' | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"; }
run_off() { printf '{}' | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"; }
unset HARNESS_LOOP

# 1) INERT off-mode.
OUT=$(run_off); [ -z "$OUT" ] && ok "inert off-mode" || bad "spoke off-mode: $OUT"

# 2) Continue: blocks + injects next-action; counter → 1.
OUT=$(run_on)
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "blocks to continue in loop mode" || bad "did not block: $OUT"
echo "$OUT" | jq -e '.reason | test("R-410")' >/dev/null 2>&1 && ok "injects next-action R-410" || bad "no next-action: $OUT"
[ "$(cat "$REPO/.harness/.loop-iter")" = "1" ] && ok "counter incremented to 1" || bad "counter wrong: $(cat "$REPO/.harness/.loop-iter" 2>/dev/null)"

# 3) Counter increments per turn.
run_on >/dev/null; run_on >/dev/null
[ "$(cat "$REPO/.harness/.loop-iter")" = "3" ] && ok "counter increments per turn (=3)" || bad "counter=$(cat "$REPO/.harness/.loop-iter")"

# 4) Iteration cap → stop + reset (HARNESS_LOOP_MAX=2 with counter already 3).
OUT=$(printf '{}' | HARNESS_LOOP=1 HARNESS_LOOP_MAX=2 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && ok "iteration cap → allows stop" || bad "blocked past cap: $OUT"
[ ! -f "$REPO/.harness/.loop-iter" ] && ok "counter reset at cap" || bad "counter not reset"
grep -q '| STOP | iteration cap' "$REPO/.harness/loop_status.md" && ok "cap logged to ledger" || bad "cap not logged"

# 5) Halt marker → stand down (allow stop) + marker cleared.
: > "$REPO/.harness/.loop-halt"
OUT=$(run_on)
[ -z "$OUT" ] && ok "halt marker → allows stop" || bad "blocked despite halt: $OUT"
[ ! -f "$REPO/.harness/.loop-halt" ] && ok "halt marker cleared" || bad "halt marker not cleared"
grep -q '| STOP | halt marker' "$REPO/.harness/loop_status.md" && ok "halt logged to ledger" || bad "halt not logged"

# 6) Non-numeric HARNESS_LOOP_MAX must not break the cap (codex P2): falls back to 25,
#    so a counter ≥ 25 still stops instead of blocking forever.
printf '30' > "$REPO/.harness/.loop-iter"
OUT=$(printf '{}' | HARNESS_LOOP=1 HARNESS_LOOP_MAX=abc CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && ok "non-numeric MAX → defaults to 25, counter 30 stops" || bad "invalid MAX kept blocking: $OUT"

echo "----"
echo "stop_loop: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

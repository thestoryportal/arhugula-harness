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
[ -f "$REPO/.harness/.loop-halt" ] && ok "cap raises halt marker (real boundary)" || bad "cap did not raise halt marker"
grep -q '| STOP | iteration cap' "$REPO/.harness/loop_status.md" && ok "cap logged to ledger" || bad "cap not logged"
rm -f "$REPO/.harness/.loop-halt"

# 5) Halt marker → stand down (allow stop) + marker PRESERVED for the runner (codex P1:
#    the in-session hook must not consume the gate signal the outer runner needs to see).
: > "$REPO/.harness/.loop-halt"
OUT=$(run_on)
[ -z "$OUT" ] && ok "halt marker → allows stop" || bad "blocked despite halt: $OUT"
[ -f "$REPO/.harness/.loop-halt" ] && ok "halt marker preserved for runner" || bad "halt marker was consumed"
grep -q '| STOP | halt marker' "$REPO/.harness/loop_status.md" && ok "halt logged to ledger" || bad "halt not logged"
rm -f "$REPO/.harness/.loop-halt"

# 6) Non-numeric HARNESS_LOOP_MAX must not break the cap (codex P2): falls back to 25,
#    so a counter ≥ 25 still stops instead of blocking forever.
printf '30' > "$REPO/.harness/.loop-iter"
OUT=$(printf '{}' | HARNESS_LOOP=1 HARNESS_LOOP_MAX=abc CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK")
[ -z "$OUT" ] && ok "non-numeric MAX → defaults to 25, counter 30 stops" || bad "invalid MAX kept blocking: $OUT"

# 7) Skip-set injection (the defer-and-ADVANCE mechanism — the load-bearing fix). With a
#    ledger carrying DEFERRED-HIL rows SINCE the last ACTIVATE, the continue-reason must
#    carry those item-IDs (so a fresh headless `claude -p` child skips them off the static
#    pointer) and must instruct defer-and-advance, NOT halt-at-gate. A DEFERRED-HIL row
#    BEFORE the ACTIVATE is a prior run's — it must NOT leak into this run's skip-set.
rm -f "$REPO/.harness/.loop-iter" "$REPO/.harness/.loop-halt"
cat > "$REPO/.harness/loop_status.md" <<'EOF'
# ledger
| ts | kind | detail |
|---|---|---|
| t0 | DEFERRED-HIL | R-999 — prior run, must be excluded |
| t1 | ACTIVATE | this run |
| t2 | DEFERRED-HIL | R-410 — needs container runtime |
| t3 | DEFERRED-HIL | R-300 — needs OpenAI creds |
EOF
OUT=$(run_on)
echo "$OUT" | jq -e '.reason | test("ALREADY DEFERRED")'         >/dev/null 2>&1 && ok "reason carries the skip-set header" || bad "no skip-set header: $OUT"
echo "$OUT" | jq -e '.reason | test("R-410")'                    >/dev/null 2>&1 && ok "skip-set includes R-410 (this run)" || bad "R-410 missing from skip-set"
echo "$OUT" | jq -e '.reason | test("R-300")'                    >/dev/null 2>&1 && ok "skip-set includes R-300 (this run)" || bad "R-300 missing from skip-set"
echo "$OUT" | jq -e '.reason | test("R-999") | not'              >/dev/null 2>&1 && ok "skip-set EXCLUDES R-999 (pre-ACTIVATE)" || bad "R-999 leaked into skip-set: $OUT"
echo "$OUT" | jq -e '.reason | test("do NOT raise .loop-halt")'  >/dev/null 2>&1 && ok "instructs defer-NOT-halt at a gate" || bad "missing defer-not-halt guidance"
echo "$OUT" | jq -e '.reason | test("loop_defer")'               >/dev/null 2>&1 && ok "instructs loop_defer <item-id>" || bad "missing loop_defer guidance"
echo "$OUT" | jq -e '.reason | test("exhausted")'                >/dev/null 2>&1 && ok "exhaustion is the ONLY .loop-halt condition" || bad "missing exhaustion condition"

echo "----"
echo "stop_loop: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

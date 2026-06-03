#!/usr/bin/env bash
# Hermetic test for tools/loop/run.sh (U-HK-15). Fakes `claude` on PATH; asserts:
# dry-run never calls claude but exercises activate/deactivate + ledger, real mode caps
# iterations + calls the fake claude, a halt marker stops the loop early, and loop mode
# is OFF on exit.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="$SCRIPT_DIR/run.sh"
HOOKS="$(cd "$SCRIPT_DIR/../hooks" && pwd)"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"; { [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL mktemp"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
mkdir -p "$REPO/.harness" "$REPO/tools" "$REPO/bin"
# run.sh resolves the hooks libs relative to its own location, so point it at the real
# ones by copying the loop dir + symlinking hooks into the throwaway repo layout.
cp -R "$SCRIPT_DIR" "$REPO/tools/loop"
cp -R "$HOOKS" "$REPO/tools/hooks"
RUN="$REPO/tools/loop/run.sh"

# Fake claude: logs each call; if a sentinel file says so, drops a halt marker on call N.
cat > "$REPO/bin/claude" <<'EOF'
#!/usr/bin/env bash
echo "called" >> "$CLAUDE_PROJECT_DIR/.harness/claude_calls.log"
N=$(wc -l < "$CLAUDE_PROJECT_DIR/.harness/claude_calls.log" | tr -d ' ')
if [ -f "$CLAUDE_PROJECT_DIR/.harness/HALT_ON" ] && [ "$N" -ge "$(cat "$CLAUDE_PROJECT_DIR/.harness/HALT_ON")" ]; then
  : > "$CLAUDE_PROJECT_DIR/.harness/.loop-halt"
fi
EOF
chmod +x "$REPO/bin/claude"

calls() { wc -l < "$REPO/.harness/claude_calls.log" 2>/dev/null | tr -d ' ' || echo 0; }

# 1) Dry-run: never calls claude, but activates + logs + deactivates; loop mode OFF after.
OUT=$(CLAUDE_PROJECT_DIR="$REPO" DRY_ITERS=2 bash "$RUN" --dry-run --max 5 2>&1)
[ ! -f "$REPO/.harness/claude_calls.log" ] && ok "dry-run never calls claude" || bad "dry-run called claude ($(calls))"
echo "$OUT" | grep -q '\[dry-run\] iter 1/5' && ok "dry-run prints planned invocation" || bad "no dry-run line: $OUT"
[ ! -f "$REPO/.harness/.loop-active" ] && ok "loop mode OFF after dry-run" || bad "marker left active"
grep -q '| ACTIVATE |' "$REPO/.harness/loop_status.md" && grep -q '| DEACTIVATE |' "$REPO/.harness/loop_status.md" \
  && ok "dry-run logs activate+deactivate" || bad "missing activate/deactivate rows"

# 2) Real mode: caps at --max, calls fake claude that many times, OFF after.
rm -f "$REPO/.harness/loop_status.md" "$REPO/.harness/claude_calls.log"
CLAUDE_PROJECT_DIR="$REPO" PATH="$REPO/bin:$PATH" bash "$RUN" --max 3 >/dev/null 2>&1
[ "$(calls)" = "3" ] && ok "real mode caps at --max (3 claude calls)" || bad "calls=$(calls) (want 3)"
[ ! -f "$REPO/.harness/.loop-active" ] && ok "loop mode OFF after real run" || bad "marker left active after real run"

# 3) Halt marker mid-run stops the loop early (claude drops .loop-halt on call 2 of 10).
rm -f "$REPO/.harness/loop_status.md" "$REPO/.harness/claude_calls.log"
echo 2 > "$REPO/.harness/HALT_ON"
CLAUDE_PROJECT_DIR="$REPO" PATH="$REPO/bin:$PATH" bash "$RUN" --max 10 >/dev/null 2>&1
# call 1 (no halt yet) → call 2 drops halt → next loop top sees halt, stops. So 2 calls.
[ "$(calls)" = "2" ] && ok "halt marker stops loop early (2 calls, not 10)" || bad "calls=$(calls) (want 2)"
grep -q '| STOP | headless: halt marker' "$REPO/.harness/loop_status.md" && ok "halt logged" || bad "halt not logged"

# 4) Bad --max rejected.
CLAUDE_PROJECT_DIR="$REPO" bash "$RUN" --max abc >/dev/null 2>&1; [ $? -eq 2 ] && ok "non-integer --max rejected" || bad "bad --max not rejected"

echo "----"
echo "loop_run: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

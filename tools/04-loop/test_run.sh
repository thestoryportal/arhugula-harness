#!/usr/bin/env bash
# Hermetic test for tools/04-loop/run.sh (U-HK-15). Fakes `claude` on PATH; asserts:
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
# C-HE-09 §2 (U-HE-29): the loop ledger is a SHARED venue outside every worktree, so it is
# no longer reachable as "$REPO/.harness/loop_status.md". Pin it hermetically for this run.
export HARNESS_LOOP_STATUS_PATH="$REPO/shared-loop_status.md"

# run.sh resolves the hooks libs relative to its own location, so point it at the real
# ones by copying the loop dir + symlinking hooks into the throwaway repo layout.
cp -R "$SCRIPT_DIR" "$REPO/tools/04-loop"
cp -R "$HOOKS" "$REPO/tools/hooks"
RUN="$REPO/tools/04-loop/run.sh"

# Fake claude: logs each call; if a sentinel file says so, drops a halt marker on call N.
cat > "$REPO/bin/claude" <<'EOF'
#!/usr/bin/env bash
echo "called" >> "$CLAUDE_PROJECT_DIR/.harness/claude_calls.log"
printf '%s\n' "$*" >> "$CLAUDE_PROJECT_DIR/.harness/child_prompt.log"
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
grep -q '| ACTIVATE | lane=' "$HARNESS_LOOP_STATUS_PATH" && grep -q '| DEACTIVATE | lane=' "$HARNESS_LOOP_STATUS_PATH" \
  && ok "dry-run logs activate+deactivate" || bad "missing activate/deactivate rows"

# 2) Real mode: caps at --max, calls fake claude that many times, OFF after.
rm -f "$HARNESS_LOOP_STATUS_PATH" "$REPO/.harness/claude_calls.log"
CLAUDE_PROJECT_DIR="$REPO" PATH="$REPO/bin:$PATH" bash "$RUN" --max 3 >/dev/null 2>&1
[ "$(calls)" = "3" ] && ok "real mode caps at --max (3 claude calls)" || bad "calls=$(calls) (want 3)"
[ ! -f "$REPO/.harness/.loop-active" ] && ok "loop mode OFF after real run" || bad "marker left active after real run"

# 3) Halt marker mid-run stops the loop early (claude drops .loop-halt on call 2 of 10).
rm -f "$HARNESS_LOOP_STATUS_PATH" "$REPO/.harness/claude_calls.log"
echo 2 > "$REPO/.harness/HALT_ON"
CLAUDE_PROJECT_DIR="$REPO" PATH="$REPO/bin:$PATH" bash "$RUN" --max 10 >/dev/null 2>&1
# call 1 (no halt yet) → call 2 drops halt → next loop top sees halt, stops. So 2 calls.
[ "$(calls)" = "2" ] && ok "halt marker stops loop early (2 calls, not 10)" || bad "calls=$(calls) (want 2)"
grep -q '| STOP | lane=[^|]* | headless: halt marker' "$HARNESS_LOOP_STATUS_PATH" && ok "halt logged" || bad "halt not logged"

# 4) Bad --max rejected.
CLAUDE_PROJECT_DIR="$REPO" bash "$RUN" --max abc >/dev/null 2>&1; [ $? -eq 2 ] && ok "non-integer --max rejected" || bad "bad --max not rejected"

# 4b) --max / --prompt with NO value → exit 2, not an infinite arg-parse loop (codex P3).
( CLAUDE_PROJECT_DIR="$REPO" bash "$RUN" --max >/dev/null 2>&1 ); [ $? -eq 2 ] && ok "--max with no value → exit 2" || bad "--max no-value not rejected"
( CLAUDE_PROJECT_DIR="$REPO" bash "$RUN" --prompt >/dev/null 2>&1 ); [ $? -eq 2 ] && ok "--prompt with no value → exit 2" || bad "--prompt no-value not rejected"

# 4c) --max is passed to the child as HARNESS_LOOP_MAX (codex P2). Fake claude records env.
rm -f "$HARNESS_LOOP_STATUS_PATH" "$REPO/.harness/claude_calls.log" "$REPO/.harness/HALT_ON" "$REPO/.harness/child_env.log"
cat > "$REPO/bin/claude" <<'EOF'
#!/usr/bin/env bash
echo "called" >> "$CLAUDE_PROJECT_DIR/.harness/claude_calls.log"
echo "HARNESS_LOOP_MAX=${HARNESS_LOOP_MAX:-unset}" >> "$CLAUDE_PROJECT_DIR/.harness/child_env.log"
EOF
chmod +x "$REPO/bin/claude"
CLAUDE_PROJECT_DIR="$REPO" PATH="$REPO/bin:$PATH" bash "$RUN" --max 3 >/dev/null 2>&1
grep -q 'HARNESS_LOOP_MAX=3' "$REPO/.harness/child_env.log" && ok "--max passed to child as HARNESS_LOOP_MAX" || bad "child env: $(cat "$REPO/.harness/child_env.log" 2>/dev/null)"

# 4d) HARNESS_LOOP_PROMPT env is honored as the prompt source (codex P3 multi-word path).
rm -f "$REPO/.harness/child_env.log" "$REPO/.harness/claude_calls.log"
cat > "$REPO/bin/claude" <<'EOF'
#!/usr/bin/env bash
echo "called" >> "$CLAUDE_PROJECT_DIR/.harness/claude_calls.log"
# $2 is the prompt (claude -p "<prompt>" ...)
echo "PROMPT=$2" >> "$CLAUDE_PROJECT_DIR/.harness/child_env.log"
EOF
chmod +x "$REPO/bin/claude"
HARNESS_LOOP_PROMPT="do alpha then beta" CLAUDE_PROJECT_DIR="$REPO" PATH="$REPO/bin:$PATH" bash "$RUN" --max 1 >/dev/null 2>&1
grep -q 'PROMPT=do alpha then beta' "$REPO/.harness/child_env.log" && ok "HARNESS_LOOP_PROMPT honored (multi-word)" || bad "prompt env: $(cat "$REPO/.harness/child_env.log" 2>/dev/null)"

# 5) SIGTERM mid-run → the EXIT/signal trap clears the .loop-active marker (codex P2:
#    an interrupted runner must not leak loop mode into the next interactive session).
rm -f "$HARNESS_LOOP_STATUS_PATH" "$REPO/.harness/claude_calls.log" "$REPO/.harness/HALT_ON" "$REPO/.harness/.loop-active"
cat > "$REPO/bin/claude" <<'EOF'
#!/usr/bin/env bash
echo "called" >> "$CLAUDE_PROJECT_DIR/.harness/claude_calls.log"
sleep 5
EOF
chmod +x "$REPO/bin/claude"
CLAUDE_PROJECT_DIR="$REPO" PATH="$REPO/bin:$PATH" bash "$RUN" --max 5 >/dev/null 2>&1 &
RUNPID=$!
for _ in $(seq 1 20); do [ -f "$REPO/.harness/.loop-active" ] && break; sleep 0.3; done
kill -TERM "$RUNPID" 2>/dev/null
wait "$RUNPID" 2>/dev/null
[ ! -f "$REPO/.harness/.loop-active" ] && ok "SIGTERM mid-run → marker cleared (trap)" || bad "marker leaked after SIGTERM"
# And the loop must NOT continue after the signal (codex P1): only the in-flight call ran.
sleep 1
[ "$(calls)" = "1" ] && ok "SIGTERM stops the loop (no further claude calls)" || bad "loop continued after SIGTERM: $(calls) calls"
# And the in-flight claude child must be KILLED, not orphaned (codex P2: no loop-enabled
# process left running with auto-approval armed).
LEFT=$(pgrep -f "$REPO/bin/claude" 2>/dev/null | wc -l | tr -d ' ')
[ "${LEFT:-0}" = "0" ] && ok "in-flight claude child killed on signal (no orphan)" || bad "orphaned claude child after signal: $LEFT"

# merge-gate concurrency lens (#1426) — the runner must DRAIN a pre-U-HE-29 legacy ledger
# before computing the skip-set it bakes into the child's prompt. The child's own SessionStart
# migration runs too late: the prompt is already built. On iteration 1 this is deterministic,
# and before the venue move `loop_skip_set` read that legacy file directly — so leaving it
# unwired is a REGRESSION in the unsafe (under-skip) direction.
rm -f "$HARNESS_LOOP_STATUS_PATH" "$REPO/.harness/claude_calls.log" "$REPO/.harness/child_prompt.log"
rm -f "$REPO/.harness"/loop_status.md.migrat* "$REPO/.harness/HALT_ON" \
      "$REPO/.harness/.loop-halt" "$REPO/.harness/.loop-iter" "$REPO/.harness/child_env.log"
# The migration enumerates through `git worktree list`, so the throwaway repo has to BE one.
( cd "$REPO" && git init -q . \
  && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init ) >/dev/null 2>&1
cat > "$REPO/.harness/loop_status.md" <<'EOF'
| ts | kind | detail |
|---|---|---|
| 2026-08-01T00:00:00Z | DEFERRED-HIL | R-888 — declined by the operator, never drained |
EOF
# A later test in this file replaces $REPO/bin/claude, so this block installs its OWN stub
# rather than relying on the one defined at setup.
cat > "$REPO/bin/claude" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$CLAUDE_PROJECT_DIR/.harness/child_prompt.log"
EOF
chmod +x "$REPO/bin/claude"
CLAUDE_PROJECT_DIR="$REPO" PATH="$REPO/bin:$PATH" bash "$RUN" --max 1 >/dev/null 2>&1
if grep -q 'R-888' "$REPO/.harness/child_prompt.log" 2>/dev/null; then
  ok "the runner drains a legacy ledger before baking the skip-set into the prompt"
else
  bad "un-drained legacy deferral omitted from the child's skip-set: prompt=[$(head -c 160 "$REPO/.harness/child_prompt.log" 2>/dev/null)]"
fi
# ... and a FAILED drain must SAY so in the prompt (codex r19 P1): the child reads "not in
# the list" as "safe to attempt", so an unknowably-incomplete list must never look complete.
rm -f "$REPO/.harness"/loop_status.md.migrat* "$REPO/.harness/child_prompt.log"
printf '| t | DEFERRED-HIL | R-777 — unreadable |\n' > "$REPO/.harness/loop_status.md"
chmod 000 "$REPO/.harness/loop_status.md"
CLAUDE_PROJECT_DIR="$REPO" PATH="$REPO/bin:$PATH" bash "$RUN" --max 1 >/dev/null 2>&1
chmod 644 "$REPO/.harness/loop_status.md"
# A GENUINE drain failure now STANDS THE RUN DOWN rather than launching a child against an
# unknowable skip-set (codex r20 P2: a warning is not enforcement — the same prompt tells the
# child to pick an item ABSENT from that list). A stopped run is visible and recoverable; a
# silently re-attempted gate is neither.
[ ! -s "$REPO/.harness/child_prompt.log" ] \
  && ok "a failed drain stands the run down instead of launching on an unknowable skip-set" \
  || bad "a child was launched despite an undrained legacy ledger: $(head -c 120 "$REPO/.harness/child_prompt.log")"
# The runner CONSUMES the halt marker on exit (loop_deactivate clears it), so the durable
# evidence is the ledger row — which is what an operator actually reads afterwards.
grep -q 'skip-set unknowable' "$HARNESS_LOOP_STATUS_PATH" 2>/dev/null \
  && ok "the stand-down reason is recorded durably in the ledger" \
  || bad "no STOP row explaining the stand-down: $(tail -2 "$HARNESS_LOOP_STATUS_PATH" 2>/dev/null)"
rm -f "$REPO/.harness/.loop-halt"
rm -f "$REPO/.harness/loop_status.md" "$REPO/.harness"/loop_status.md.migrat* "$REPO/.harness/child_prompt.log"

echo "----"
echo "loop_run: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

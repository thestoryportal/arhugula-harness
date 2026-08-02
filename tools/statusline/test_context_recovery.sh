#!/usr/bin/env bash
# Hermetic test for context-recovery.sh (U-HK-27). Drives synthetic statusLine stdin
# across context thresholds against a fake $HOME (with a user statusline) + a fake project
# git repo. Asserts: proactive save fires once per (session, threshold); dedup; the
# operator's configured statusline is chained for display; minimal fallback when none;
# never blocks (exit 0, even on empty stdin). No network — the save uses skip_gh.

set -uo pipefail
# This suite exercises normal production hooks, even when launched by an isolated
# merge-gate reviewer whose own hook processes must remain inert.
unset HARNESS_CODEX_REVIEW_ISOLATED
SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/context-recovery.sh"
PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

BASE="$(cd "$(mktemp -d)" && pwd -P)"
{ [ -n "$BASE" ] && [ -d "$BASE" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$BASE"' EXIT

# Fake HOME: a user statusline that echoes a recognizable marker + a settings.json pointing at it.
HOMEDIR="$BASE/home"; mkdir -p "$HOMEDIR/.claude"
cat > "$HOMEDIR/.claude/statusline.sh" <<'EOF'
#!/usr/bin/env bash
in=$(cat); m=$(printf '%s' "$in" | jq -r '.model.display_name // "?"' 2>/dev/null)
printf 'USERLINE[%s]' "$m"
EOF
chmod +x "$HOMEDIR/.claude/statusline.sh"
printf '{"statusLine":{"type":"command","command":"bash %s/.claude/statusline.sh"}}' "$HOMEDIR" \
  > "$HOMEDIR/.claude/settings.json"

# Fake project (a git repo so HEAD/branch resolve in the snapshot writer).
PROJ="$BASE/proj"; git init -q -b main "$PROJ"
git -C "$PROJ" config user.email t@t; git -C "$PROJ" config user.name t
git -C "$PROJ" commit -q --allow-empty -m init

run() {  # run <pct> [sid]
  printf '{"context_window":{"used_percentage":%s},"session_id":"%s","model":{"display_name":"opus"}}' "$1" "${2:-sess1}" \
    | HOME="$HOMEDIR" CLAUDE_PROJECT_DIR="$PROJ" bash "$SCRIPT"
}
mark()     { [ -e "$PROJ/.harness/.checkpoints/.ctxmarks/$1" ]; }
ck_count() { ls "$PROJ/.harness/.checkpoints"/precompact-*.md 2>/dev/null | grep -c . ; }

# 1) below 60% → no save; still chains the user statusline for display.
OUT=$(run 50)
printf '%s' "$OUT" | grep -q 'USERLINE\[opus\]' && ok "chains user statusline for display" || bad "did not chain user statusline: [$OUT]"
mark sess1-60 && bad "saved below threshold" || ok "no save below 60%"

# 2) 65% → save at T=60 (marker + checkpoint).
run 65 >/dev/null
mark sess1-60 && ok "saved at 60% threshold (marker)" || bad "no marker at 60%"
[ "$(ck_count)" -ge 1 ] && ok "checkpoint written" || bad "no checkpoint file"

# 3) 65% again → dedup. Delete the checkpoint, keep the marker, re-run: must NOT re-save.
rm -f "$PROJ/.harness/.checkpoints"/precompact-*.md
run 65 >/dev/null
[ "$(ck_count)" -eq 0 ] && ok "dedup: no second save at same threshold" || bad "duplicate save at same threshold"

# 4) 80% → next threshold T=75 saves (independent of the 60 marker).
run 80 >/dev/null
mark sess1-75 && ok "saved at 75% threshold" || bad "no marker at 75%"

# The proactive writer and PostCompact reader must agree on the normalized session key.
# Drive the real statusline writer, then the real reinjection hook as one round-trip.
POSTCOMPACT="$(dirname "$SCRIPT")/../hooks/postcompact-reinject.sh"
OUT=$(printf '%s' '{"hook_event_name":"PostCompact","session_id":"sess1"}' \
  | CLAUDE_PROJECT_DIR="$PROJ" bash "$POSTCOMPACT" \
  | jq -r '.hookSpecificOutput.additionalContext // empty')
printf '%s' "$OUT" | grep -q 'precompact-latest-sess1.md' \
  && ok "statusline checkpoint round-trips through PostCompact" \
  || bad "PostCompact missed statusline checkpoint: [$OUT]"

# 5) fallback: no user statusline configured → minimal 'ctx N%'.
rm -f "$HOMEDIR/.claude/settings.json"
OUT=$(run 42)
printf '%s' "$OUT" | grep -q 'ctx 42%' && ok "minimal fallback when no user statusline" || bad "fallback wrong: [$OUT]"

# 6) never blocks / always exit 0 (even on empty stdin).
printf '' | HOME="$HOMEDIR" CLAUDE_PROJECT_DIR="$PROJ" bash "$SCRIPT" >/dev/null 2>&1 \
  && ok "exit 0 on empty stdin" || bad "non-zero exit on empty stdin"

echo
echo "RESULT: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

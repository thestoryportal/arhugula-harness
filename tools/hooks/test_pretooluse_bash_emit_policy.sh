#!/usr/bin/env bash
# Witness for U-SR-08 leg 2 (charter WR-16): the PreToolUse:Bash emit policy — a hook
# emits only on an actual rewrite or a guard decision; a plain command yields zero bytes.
#
# Premise correction, recorded here so the next reader does not re-derive it. [B] F12
# counted 143 PreToolUse:Bash `hook_success` attachments (~108 KB) as "hook chatter in
# context" and c3 called them "rtk rewrote nothing" chatter. Grounded at U-SR-08:
#   (1) rtk 0.40.0 (installed 2026-05-21, before the audit) emits 0 bytes when it does not
#       rewrite; of the 8,448 rtk attachments in this project's transcripts (counted
#       2026-09-01) all but 2 empty ones are real `rtk`-prefix rewrites — 0 "rewrote nothing".
#   (2) Those bytes never reach the model. Claude Code hooks doc, "Exit code 0": "For most
#       events, Claude Code writes stdout to the debug log and doesn't show it in the
#       transcript. The exceptions are UserPromptSubmit, UserPromptExpansion, SessionStart,
#       and PostModelSwitch, where Claude Code adds plain-text stdout as context". For
#       PreToolUse JSON only `additionalContext` reaches Claude; `permissionDecisionReason`
#       on allow is "shown to the user but not Claude". In the transcript, hook_success
#       attachments carry `content: ""`; only hook_additional_context / hook_system_message
#       rows carry model-facing content.
# So the no-rewrite case is 0 -> 0 bytes (before/after), and the policy holds at HEAD for
# every PreToolUse hook the workspace registers. This witness pins it against regression:
# a workspace hook that starts chattering on plain commands reds here. The rtk hook lives
# in the user-level settings (not workspace-owned); its checks are presence-gated and say
# so explicitly, so an empty result is never mistaken for a pass.
#
# Hooks run IN PLACE (bash "$SCRIPT_DIR/<hook>") with CLAUDE_PROJECT_DIR pointed at a
# throwaway dir — copying a hook out breaks its lib.sh source and it exits 0 silently, a
# vacuous green. HARNESS_CODEX_REVIEW_ISOLATED is never set (hooks early-exit on it). The
# permission guard is driven loop-OFF: in loop mode an allowlisted command emits an
# `allow` decision, which is a guard decision and inside the policy, not chatter.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SETTINGS="$ROOT/.claude/settings.json"
[ -f "$SETTINGS" ] || { echo "FATAL: missing $SETTINGS"; exit 1; }

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"; { [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
OUT="$REPO/out.txt"

payload() { printf '{"session_id":"probe","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"%s"}}' "$1"; }
# run_hook <hook-script> <bash-command>: stdout AND stderr -> $OUT (an attachment records
# both streams, so both must be silent), echoes the exit code.
run_hook() {
  payload "$2" | CLAUDE_PROJECT_DIR="$REPO" bash "$1" > "$OUT" 2>&1
  echo $?
}
bytes() { wc -c < "$OUT" | tr -d ' '; }

# --- 1. enumerate every PreToolUse hook command that fires on a Bash call ---------------
# (matcher "Bash", "*", or absent). The list must not be empty and must not carry a second
# rtk rewrite hook — the user-level one already rewrites, and two would double-prefix.
HOOKS=$(python3 - "$SETTINGS" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
for row in d.get("hooks", {}).get("PreToolUse", []):
    m = row.get("matcher")
    if m in (None, "", "*", "Bash") or "Bash" in str(m).split("|"):
        for h in row.get("hooks", []):
            if h.get("command"):
                print(h["command"])
EOF
)
N=$(printf '%s\n' "$HOOKS" | grep -c . || true)   # grep -c exits 1 on zero lines; N is asserted below
[ "$N" -ge 2 ] && ok "$N PreToolUse hook commands fire on Bash calls" || bad "expected >=2 Bash-firing PreToolUse hooks, found $N"
printf '%s\n' "$HOOKS" | grep -q 'precmd-clear-cache.sh' && ok "enumeration reaches precmd-clear-cache.sh" || bad "precmd-clear-cache.sh not enumerated"
printf '%s\n' "$HOOKS" | grep -q 'permission-guard.sh' && ok "enumeration reaches permission-guard.sh" || bad "permission-guard.sh not enumerated"
printf '%s\n' "$HOOKS" | grep -q 'rtk hook' && bad "project settings register a second rtk rewrite hook" || ok "no project-level rtk rewrite hook (the user-level one is the single rewriter)"

# --- 2. every workspace hook: plain commands -> exit 0, zero stdout bytes ---------------
# Two plain shapes: one rtk would rewrite (so the SILENCE here is the workspace hooks',
# not a no-op path) and one nothing rewrites.
while IFS= read -r cmd; do
  [ -n "$cmd" ] || continue
  case "$cmd" in
    *'${CLAUDE_PROJECT_DIR}'*) script="${cmd//\$\{CLAUDE_PROJECT_DIR\}/$ROOT}" ;;
    *) echo "  note: skipping non-workspace hook command: $cmd"; continue ;;
  esac
  script="${script%% *}"
  [ -f "$script" ] || { bad "hook script missing: $script"; continue; }
  label=$(basename "$script")
  for plain in 'ls -la /tmp' 'echo hi'; do
    rc=$(run_hook "$script" "$plain")
    b=$(bytes)
    [ "$rc" -eq 0 ] && [ "$b" -eq 0 ] && ok "$label: '$plain' -> exit 0, 0 bytes" \
      || bad "$label: '$plain' -> exit $rc, $b bytes: $(head -c 200 "$OUT")"
  done
done <<< "$HOOKS"

# --- 3. the guard in loop mode: emits ONLY a decision --------------------------------
# Loop-off the guard is inert (its own witness pins that). Loop-on, a force-push must yield
# a deny decision — the positive control that the zero-byte checks above are observing a
# real channel — and a plain command yields either nothing or a decision JSON, never prose.
# The loop ledger is a SHARED venue (C-HE-09 §2): pin it into the temp dir so a deny row
# never lands in the real one.
GUARD="$SCRIPT_DIR/permission-guard.sh"
export HARNESS_LOOP_STATUS_PATH="$REPO/shared-loop_status.md"
mkdir -p "$REPO/.harness"
payload "git push --force origin main" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$GUARD" > "$OUT" 2>&1; rc=$?
b=$(bytes)
if [ "$b" -gt 0 ] && grep -q '"permissionDecision"' "$OUT"; then
  ok "permission-guard (loop on) emits a decision JSON for a force-push ($b bytes) — emission is observable"
else
  bad "permission-guard (loop on) emitted no decision for a force-push (rc=$rc, $b bytes) — the zero-byte checks above would be vacuous"
fi
payload "ls -la /tmp" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$GUARD" > "$OUT" 2>&1
b=$(bytes)
if [ "$b" -eq 0 ] || grep -q '"permissionDecision"' "$OUT"; then
  ok "permission-guard (loop on) plain command -> $b bytes, decision-only (no prose)"
else
  bad "permission-guard (loop on) plain command emitted non-decision output: $(head -c 200 "$OUT")"
fi
unset HARNESS_LOOP_STATUS_PATH

# --- 4. rtk (user-level hook; presence-gated, stated loudly) -----------------------------
if command -v rtk >/dev/null 2>&1; then
  echo "  rtk present: $(rtk --version 2>&1 | head -1)"
  payload "echo hi" | rtk hook claude > "$OUT" 2>&1; b=$(bytes)
  [ "$b" -eq 0 ] && ok "rtk: no-rewrite command -> 0 bytes" || bad "rtk: no-rewrite command emitted $b bytes: $(head -c 200 "$OUT")"
  payload "cat foo.txt" | rtk hook claude > "$OUT" 2>&1; b=$(bytes)
  grep -q '"updatedInput"' "$OUT" && ok "rtk: rewrite command -> updatedInput JSON ($b bytes)" || bad "rtk: rewrite command emitted no updatedInput: $(head -c 200 "$OUT")"
  grep -q '"additionalContext"' "$OUT" && bad "rtk: rewrite JSON carries additionalContext (would reach the model)" \
    || ok "rtk: rewrite JSON carries no additionalContext (nothing reaches the model)"
else
  echo "  rtk absent: 3 rtk checks NOT run (the user-level rewrite hook is not workspace-owned; the local run is recorded on the U-SR-08 PR)"
fi

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

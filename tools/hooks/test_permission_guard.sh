#!/usr/bin/env bash
# Hermetic test for permission-guard.sh (U-HK-12). Synthetic PreToolUse/PermissionRequest
# payloads against a throwaway project dir. Asserts the tri-state: inert off-mode,
# deny-list (force-push, rm -rf, secret reloc, paid MCP), allowlist (safe bash, Read,
# Edit), design-substrate Edit → ask, unknown → ask, and the PermissionRequest schema.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/permission-guard.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"; { [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL mktemp"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
mkdir -p "$REPO/.harness"

# Helpers: build a payload + run the hook with loop mode forced via env.
pl() { # $1=tool $2=command $3=file_path $4=event
  jq -nc --arg t "$1" --arg c "$2" --arg f "$3" --arg e "${4:-PreToolUse}" \
    '{"hook_event_name":$e,"tool_name":$t,"tool_input":{"command":$c,"file_path":$f}}'
}
run_on()  { printf '%s' "$1" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"; }   # loop ON
run_off() { printf '%s' "$1" | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"; }                   # loop OFF (unset)
dec()  { echo "$1" | jq -r '.hookSpecificOutput.permissionDecision // empty' 2>/dev/null; }
beh()  { echo "$1" | jq -r '.hookSpecificOutput.decision.behavior // empty' 2>/dev/null; }

unset HARNESS_LOOP

# 1) INERT when loop mode off — even a force-push must produce NO output.
OUT=$(run_off "$(pl Bash 'git push --force origin main' '')")
[ -z "$OUT" ] && ok "inert when loop mode off" || bad "produced output off-mode: $OUT"

# 2) DENY-LIST (loop on).
OUT=$(run_on "$(pl Bash 'git push --force origin main' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny force-push" || bad "force-push not denied: $OUT"
OUT=$(run_on "$(pl Bash 'rm -rf build/' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny rm -rf" || bad "rm -rf not denied: $OUT"
OUT=$(run_on "$(pl Bash 'git reset --hard origin/main' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny git reset --hard" || bad "reset --hard not denied: $OUT"
OUT=$(run_on "$(pl Bash 'cp .env /tmp/backup.env' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny secret relocation" || bad "secret reloc not denied: $OUT"
OUT=$(run_on "$(pl Bash 'gh secret set FOO' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny gh secret" || bad "gh secret not denied: $OUT"
OUT=$(run_on "$(pl Bash 'curl https://api.anthropic.com/v1/messages' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny paid provider call" || bad "provider call not denied: $OUT"
OUT=$(run_on "$(pl mcp__harness-7a-scaffold__route_llm_call '' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny paid MCP route_llm_call" || bad "paid MCP not denied: $OUT"

# 3) DENY is logged to the ledger.
grep -q '| DENY |' "$REPO/.harness/loop_status.md" && ok "deny logged to ledger" || bad "deny not logged"

# 4) ALLOWLIST.
OUT=$(run_on "$(pl Bash 'git status' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow git status" || bad "git status not allowed: $OUT"
OUT=$(run_on "$(pl Bash 'git commit -m wip' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow git commit" || bad "git commit not allowed: $OUT"
OUT=$(run_on "$(pl Bash 'bash tools/hooks/test_loop_lib.sh' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow hermetic test run" || bad "test run not allowed: $OUT"
OUT=$(run_on "$(pl Bash 'gh pr create --fill' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow gh pr create" || bad "gh pr not allowed: $OUT"
OUT=$(run_on "$(pl Read '' '/x/y.py')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow Read tool" || bad "Read not allowed: $OUT"
OUT=$(run_on "$(pl Edit '' "$REPO/tools/hooks/foo.sh")")
[ "$(dec "$OUT")" = "allow" ] && ok "allow Edit to normal path" || bad "Edit not allowed: $OUT"

# 5) ASK (no output) — design-substrate Edit + unknown bash + bare git push (non-force).
OUT=$(run_on "$(pl Edit '' '/repo/design-substrate/Spec_X.md')")
[ -z "$OUT" ] && ok "design-substrate Edit → ask (no auto-approve)" || bad "design-substrate auto-decided: $OUT"
OUT=$(run_on "$(pl Bash 'python scripts/migrate.py --wipe' '')")
[ -z "$OUT" ] && ok "unknown bash → ask" || bad "unknown bash auto-decided: $OUT"

# 5b) CHAINED/NESTED command with a safe PREFIX must NOT auto-allow (codex P1). A safe
#     prefix fronting a dangerous follow-on falls through to ask.
OUT=$(run_on "$(pl Bash 'git status && python scripts/migrate.py --wipe' '')")
[ -z "$OUT" ] && ok "safe-prefix && danger → ask (no chained auto-allow)" || bad "chained cmd auto-decided: $OUT"
OUT=$(run_on "$(pl Bash 'uv run python scripts/migrate.py --wipe' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "uv run python wipe → not auto-allowed" || bad "uv-run-python auto-allowed: $OUT"
OUT=$(run_on "$(pl Bash 'cat secrets.txt | sh' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "piped cat | sh → not auto-allowed" || bad "pipe auto-allowed: $OUT"
OUT=$(run_on "$(pl Bash 'git log $(rm -rf /)' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "command substitution → not auto-allowed" || bad "cmd-subst auto-allowed: $OUT"

# 5c) Edit/Write to a secret file must NOT auto-allow (codex P1) — falls through to ask.
OUT=$(run_on "$(pl Edit '' '/repo/.env')")
[ -z "$OUT" ] && ok ".env Edit → ask (no auto-approve)" || bad ".env edit auto-decided: $OUT"
OUT=$(run_on "$(pl Write '' '/repo/config/credentials.json')")
[ -z "$OUT" ] && ok "credentials Write → ask" || bad "credentials write auto-decided: $OUT"
OUT=$(run_on "$(pl Write '' '/home/u/.ssh/id_rsa')")
[ -z "$OUT" ] && ok "id_rsa Write → ask" || bad "id_rsa write auto-decided: $OUT"

# 6) PermissionRequest event uses the decision.behavior schema.
OUT=$(run_on "$(pl Bash 'git status' '' PermissionRequest)")
[ "$(beh "$OUT")" = "allow" ] && ok "PermissionRequest allow schema" || bad "PR allow schema wrong: $OUT"
OUT=$(run_on "$(pl Bash 'rm -rf /' '' PermissionRequest)")
[ "$(beh "$OUT")" = "deny" ] && ok "PermissionRequest deny schema" || bad "PR deny schema wrong: $OUT"

echo "----"
echo "permission_guard: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

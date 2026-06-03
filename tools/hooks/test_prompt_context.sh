#!/usr/bin/env bash
# Hermetic test for prompt-context.sh (U-HK-08). Asserts next-action injection and
# the local drift proxy (matching / drift / refresh-exempt).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/prompt-context.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
git -C "$REPO" init -q -b main; git -C "$REPO" config user.email t@t.t; git -C "$REPO" config user.name t
mkdir -p "$REPO/.harness"
git -C "$REPO" commit -q --allow-empty -m base
HEAD8=$(git -C "$REPO" rev-parse HEAD | head -c 8)

dash() { # $1=git_head to pin
  cat > "$REPO/.harness/roadmap_status.md" <<EOF
# dash
| \`git_head\` | \`${1}\` (main) |
## Next action
**\`R-BAZ\`** go.
EOF
}
run() { printf '%s' '{"hook_event_name":"UserPromptSubmit","prompt":"hi"}' | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" | jq -r '.hookSpecificOutput.additionalContext // empty'; }

# 1) dashboard pins current HEAD → next-action, no drift.
dash "$HEAD8"
OUT=$(run)
printf '%s' "$OUT" | grep -q "next=R-BAZ" && ok "injects next-action ($OUT)" || bad "no next-action: $OUT"
printf '%s' "$OUT" | grep -q "drift" && bad "false drift when HEAD matches" || ok "no drift when HEAD matches"

# 2) dashboard pins a DIFFERENT head, last commit not a refresh → drift flag.
dash "deadbeef"
OUT=$(run)
printf '%s' "$OUT" | grep -q "possible drift" && ok "flags drift on HEAD mismatch" || bad "no drift flag: $OUT"

# 3) HEAD mismatch but last commit is a terminating refresh → no drift (§12.2.1).
git -C "$REPO" commit -q --allow-empty -m "ops: roadmap status refresh post-#1 (#2)"
dash "deadbeef"
OUT=$(run)
printf '%s' "$OUT" | grep -q "drift" && bad "drift flagged despite refresh commit" || ok "refresh commit exempt from drift"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

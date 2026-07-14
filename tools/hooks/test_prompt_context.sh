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

# 1) roadmap_status.md pins current HEAD → next-action, no drift.
dash "$HEAD8"
OUT=$(run)
printf '%s' "$OUT" | grep -q "next=R-BAZ" && ok "injects next-action ($OUT)" || bad "no next-action: $OUT"
printf '%s' "$OUT" | grep -q "drift" && bad "false drift when HEAD matches" || ok "no drift when HEAD matches"

# 2) roadmap_status.md pins a DIFFERENT head, last commit not a refresh → drift flag.
dash "deadbeef"
OUT=$(run)
printf '%s' "$OUT" | grep -q "possible drift" && ok "flags drift on HEAD mismatch" || bad "no drift flag: $OUT"

# 3) HEAD mismatch but last commit is a GENUINE terminating refresh (refresh title
#    AND roadmap-status-only changed file) → no drift (§12.2.1 both-conditions).
dash "deadbeef"
git -C "$REPO" add .harness/roadmap_status.md
git -C "$REPO" commit -q -m "ops: roadmap status refresh post-#1 (#2)"
OUT=$(run)
printf '%s' "$OUT" | grep -q "drift" && bad "drift flagged despite genuine roadmap-status-only refresh" || ok "genuine roadmap-status-only refresh exempt from drift"

# 4) Refresh-TITLED commit that ALSO touches a non-roadmap-status file → NOT exempt
#    (§12.2.1 requires roadmap-status-only; title-only matching would be a false negative).
dash "deadbeef"
echo "x" > "$REPO/other.txt"
git -C "$REPO" add .harness/roadmap_status.md other.txt
git -C "$REPO" commit -q -m "ops: roadmap status refresh post-#3 (#4)"
OUT=$(run)
printf '%s' "$OUT" | grep -q "possible drift" && ok "mis-titled substantive commit still flags drift" || bad "drift suppressed on title-only match (P3 regression): $OUT"

# 5) On a NON-default branch, HEAD always differs from the main-pinned dashboard
#    git_head — the drift proxy must NOT false-positive (default-branch guard).
git -C "$REPO" checkout -q -b feature/work
dash "deadbeef"   # mismatch vs local HEAD, but we are off the default branch
OUT=$(run)
printf '%s' "$OUT" | grep -q "drift" && bad "false drift on feature branch (P2 regression): $OUT" || ok "no drift proxy off the default branch"
printf '%s' "$OUT" | grep -q "next=" && ok "next-action still injected off default branch" || bad "next-action dropped off default branch: $OUT"
git -C "$REPO" checkout -q main

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

#!/usr/bin/env bash
# Hermetic test for post-merge-refresh.sh (Hook A).
# Builds a throwaway git repo + fixture dashboard so the test never rots against
# the live roadmap_status.md. Exercises all four guard branches via direct
# synthetic-stdin invocation (the hook cannot self-activate a session, so direct
# invocation IS the pilot test per the advisor pass).
#
# Run: tools/roadmap-audit/test_post_merge_refresh.sh
# Exits non-zero on any failed assertion (CI-friendly).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/post-merge-refresh.sh"
[ -x "$HOOK" ] || { echo "FAIL: hook not executable at $HOOK"; exit 1; }

REPO="$(mktemp -d)"
trap 'rm -rf "$REPO"' EXIT

git -C "$REPO" init -q -b main
git -C "$REPO" config user.email t@t.t
git -C "$REPO" config user.name t
mkdir -p "$REPO/.harness"

# commit 1 — base (the dashboard will pin this as git_head)
echo a > "$REPO/.harness/seed"; git -C "$REPO" add -A; git -C "$REPO" commit -qm "base commit"
C1=$(git -C "$REPO" rev-parse HEAD | head -c 8)

# commit 2 — substantive (non-refresh title)
echo b >> "$REPO/.harness/seed"; git -C "$REPO" add -A; git -C "$REPO" commit -qm "feat(x): a substantive change (#101)"
C2=$(git -C "$REPO" rev-parse HEAD | head -c 8)

# commit 3 — a terminating refresh (matches the §12.2.1 prefix)
echo c >> "$REPO/.harness/seed"; git -C "$REPO" add -A; git -C "$REPO" commit -qm "ops: roadmap status refresh post-#101 (#102)"
C3=$(git -C "$REPO" rev-parse HEAD | head -c 8)

# fixture dashboard pinning C1 as git_head
cat > "$REPO/.harness/roadmap_status.md" <<EOF
# Roadmap status dashboard
| Field | Value |
|---|---|
| \`workspace_state_hash\` | \`abcdef012345\` |
| \`git_head\` | \`${C1}\` (main) — base commit |
EOF

MERGE_CMD='{"tool_name":"Bash","tool_input":{"command":"gh pr merge 101 --squash"}}'
NONMERGE_CMD='{"tool_name":"Bash","tool_input":{"command":"ls -la"}}'

run() { # $1=stdin json, $2=compare-ref(optional)
  if [ -n "${2:-}" ]; then
    printf '%s' "$1" | CLAUDE_PROJECT_DIR="$REPO" POST_MERGE_REFRESH_REF="$2" bash "$HOOK"
  else
    printf '%s' "$1" | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"
  fi
}

PASS=0; FAIL=0
ok()   { echo "  ok: $1"; PASS=$((PASS+1)); }
bad()  { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

# 1) non-merge command → silent
OUT=$(run "$NONMERGE_CMD" "$C2")
[ -z "$OUT" ] && ok "non-merge command stays silent" || bad "non-merge emitted: $OUT"

# 2) merge command but no advance (compare-ref == dashboard head) → silent
OUT=$(run "$MERGE_CMD" "$C1")
[ -z "$OUT" ] && ok "no-advance stays silent" || bad "no-advance emitted: $OUT"

# 3) merge command, tip IS a refresh → silent (no follow-on owed)
OUT=$(run "$MERGE_CMD" "$C3")
[ -z "$OUT" ] && ok "refresh-tip stays silent" || bad "refresh-tip emitted: $OUT"

# 4) merge command, advanced to a substantive (non-refresh) commit → EMIT
OUT=$(run "$MERGE_CMD" "$C2")
if printf '%s' "$OUT" | grep -q "substantive merge detected" \
   && printf '%s' "$OUT" | grep -qE '"hookEventName":"PostToolUse"' \
   && printf '%s' "$OUT" | grep -qE 'workspace_state_hash=[a-f0-9]{12}'; then
  ok "substantive advance emits reminder with computed hash"
else
  bad "substantive advance did not emit expected reminder: $OUT"
fi

echo "---"
echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

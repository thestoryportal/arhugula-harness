#!/usr/bin/env bash
# Hermetic test for post-merge-refresh.sh (Hook A).
# Builds a throwaway git repo + fixture roadmap_status.md so the test never rots against
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
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT

git -C "$REPO" init -q -b main
git -C "$REPO" config user.email t@t.t
git -C "$REPO" config user.name t
mkdir -p "$REPO/.harness"

# commit 1 — base (roadmap_status.md will pin this as git_head)
echo a > "$REPO/.harness/seed"; git -C "$REPO" add -A; git -C "$REPO" commit -qm "base commit"
C1=$(git -C "$REPO" rev-parse HEAD | head -c 8)

# commit 2 — substantive (non-refresh title)
echo b >> "$REPO/.harness/seed"; git -C "$REPO" add -A; git -C "$REPO" commit -qm "feat(x): a substantive change (#101)"
C2=$(git -C "$REPO" rev-parse HEAD | head -c 8)

# commit 3 — a GENUINE terminating refresh: §12.2.1 prefix AND roadmap-status-only
printf '# dash\n' > "$REPO/.harness/roadmap_status.md"; git -C "$REPO" add -A; git -C "$REPO" commit -qm "ops: roadmap status refresh post-#101 (#102)"
C3=$(git -C "$REPO" rev-parse HEAD | head -c 8)

# commit 4 — a MIS-TITLED refresh: §12.2.1 prefix BUT touches a non-roadmap-status file
#            (P2-a: must NOT be suppressed — a substantive PR wearing the prefix)
echo d >> "$REPO/.harness/seed"; git -C "$REPO" add -A; git -C "$REPO" commit -qm "ops: roadmap status refresh post-#102 (#104) [also code]"
C_MIS=$(git -C "$REPO" rev-parse HEAD | head -c 8)

# fixture roadmap_status.md pinning C1 as git_head (uncommitted working-tree
# override — the hook reads STORED_HEAD from the working tree, not from a commit)
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

# 2) merge command but no advance (compare-ref == stored head) → silent
OUT=$(run "$MERGE_CMD" "$C1")
[ -z "$OUT" ] && ok "no-advance stays silent" || bad "no-advance emitted: $OUT"

# 3) merge command, tip IS a genuine (roadmap-status-only) refresh → silent
OUT=$(run "$MERGE_CMD" "$C3")
[ -z "$OUT" ] && ok "roadmap-status-only refresh-tip stays silent" || bad "refresh-tip emitted: $OUT"

# 4) merge command, advanced to a substantive (non-refresh) commit → EMIT
OUT=$(run "$MERGE_CMD" "$C2")
if printf '%s' "$OUT" | grep -q "substantive merge detected" \
   && printf '%s' "$OUT" | grep -qE '"hookEventName":"PostToolUse"' \
   && printf '%s' "$OUT" | grep -qE 'workspace_state_hash=[a-f0-9]{12}'; then
  ok "substantive advance emits reminder with computed hash"
else
  bad "substantive advance did not emit expected reminder: $OUT"
fi

# 5) [P1 regression — Codex finding] hash inputs (FORKS/BATCH) must come from the
#    MERGED ref, not the pre-merge local tree. Add a fork doc in a NEW commit C4
#    (absent at the roadmap_status.md pin C1) and assert the emitted hash counts it (FORKS=1),
#    i.e. equals the hash recomputed from C4's tree — and is NOT the FORKS=0 hash.
echo "x" > "$REPO/.harness/class_1_fork_regression.md"
git -C "$REPO" add -A; git -C "$REPO" commit -qm "feat(y): add a fork doc (#103)"
C_FORK=$(git -C "$REPO" rev-parse HEAD | head -c 8)
# Expected hash with the recipe `ORIGIN_HEAD|PRS|FORKS|BATCH` — fixture has no
# GitHub remote (PRS empty) and no batch files (BATCH empty); FORKS must be 1.
EXP_OK=$(printf '%s|%s|%s|%s'  "$C_FORK" "" "1" "" | shasum -a 256 | head -c 12)
EXP_BAD=$(printf '%s|%s|%s|%s' "$C_FORK" "" "0" "" | shasum -a 256 | head -c 12)
OUT=$(run "$MERGE_CMD" "$C_FORK")
GOT=$(printf '%s' "$OUT" | grep -oE 'workspace_state_hash=[a-f0-9]{12}' | head -1 | cut -d= -f2)
if [ "$GOT" = "$EXP_OK" ] && [ "$GOT" != "$EXP_BAD" ]; then
  ok "hash reads FORKS from the merged ref (P1 fix: got=$GOT == merged-ref hash, != pre-merge hash)"
else
  bad "P1 regression: got=$GOT expected=$EXP_OK (pre-merge-would-be=$EXP_BAD)"
fi

# 6) [P2-a regression — Codex finding] a commit with the refresh title prefix but
#    that touches a NON-roadmap-status file is NOT a §12.2.1 terminating refresh →
#    must EMIT.
OUT=$(run "$MERGE_CMD" "$C_MIS")
if printf '%s' "$OUT" | grep -q "substantive merge detected"; then
  ok "mis-titled refresh (prefix but not roadmap-status-only) still emits (P2-a fix)"
else
  bad "P2-a regression: mis-titled refresh was wrongly suppressed: '$OUT'"
fi

echo "---"
echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

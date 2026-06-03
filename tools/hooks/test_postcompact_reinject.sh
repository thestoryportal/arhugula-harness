#!/usr/bin/env bash
# Hermetic test for postcompact-reinject.sh (U-HK-06). Asserts the post-compaction
# additionalContext carries next-action + the checkpoint pointer when present.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/postcompact-reinject.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
git -C "$REPO" init -q -b main; git -C "$REPO" config user.email t@t.t; git -C "$REPO" config user.name t
mkdir -p "$REPO/.harness"
printf '# dash\n## Next action\n**`R-BAR`** go.\n' > "$REPO/.harness/roadmap_status.md"
git -C "$REPO" add -A; git -C "$REPO" commit -qm base

run() { printf '%s' '{"hook_event_name":"PostCompact"}' | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" | jq -r '.hookSpecificOutput.additionalContext // empty'; }

# 1) without a checkpoint file → emits next-action + audit nudge, no pointer.
OUT=$(run)
printf '%s' "$OUT" | grep -q "R-BAR" && ok "carries next-action" || bad "missing next-action: $OUT"
printf '%s' "$OUT" | grep -q "§12.1" && ok "nudges audit" || bad "missing audit nudge"
printf '%s' "$OUT" | grep -q "snapshot" && bad "claims snapshot when none exists" || ok "no pointer when no checkpoint"

# 2) with a checkpoint file → includes the pointer.
mkdir -p "$REPO/.harness/.checkpoints"; : > "$REPO/.harness/.checkpoints/precompact-latest.md"
OUT=$(run)
printf '%s' "$OUT" | grep -q "precompact-latest.md" && ok "surfaces checkpoint pointer" || bad "missing pointer: $OUT"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

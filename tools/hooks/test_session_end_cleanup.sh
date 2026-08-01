#!/usr/bin/env bash
# Hermetic test for session-end-cleanup.sh (U-HK-09). Asserts checkpoint pruning
# (keep 10, preserve latest) and report generation. No network: gh returns empty in
# a repo with no GitHub remote, so the merged-branch section is empty (fine).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/session-end-cleanup.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
git -C "$REPO" init -q -b main; git -C "$REPO" config user.email t@t.t; git -C "$REPO" config user.name t
git -C "$REPO" commit -q --allow-empty -m base
CK="$REPO/.harness/.checkpoints"; mkdir -p "$CK"
BIN="$REPO/bin"; mkdir -p "$BIN"
printf '#!/usr/bin/env bash\ntouch "$GH_CALLED"\nsleep 10\n' > "$BIN/gh"
chmod +x "$BIN/gh"

# 15 timestamped snapshots + two session-specific latest pointers.
for i in $(seq -w 1 15); do : > "$CK/precompact-20260101-0000${i}.md"; done
: > "$CK/precompact-latest-session-a.md"
: > "$CK/precompact-latest-session-b.md"

SECONDS=0
printf '%s' '{"hook_event_name":"SessionEnd","end_reason":"clear"}' \
  | GH_CALLED="$REPO/gh-called" PATH="$BIN:$PATH" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"
ELAPSED=$SECONDS
[ "$ELAPSED" -lt 3 ] && ok "cleanup fits SessionEnd budget" || bad "cleanup exceeded SessionEnd budget (${ELAPSED}s)"
[ ! -e "$REPO/gh-called" ] && ok "cleanup avoids network" || bad "cleanup invoked gh"

KEPT=$(ls -1 "$CK"/precompact-2*.md 2>/dev/null | wc -l | tr -d ' ')
[ "$KEPT" = "10" ] && ok "prunes to 10 newest snapshots (kept=$KEPT)" || bad "expected 10 kept, got $KEPT"
[ -f "$CK/precompact-latest-session-a.md" ] && [ -f "$CK/precompact-latest-session-b.md" ] \
  && ok "preserves session-specific latest pointers" || bad "deleted a latest pointer"
# The 5 oldest (00001..00005) should be gone; the 5 newest (00011..00015) kept.
[ ! -f "$CK/precompact-20260101-000001.md" ] && ok "oldest snapshot pruned" || bad "oldest snapshot survived"
[ -f "$CK/precompact-20260101-000015.md" ] && ok "newest snapshot kept" || bad "newest snapshot pruned"
[ -f "$CK/session-end-report.md" ] && ok "writes hygiene report" || bad "no report"
grep -q "MEMORY.md cap" "$CK/session-end-report.md" 2>/dev/null && ok "report has sections" || bad "report missing sections"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

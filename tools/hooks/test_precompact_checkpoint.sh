#!/usr/bin/env bash
# Hermetic test for precompact-checkpoint.sh (U-HK-05). Temp git repo + fixture
# dashboard; drives the hook and asserts a snapshot is written with the essentials.
# Exits non-zero on any failed assertion.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/precompact-checkpoint.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
git -C "$REPO" init -q -b main; git -C "$REPO" config user.email t@t.t; git -C "$REPO" config user.name t
mkdir -p "$REPO/.harness"
cat > "$REPO/.harness/roadmap_status.md" <<'EOF'
# dash
## Next action
**`R-FOO`** do the thing.
EOF
git -C "$REPO" add -A; git -C "$REPO" commit -qm "base"

printf '%s' '{"hook_event_name":"PreCompact","session_id":"session-a","trigger":"auto"}' \
  | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"

LATEST="$REPO/.harness/.checkpoints/precompact-latest-session-a.md"
[ -f "$LATEST" ] && ok "latest snapshot written" || bad "no latest snapshot"
if [ -f "$LATEST" ]; then
  grep -q "Pre-compaction snapshot" "$LATEST" && ok "has header" || bad "no header"
  grep -q "R-FOO" "$LATEST" && ok "captures roadmap next-action" || bad "missing next-action"
  grep -q "trigger=auto" "$LATEST" && ok "records trigger" || bad "missing trigger"
  grep -q "HEAD:" "$LATEST" && ok "records HEAD/branch" || bad "missing HEAD"
fi
# A different session receives a different atomic latest pointer even in the same second.
printf '%s' '{"hook_event_name":"PreCompact","session_id":"session-b","trigger":"manual"}' \
  | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"
[ -f "$REPO/.harness/.checkpoints/precompact-latest-session-b.md" ] \
  && ok "second session gets its own latest pointer" || bad "second session pointer missing"
grep -q 'trigger=auto' "$LATEST" && ok "session-a pointer not overwritten by session-b" || bad "session-a pointer contaminated"
grep -q 'trigger=manual' "$REPO/.harness/.checkpoints/precompact-latest-session-b.md" \
  && ok "session-b pointer carries its own snapshot" || bad "session-b pointer contaminated"
COUNT=$(ls "$REPO/.harness/.checkpoints/"precompact-20*.md 2>/dev/null | wc -l | tr -d ' ')
[ "$COUNT" = "2" ] && ok "same-second snapshots have collision-free names" || bad "expected two timestamped snapshots, got $COUNT"
ls "$REPO/.harness/.checkpoints/"*.tmp-* >/dev/null 2>&1 \
  && bad "atomic checkpoint temp file leaked" || ok "atomic checkpoint leaves no temp files"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

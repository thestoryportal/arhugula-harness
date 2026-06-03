#!/usr/bin/env bash
# Hermetic smoke test for session-start.sh (the SessionStart roadmap audit).
# Builds a throwaway repo + fixture dashboard and drives the real hook with
# CLAUDE_PROJECT_DIR pointed at it, asserting each emit branch (hash=ok /
# lag-expected / drift). No network: `gh pr list` returns empty in a repo with no
# GitHub remote, so PRS="" and the hash is computed deterministically.
# Exits non-zero on any failed assertion.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/session-start.sh"
. "$SCRIPT_DIR/../hooks/lib.sh"   # for hook_state_hash to compute the expected value

REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
git -C "$REPO" init -q -b main; git -C "$REPO" config user.email t@t.t; git -C "$REPO" config user.name t
mkdir -p "$REPO/.harness"
: > "$REPO/Project_Roadmap_v1.md"
echo seed > "$REPO/.harness/seed"
git -C "$REPO" add -A; git -C "$REPO" commit -qm "base commit"

HEAD8=$(git -C "$REPO" rev-parse HEAD | head -c 8)
# Fixture state: PRS="" (no remote), FORKS=0 (no fork files), BATCH="" (none).
EXP_HASH=$(hook_state_hash "$HEAD8" "" "0" "")

write_dashboard() { # $1=hash to pin
  cat > "$REPO/.harness/roadmap_status.md" <<EOF
# Roadmap status dashboard
| Field | Value |
|---|---|
| \`workspace_state_hash\` | \`${1}\` |
| \`git_head\` | \`${HEAD8}\` (main) — base commit |

## Next action
**\`R-TEST\`** do the thing.
EOF
}

run() { CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" | jq -r '.hookSpecificOutput.additionalContext' 2>/dev/null; }

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

# 1) hash=ok — dashboard pins the correct hash; last commit is not a refresh.
write_dashboard "$EXP_HASH"
OUT=$(run)
printf '%s' "$OUT" | grep -q "hash=ok" && printf '%s' "$OUT" | grep -q "next=R-TEST" \
  && ok "hash=ok branch ($OUT)" || bad "expected hash=ok next=R-TEST, got: $OUT"

# 2) drift — wrong hash, last commit not a refresh.
write_dashboard "000000000000"
OUT=$(run)
printf '%s' "$OUT" | grep -q "ROADMAP DRIFT" && ok "drift branch ($OUT)" || bad "expected DRIFT, got: $OUT"

# 3) lag-expected — wrong hash, last commit is a GENUINE terminating refresh: the
#    reserved title prefix AND the only changed file is the dashboard (§12.2.1 both
#    conditions). write_dashboard rewrites only .harness/roadmap_status.md, so staging
#    just that file makes a dashboard-only commit.
write_dashboard "000000000000"
git -C "$REPO" add .harness/roadmap_status.md
git -C "$REPO" commit -qm "ops: roadmap status refresh post-#1 (#2)"
OUT=$(run)
printf '%s' "$OUT" | grep -q "lag-expected" && ok "lag-expected on dashboard-only refresh ($OUT)" || bad "expected lag-expected, got: $OUT"

# 4) DRIFT despite refresh title — last commit carries the reserved prefix but ALSO
#    changes a non-dashboard file, so it is NOT a terminating refresh under §12.2.1.
#    Title-only matching would mis-pass this as lag-expected (the false negative).
write_dashboard "000000000000"
echo more > "$REPO/.harness/seed"
git -C "$REPO" add .harness/roadmap_status.md .harness/seed
git -C "$REPO" commit -qm "ops: roadmap status refresh post-#3 (#4)"
OUT=$(run)
printf '%s' "$OUT" | grep -q "ROADMAP DRIFT" && ok "mis-titled substantive commit halts as DRIFT ($OUT)" || bad "expected DRIFT (title-only false negative), got: $OUT"

# 5) Pending-HIL surfacing — when the loop ledger carries post-ACTIVATE DEFERRED-HIL
#    rows, EVERY emit branch appends the operator-facing summary (so the last unattended
#    run's deferrals are "clearly presented when the operator engages next"). Absent when
#    there is no ledger. Branch-agnostic: the suffix rides whatever audit verdict fires.
cat > "$REPO/.harness/loop_status.md" <<'EOF'
| ts | kind | detail |
|---|---|---|
| t1 | ACTIVATE | run |
| t2 | DEFERRED-HIL | R-410 — needs container runtime |
EOF
OUT=$(run)
printf '%s' "$OUT" | grep -q "await your input" && printf '%s' "$OUT" | grep -q "R-410" \
  && ok "pending-HIL summary appended to SessionStart ($OUT)" || bad "no pending-HIL suffix: $OUT"
rm -f "$REPO/.harness/loop_status.md"
OUT=$(run)
printf '%s' "$OUT" | grep -q "await your input" && bad "pending-HIL suffix present with no ledger: $OUT" || ok "no pending-HIL suffix when no ledger"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

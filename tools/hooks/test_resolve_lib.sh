#!/usr/bin/env bash
# Hermetic test for resolve_lib.sh (U-HK-13). Fakes codex on PATH; asserts resolve_codex
# returns its output (subscription-auth invocation), the absent-codex path returns 2,
# and the ledger helpers append correctly-shaped RESOLVE / RESOLVE-SPLIT rows.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"; { [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL mktemp"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
mkdir -p "$REPO/.harness" "$REPO/bin"

export CLAUDE_PROJECT_DIR="$REPO"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
# shellcheck source=loop_lib.sh
. "$SCRIPT_DIR/loop_lib.sh"
# shellcheck source=resolve_lib.sh
. "$SCRIPT_DIR/resolve_lib.sh"

# Fake codex: echoes a canned verdict; records the args it saw so we can assert the
# subscription-auth flags are passed.
cat > "$REPO/bin/codex" <<'EOF'
#!/usr/bin/env bash
echo "ARGS:$*" >> "$CLAUDE_PROJECT_DIR/.harness/codex_args.log"
echo "VERDICT: option A (safer)"
EOF
chmod +x "$REPO/bin/codex"

# 1) resolve_codex returns codex's output + passes subscription-auth flags.
OUT=$(PATH="$REPO/bin:$PATH" resolve_codex "pick A or B?")
echo "$OUT" | grep -q "VERDICT: option A" && ok "resolve_codex returns codex output" || bad "no verdict: $OUT"
grep -q 'preferred_auth_method=chatgpt' "$REPO/.harness/codex_args.log" && ok "passes chatgpt subscription auth" || bad "no chatgpt auth flag: $(cat "$REPO/.harness/codex_args.log")"
grep -q 'exec' "$REPO/.harness/codex_args.log" && ok "uses codex exec" || bad "not codex exec"

# 2) absent codex → return code 2.
( PATH="/nonexistent-only"; resolve_codex "x" >/dev/null 2>&1 ); [ $? -eq 2 ] && ok "absent codex → rc 2" || bad "absent codex rc wrong"

# 3) resolve_record appends a RESOLVE row.
resolve_record "option A" "both agreed A is reversible"
grep -q '| RESOLVE | DECIDE: option A — both agreed A is reversible |' "$REPO/.harness/loop_status.md" \
  && ok "resolve_record appends RESOLVE row" || bad "no RESOLVE row: $(grep RESOLVE "$REPO/.harness/loop_status.md")"

# 4) resolve_split appends a RESOLVE-SPLIT row.
resolve_split "option A" "codex=A advisor=B; took safer"
grep -q '| RESOLVE-SPLIT | SAFE-DEFAULT: option A — codex=A advisor=B; took safer |' "$REPO/.harness/loop_status.md" \
  && ok "resolve_split appends RESOLVE-SPLIT row" || bad "no SPLIT row: $(grep SPLIT "$REPO/.harness/loop_status.md")"

echo "----"
echo "resolve_lib: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

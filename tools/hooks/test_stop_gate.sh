#!/usr/bin/env bash
# Hermetic test for stop-gate.sh (U-HK-10). Fake ruff on PATH (finding iff # LINT_BAD).
# Asserts: blocks on lint failure, the stop_hook_active loop guard, clean/no-change pass.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/stop-gate.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
git -C "$REPO" init -q -b main; git -C "$REPO" config user.email t@t.t; git -C "$REPO" config user.name t

# Fake ruff: emits a finding for files containing # LINT_BAD.
mkdir -p "$REPO/bin"
cat > "$REPO/bin/ruff" <<'EOF'
#!/usr/bin/env bash
for f in "$@"; do
  [ -f "$f" ] && grep -q '# LINT_BAD' "$f" 2>/dev/null && echo "$f:1:1: F401 fake finding"
done
exit 0
EOF
chmod +x "$REPO/bin/ruff"

# Committed clean baseline.
printf 'x = 1\n' > "$REPO/mod.py"; git -C "$REPO" add -A; git -C "$REPO" commit -qm base

run() { # $1=stop_hook_active(true/false)
  printf '%s' "{\"hook_event_name\":\"Stop\",\"stop_hook_active\":$1}" \
    | PATH="$REPO/bin:$PATH" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"
}

# 1) uncommitted .py with a lint error → block.
printf 'import os  # LINT_BAD\n' > "$REPO/mod.py"
OUT=$(run false)
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "blocks on lint failure" || bad "did not block: $OUT"
echo "$OUT" | jq -e '.reason | test("ruff lint failed")' >/dev/null 2>&1 && ok "reason names the failure" || bad "reason missing"

# 2) same lint error but stop_hook_active=true → no block (loop guard).
OUT=$(run true)
[ -z "$OUT" ] && ok "stop_hook_active guard prevents re-block" || bad "blocked despite active flag: $OUT"

# 3) clean uncommitted .py change → no block.
printf 'y = 2\n' > "$REPO/mod.py"
OUT=$(run false)
[ -z "$OUT" ] && ok "clean change → allows stop" || bad "blocked on clean change: $OUT"

# 4) no .py change (revert) → no block.
git -C "$REPO" checkout -q -- mod.py
OUT=$(run false)
[ -z "$OUT" ] && ok "no change → allows stop" || bad "blocked with no change: $OUT"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

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

# Fake ruff: emits a finding (stdout, exit 1) for files containing # LINT_BAD; for
# files containing # RUFF_DIES it simulates a runner that cannot run (stderr, exit 2,
# NO stdout) — the fail-open case. Clean files → exit 0.
mkdir -p "$REPO/bin"
cat > "$REPO/bin/ruff" <<'EOF'
#!/usr/bin/env bash
# Dispatch on the subcommand: `format --check` reports `# FMT_BAD` files as
# would-be-reformatted; `check` keeps the lint behavior.
sub="$1"; shift
if [ "$sub" = "format" ]; then
  n=0
  for f in "$@"; do [ -f "$f" ] || continue; grep -q '# FMT_BAD' "$f" 2>/dev/null && n=$((n+1)); done
  [ "$n" -gt 0 ] && { echo "$n file would be reformatted"; exit 1; }
  echo "$n files already formatted"; exit 0
fi
rc=0
for f in "$@"; do
  [ -f "$f" ] || continue
  if grep -q '# RUFF_DIES' "$f" 2>/dev/null; then echo "ruff: internal error" >&2; exit 2; fi
  if grep -q '# LINT_BAD' "$f" 2>/dev/null; then echo "$f:1:1: F401 fake finding"; rc=1; fi
done
exit $rc
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

# 5) UNTRACKED (never git-added) .py with a lint error → block (P1 regression:
#    git diff HEAD misses untracked files; ls-files --others arm must catch them).
printf 'import sys  # LINT_BAD\n' > "$REPO/fresh.py"
OUT=$(run false)
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "blocks on untracked .py lint failure" || bad "untracked .py bypassed gate (P1): $OUT"
rm -f "$REPO/fresh.py"

# 6) untracked but git-ignored .py → not linted (ls-files --others --exclude-standard
#    respects .gitignore), so a clean tree allows stop.
printf 'venv/\n' > "$REPO/.gitignore"
mkdir -p "$REPO/venv"; printf 'import os  # LINT_BAD\n' > "$REPO/venv/ignored.py"
OUT=$(run false)
[ -z "$OUT" ] && ok "git-ignored .py excluded from gate" || bad "ignored .py linted: $OUT"
rm -rf "$REPO/venv" "$REPO/.gitignore"

# 7) lint runner ERRORS with no findings (exit 2, empty stdout) → block VISIBLY,
#    not a silent fail-open (P2 regression). The gate must surface "could not run".
printf 'import os  # RUFF_DIES\n' > "$REPO/mod.py"
OUT=$(run false)
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "runner failure → blocks (no fail-open)" || bad "runner failure fell open (P2): $OUT"
echo "$OUT" | jq -e '.reason | test("could not run the lint gate")' >/dev/null 2>&1 && ok "block reason names the runner failure" || bad "reason missing runner-failure text: $OUT"
git -C "$REPO" checkout -q -- mod.py

# 8) changed .py path with a SPACE → must reach ruff intact and block (P3 regression:
#    unquoted word-split would pass "bad" and "name.py" as two non-existent paths).
printf 'import os  # LINT_BAD\n' > "$REPO/bad name.py"
OUT=$(run false)
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "path with space reaches ruff (blocks)" || bad "space-path word-split (P3): $OUT"
rm -f "$REPO/bad name.py"

# 9) lint-CLEAN but FORMAT-dirty .py → block on the format finding (U-HK-28 R-12).
printf 'z = 3  # FMT_BAD\n' > "$REPO/mod.py"
OUT=$(run false)
echo "$OUT" | jq -e '.decision=="block"' >/dev/null 2>&1 && ok "blocks on format-dirty .py" || bad "format-dirty .py bypassed gate: $OUT"
echo "$OUT" | jq -e '.reason | test("format:")' >/dev/null 2>&1 && ok "block reason names the format finding" || bad "reason missing format text: $OUT"
git -C "$REPO" checkout -q -- mod.py

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

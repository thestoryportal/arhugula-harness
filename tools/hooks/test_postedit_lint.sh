#!/usr/bin/env bash
# Hermetic test for postedit-lint.sh (U-HK-04). Uses a FAKE ruff on PATH (emits a
# finding iff the file contains the marker # LINT_BAD) so the test is deterministic
# and independent of the real ruff/uv. Exits non-zero on any failed assertion.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/postedit-lint.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT

# Fake ruff: prints a finding for files containing "# LINT_BAD", silent otherwise.
mkdir -p "$REPO/bin"
cat > "$REPO/bin/ruff" <<'EOF'
#!/usr/bin/env bash
sub="$1"; shift          # `check` or `format`
f="${@: -1}"             # last arg = the file path
if [ "$sub" = "format" ]; then
  grep -q '# FMT_BAD' "$f" 2>/dev/null && echo "1 file would be reformatted"
  exit 0
fi
if grep -q '# LINT_BAD' "$f" 2>/dev/null; then
  echo "$f:1:1: F401 fake unused import"
fi
exit 0
EOF
chmod +x "$REPO/bin/ruff"

run() { # $1=file path → drive the hook with an Edit payload
  printf '%s' "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$1\"}}" \
    | PATH="$REPO/bin:$PATH" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" \
    | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null
}

# 1) a .py file with a lint finding → emits.
printf 'import os  # LINT_BAD\n' > "$REPO/bad.py"
OUT=$(run "$REPO/bad.py")
printf '%s' "$OUT" | grep -q "ruff findings" && printf '%s' "$OUT" | grep -q "bad.py" \
  && ok "emits findings for a dirty .py ($(printf '%s' "$OUT" | head -1))" || bad "no emit for dirty .py: '$OUT'"

# 2) a clean .py → silent.
printf 'x = 1\n' > "$REPO/good.py"
OUT=$(run "$REPO/good.py")
[ -z "$OUT" ] && ok "silent for a clean .py" || bad "emitted for clean .py: '$OUT'"

# 3) a non-.py file → silent (skips before ruff).
printf '# LINT_BAD\n' > "$REPO/notes.txt"
OUT=$(run "$REPO/notes.txt")
[ -z "$OUT" ] && ok "silent for non-.py file" || bad "emitted for non-.py: '$OUT'"

# 4) a missing file → silent.
OUT=$(run "$REPO/nonexistent.py")
[ -z "$OUT" ] && ok "silent for missing file" || bad "emitted for missing file: '$OUT'"

# 5) a lint-CLEAN but FORMAT-dirty .py → emits a format finding (U-HK-28 R-12).
printf 'z = 3  # FMT_BAD\n' > "$REPO/fmt.py"
OUT=$(run "$REPO/fmt.py")
printf '%s' "$OUT" | grep -q "format:" && printf '%s' "$OUT" | grep -q "fmt.py" \
  && ok "emits a format finding for an unformatted .py" || bad "no format finding: '$OUT'"

# 6) Hook subprocesses do not inherit the justfile cache fallback. When only uv
# can provide ruff, use the repo-safe /tmp cache.
mv "$REPO/bin/ruff" "$REPO/bin/ruff.saved"
cat > "$REPO/bin/uv" <<'EOF'
#!/usr/bin/env bash
printf '%s' "${UV_CACHE_DIR:-}" > "${UV_CACHE_OBS:?}"
exit 0
EOF
chmod +x "$REPO/bin/uv"
ln -s "$(command -v jq)" "$REPO/bin/jq"
printf 'cache_probe = 1\n' > "$REPO/cache.py"
unset UV_CACHE_DIR
OUT=$(printf '%s' \
  "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$REPO/cache.py\"}}" \
  | env PATH="$REPO/bin:/usr/bin:/bin" CLAUDE_PROJECT_DIR="$REPO" \
    UV_CACHE_OBS="$REPO/uv-cache-observed" bash "$HOOK" \
  | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)
[ -z "$OUT" ] && ok "uv-backed clean post-edit lint stays silent" || bad "uv-backed lint emitted: $OUT"
[ "$(cat "$REPO/uv-cache-observed")" = "/tmp/arhugula-uv-cache" ] \
  && ok "uv-backed post-edit lint uses repo-safe cache" \
  || bad "unsafe uv cache: $(cat "$REPO/uv-cache-observed")"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

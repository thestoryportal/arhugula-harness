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

# --- U-HK-42: the .yaml|.yml parse-check branch -------------------------------
# Fake venv python: prints a pyyaml-shaped error for files containing "YAML_BAD",
# silent otherwise. Same marker-file discipline as the fake ruff above, so the
# cases below assert the HOOK's plumbing, not pyyaml's behaviour. It also logs each
# invocation (the hook cd's to PROJECT_DIR, so a bare relative path lands in $REPO)
# — that log is what makes the CLEAN case load-bearing: asserting silence alone
# would also pass if the hook never ran a YAML check at all.
mkdir -p "$REPO/.venv/bin"
cat > "$REPO/.venv/bin/python" <<'EOF'
#!/usr/bin/env bash
f="${@: -1}"             # last arg = the file path
printf '%s\n' "$f" >> yaml-py-invocations
if grep -q 'YAML_BAD' "$f" 2>/dev/null; then
  echo "bad.yaml: mapping values are not allowed here (line 2, column 8)"
fi
exit 0
EOF
chmod +x "$REPO/.venv/bin/python"

# 7) a .yaml the checker reports on → emits the path AND the parser's error text.
printf 'title: fix: thing  # YAML_BAD\n' > "$REPO/bad.yaml"
OUT=$(run "$REPO/bad.yaml")
printf '%s' "$OUT" | grep -q "\[yaml\] parse error" \
  && printf '%s' "$OUT" | grep -q "bad.yaml" \
  && printf '%s' "$OUT" | grep -q "mapping values are not allowed here" \
  && printf '%s' "$OUT" | grep -q "line 2, column 8" \
  && ok "emits path + parser error for a bad .yaml" || bad "no emit for bad .yaml: '$OUT'"

# 8) a clean multi-document .yml → checker RAN (witnessed) and stayed silent.
printf -- '---\na: 1\n---\nb: 2\n' > "$REPO/clean.yml"
OUT=$(run "$REPO/clean.yml")
[ -z "$OUT" ] && ok "silent for a clean multi-doc .yml" || bad "emitted for clean .yml: '$OUT'"
grep -qx "$REPO/clean.yml" "$REPO/yaml-py-invocations" 2>/dev/null \
  && ok "the clean .yml was actually parse-checked (not just skipped)" \
  || bad "no YAML check ran for the clean .yml"

# 9) extensions the gate must not claim, and a missing .yaml → silent.
printf 'YAML_BAD\n' > "$REPO/notes2.txt"
OUT=$(run "$REPO/notes2.txt")
[ -z "$OUT" ] && ok "silent for a .txt carrying the YAML marker" || bad "emitted for .txt: '$OUT'"
printf '{"YAML_BAD": 1}\n' > "$REPO/data.json"
OUT=$(run "$REPO/data.json")
[ -z "$OUT" ] && ok "silent for a .json carrying the YAML marker" || bad "emitted for .json: '$OUT'"
OUT=$(run "$REPO/nonexistent.yaml")
[ -z "$OUT" ] && ok "silent for a missing .yaml" || bad "emitted for missing .yaml: '$OUT'"

# 10) regression guard: widening the extension gate must not change the .py branch.
mv "$REPO/bin/ruff.saved" "$REPO/bin/ruff"
printf 'import os  # LINT_BAD\n' > "$REPO/bad2.py"
OUT=$(run "$REPO/bad2.py")
printf '%s' "$OUT" | grep -q "ruff findings" && printf '%s' "$OUT" | grep -q "bad2.py" \
  && ok "the .py ruff branch still emits after the gate widening" || bad "ruff branch regressed: '$OUT'"

# 11) no repo venv → fall back to `uv run --quiet python`, never `uv run --with`
# (an ephemeral env on every edit), and still under the repo-safe /tmp uv cache.
rm -rf "$REPO/.venv"
cat > "$REPO/bin/uv" <<'EOF'
#!/usr/bin/env bash
printf '%s' "${UV_CACHE_DIR:-}" > "${UV_CACHE_OBS:?}"
printf '%s' "$*" > "${UV_ARGV_OBS:-/dev/null}"
exit 0
EOF
chmod +x "$REPO/bin/uv"
printf 'a: 1\n' > "$REPO/fallback.yaml"
unset UV_CACHE_DIR
OUT=$(printf '%s' \
  "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$REPO/fallback.yaml\"}}" \
  | env PATH="$REPO/bin:/usr/bin:/bin" CLAUDE_PROJECT_DIR="$REPO" \
    UV_CACHE_OBS="$REPO/uv-cache-observed-yaml" UV_ARGV_OBS="$REPO/uv-argv-observed" \
    bash "$HOOK" \
  | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)
[ -z "$OUT" ] && ok "uv-backed clean yaml parse-check stays silent" || bad "uv-backed yaml emitted: $OUT"
UV_ARGV=$(cat "$REPO/uv-argv-observed" 2>/dev/null)
printf '%s' "$UV_ARGV" | grep -q -- "run --quiet python" \
  && ok "yaml fallback goes through \`uv run --quiet python\`" \
  || bad "yaml fallback argv wrong: '$UV_ARGV'"
printf '%s' "$UV_ARGV" | grep -q -- "--with" \
  && bad "yaml fallback used an ephemeral \`uv run --with\` env: '$UV_ARGV'" \
  || ok "yaml fallback never passes --with"
[ "$(cat "$REPO/uv-cache-observed-yaml")" = "/tmp/arhugula-uv-cache" ] \
  && ok "uv-backed yaml parse-check uses repo-safe cache" \
  || bad "unsafe uv cache: $(cat "$REPO/uv-cache-observed-yaml")"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

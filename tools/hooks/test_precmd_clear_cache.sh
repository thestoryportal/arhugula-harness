#!/usr/bin/env bash
# Hermetic test for precmd-clear-cache.sh (U-HK-03). Builds a throwaway tree with
# __pycache__/.pyc files (incl. a .venv copy that must be preserved) and drives the
# hook with test vs non-test commands. Exits non-zero on any failed assertion.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/precmd-clear-cache.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

seed() { # recreate the fixture cache files under $1
  mkdir -p "$1/pkg/__pycache__" "$1/.venv/lib/__pycache__"
  : > "$1/pkg/__pycache__/mod.cpython-312.pyc"
  : > "$1/pkg/loose.pyc"
  : > "$1/pkg/keep.py"
  : > "$1/.venv/lib/__pycache__/dep.pyc"
}

run() { # $1=command-json-string ; CLAUDE_PROJECT_DIR=$REPO
  printf '%s' "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"$1\"}}" \
    | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"
}

REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT

# 1) a pytest command clears the project's pyc/__pycache__ but preserves .py + .venv.
seed "$REPO"
run "uv run pytest -q"
[ ! -d "$REPO/pkg/__pycache__" ] && ok "test cmd clears project __pycache__" || bad "project __pycache__ survived"
[ ! -f "$REPO/pkg/loose.pyc" ]   && ok "test cmd clears loose .pyc"          || bad "loose .pyc survived"
[ -f "$REPO/pkg/keep.py" ]       && ok "preserves .py source"                || bad ".py source deleted"
[ -f "$REPO/.venv/lib/__pycache__/dep.pyc" ] && ok "preserves .venv pyc (pruned)" || bad ".venv pyc was deleted"

# 2) a non-test command does NOT clear anything.
seed "$REPO"
run "ls -la"
[ -d "$REPO/pkg/__pycache__" ] && [ -f "$REPO/pkg/loose.pyc" ] \
  && ok "non-test command leaves caches intact" || bad "non-test command cleared caches"

# 3) other test-shaped commands also fire (just check / pyright).
seed "$REPO"; run "just check"
[ ! -f "$REPO/pkg/loose.pyc" ] && ok "'just check' fires" || bad "'just check' did not fire"
seed "$REPO"; run "uv run pyright"
[ ! -f "$REPO/pkg/loose.pyc" ] && ok "'pyright' fires" || bad "'pyright' did not fire"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

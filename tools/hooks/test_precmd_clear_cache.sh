#!/usr/bin/env bash
# Hermetic test for precmd-clear-cache.sh (U-HK-03). Builds a throwaway tree with
# __pycache__/.pyc files (incl. a .venv copy that must be preserved) and drives the
# hook with test vs non-test commands. Exits non-zero on any failed assertion.
# Cases 4-7 are the WO-U21 freshness contract any narrower invalidation must keep;
# pass a candidate hook path as $1 to run the same contract against it.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="${1:-$SCRIPT_DIR/precmd-clear-cache.sh}"

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

# The freshness cases import real modules, so they need a clean tree per case.
fresh() { rm -rf "$REPO"; mkdir -p "$REPO/pkg"; : > "$REPO/pkg/__init__.py"; }
py() { # $1=tree under $REPO, $2=python statement, run the way a test command imports
  (cd "$REPO/$1" && python3 -c "$2")
}
found() { # $1=module; prints True when the import system would load it from $REPO
  py . "import importlib.util; print(importlib.util.find_spec('$1') is not None)"
}
stale_edit() { # $1=tree: compile pkg/val.py, then edit it keeping its size and mtime
  mkdir -p "$REPO/$1/pkg"; : > "$REPO/$1/pkg/__init__.py"
  printf 'VALUE = 1\n' > "$REPO/$1/pkg/val.py"; touch -d '2026-01-01 00:00:00' "$REPO/$1/pkg/val.py"
  py "$1" 'import pkg.val' >/dev/null
  printf 'VALUE = 2\n' > "$REPO/$1/pkg/val.py"; touch -d '2026-01-01 00:00:00' "$REPO/$1/pkg/val.py"
}
value() { py "$1" 'import pkg.val; print(pkg.val.VALUE)'; }

# 4) same-size, same-mtime edit. CPython's default pyc records only source mtime and
# size, so the stale pyc is served even under -B; only invalidation makes the edit seen.
fresh; stale_edit .
[ "$(value .)" = 1 ] \
  && ok "precondition: same-size/same-mtime edit is read from the stale pyc" || bad "stale-pyc precondition no longer holds"
[ "$(cd "$REPO" && python3 -B -c 'import pkg.val; print(pkg.val.VALUE)')" = 1 ] \
  && ok "precondition: -B still reads the stale pyc" || bad "-B precondition no longer holds"
run "uv run pytest -q"
[ "$(value .)" = 2 ] && ok "test cmd makes a same-size/same-mtime edit visible" || bad "stale pyc served after the hook"

# 5) renamed or deleted module. A __pycache__ entry is never imported without its
# source, but a legacy pyc beside the source is, so the old name keeps importing.
fresh
printf 'X = 1\n' > "$REPO/pkg/old.py"
(cd "$REPO" && python3 -m compileall -q -b pkg >/dev/null)
mv "$REPO/pkg/old.py" "$REPO/pkg/new.py"
[ "$(found pkg.old)" = True ] && ok "precondition: renamed module still imports from its legacy pyc" \
  || bad "legacy-pyc precondition no longer holds"
run "uv run pytest -q"
[ "$(found pkg.old)" = False ] && ok "test cmd removes the renamed module's legacy pyc" \
  || bad "renamed module still importable after the hook"
[ "$(found pkg.new)" = True ] && ok "renamed module imports under its new name" || bad "new module name not importable"

# 6) lane worktrees nested under the project dir. A session whose project dir is the
# parent may run tests inside one, so the hook must cover their edits too.
fresh
for lane in .worktrees/lane .codex-worktrees/lane; do stale_edit "$lane"; done
run "uv run pytest -q"
for lane in .worktrees/lane .codex-worktrees/lane; do
  [ "$(value "$lane")" = 2 ] && ok "test cmd makes an edit in $lane visible" || bad "stale pyc served in $lane"
done

# 7) import origins. Workspace members import from source through an editable .pth in
# the project's own .venv; an installed (non-editable) copy in site-packages is a
# separate origin that the hook leaves alone, so which origin loads is the
# environment's decision, not the cache's. -S keeps the system site dir out.
site_import() { # prints the VALUE and origin dir of pkg.val as the project's .venv resolves it
  (cd / && python3 -S -c "import site; site.addsitedir('$REPO/.venv/lib/site-packages')
import os, pkg.val as m; print(m.VALUE, os.path.dirname(os.path.dirname(m.__file__)))")
}
fresh; stale_edit src
mkdir -p "$REPO/.venv/lib/site-packages"
printf '%s\n' "$REPO/src" > "$REPO/.venv/lib/site-packages/_editable_impl_pkg.pth"
[ "$(site_import)" = "1 $REPO/src" ] && ok "precondition: editable source import reads the stale pyc" \
  || bad "editable stale-pyc precondition no longer holds"
run "uv run pytest -q"
[ "$(site_import)" = "2 $REPO/src" ] && ok "test cmd makes an edit behind an editable install visible" \
  || bad "stale pyc served through the editable install"
mkdir -p "$REPO/.venv/lib/site-packages/pkg"
: > "$REPO/.venv/lib/site-packages/pkg/__init__.py"
printf 'VALUE = 0\n' > "$REPO/.venv/lib/site-packages/pkg/val.py"
site_import >/dev/null
run "uv run pytest -q"
[ "$(site_import)" = "0 $REPO/.venv/lib/site-packages" ] \
  && ok "an installed copy still shadows the source; the hook leaves origin choice to the environment" \
  || bad "hook changed which origin loads"
[ -n "$(find "$REPO/.venv/lib/site-packages/pkg/__pycache__" -name 'val.*.pyc')" ] \
  && ok "installed copy's pyc preserved" || bad "installed copy's pyc was deleted"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

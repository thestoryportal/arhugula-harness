#!/usr/bin/env bash
# Hermetic test for git-arc-guard.sh (U-HK-16). Builds throwaway local + "origin"
# repos and asserts the advisory systemMessage fires on dirty tree / unpushed commits
# / behind-origin main, and stays silent on a clean synced arc. Never blocks.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/git-arc-guard.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

TMP="$(mktemp -d)"; { [ -n "$TMP" ] && [ -d "$TMP" ]; } || { echo "FATAL mktemp"; exit 1; }
trap 'rm -rf "$TMP"' EXIT
ORIGIN="$TMP/origin.git"; REPO="$TMP/repo"

git init -q --bare "$ORIGIN" -b main
git init -q "$REPO" -b main
git -C "$REPO" config user.email t@t.t; git -C "$REPO" config user.name t
git -C "$REPO" remote add origin "$ORIGIN"
printf 'x\n' > "$REPO/f.txt"; git -C "$REPO" add -A; git -C "$REPO" commit -qm base
git -C "$REPO" push -q -u origin main

run() { printf '%s' "${1:-{\}}" | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"; }
msg() { echo "$1" | jq -r '.systemMessage // empty' 2>/dev/null; }

# 1) Clean + synced → silent (no decision block ever).
OUT=$(run '{"stop_hook_active":false}')
[ -z "$OUT" ] && ok "clean synced arc → silent" || bad "spoke on clean arc: $OUT"

# 2) Dirty tree → flags uncommitted.
printf 'y\n' >> "$REPO/f.txt"
OUT=$(run '{"stop_hook_active":false}')
echo "$(msg "$OUT")" | grep -q "uncommitted" && ok "flags uncommitted changes" || bad "no uncommitted flag: $OUT"
echo "$OUT" | jq -e 'has("decision")' >/dev/null 2>&1 && bad "emitted a decision (must be advisory)" || ok "never blocks (no decision key)"

# 3) Committed but not pushed → flags unpushed.
git -C "$REPO" add -A; git -C "$REPO" commit -qm wip
OUT=$(run '{"stop_hook_active":false}')
echo "$(msg "$OUT")" | grep -q "not pushed" && ok "flags unpushed commits" || bad "no unpushed flag: $OUT"

# 4) stop_hook_active guard → silent even when dirty.
printf 'z\n' >> "$REPO/f.txt"
OUT=$(run '{"stop_hook_active":true}')
[ -z "$OUT" ] && ok "stop_hook_active guard → silent" || bad "spoke despite active flag: $OUT"

# 4b) Untracked-only new file (clean tracked tree) → still flags (codex P2: orphan risk).
git -C "$REPO" reset -q --hard origin/main 2>/dev/null || git -C "$REPO" checkout -q -- .
printf 'new\n' > "$REPO/untracked_new.py"
OUT=$(run '{"stop_hook_active":false}')
echo "$(msg "$OUT")" | grep -q "untracked" && ok "flags untracked-only new file" || bad "no untracked flag: $OUT"
rm -f "$REPO/untracked_new.py"

# 4c) Branch with commits but NO upstream → warns (codex P2: no-upstream blind spot).
git -C "$REPO" checkout -q -b feat/noup
printf 'feat\n' >> "$REPO/f.txt"; git -C "$REPO" add -A; git -C "$REPO" commit -qm feat
OUT=$(run '{"stop_hook_active":false}')
echo "$(msg "$OUT")" | grep -q "no upstream" && ok "flags no-upstream branch with commits" || bad "no no-upstream flag: $OUT"
git -C "$REPO" checkout -q main; git -C "$REPO" branch -q -D feat/noup 2>/dev/null

# 5) Behind-origin main → flags stale-main. Advance origin via a second clone, then
#    refetch into REPO so origin/main is ahead of local main.
git -C "$REPO" reset -q --hard origin/main   # clean local to match origin
CLONE="$TMP/clone"; git clone -q "$ORIGIN" "$CLONE"
git -C "$CLONE" config user.email t@t.t; git -C "$CLONE" config user.name t
printf 'remote\n' >> "$CLONE/f.txt"; git -C "$CLONE" add -A; git -C "$CLONE" commit -qm remote
git -C "$CLONE" push -q origin main
git -C "$REPO" fetch -q origin
OUT=$(run '{"stop_hook_active":false}')
echo "$(msg "$OUT")" | grep -q "behind origin" && ok "flags behind-origin main" || bad "no stale-main flag: $OUT"

echo "----"
echo "git_arc_guard: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

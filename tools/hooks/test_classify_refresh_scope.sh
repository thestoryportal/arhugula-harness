#!/usr/bin/env bash
# Hermetic tests for `classify-refresh-scope.sh` — the classifier that decides whether CI
# skips the blocking test/typecheck/axis-isolation/coverage work.
#
# Auto-discovered by `tools/codex-parity-check.sh` (`for test_script in
# tools/hooks/test_*.sh`), so these run in the blocking CI lane with no extra plumbing.
#
# The git-range cases build real throwaway repos rather than stubbing git, because the
# defect this suite exists to prevent was precisely a WRONG RANGE (`HEAD^ HEAD` reading
# only the last commit of a multi-commit push) — a stub would have encoded the bug.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLASSIFY="$SCRIPT_DIR/classify-refresh-scope.sh"
BLESSED='.harness/roadmap_status.md'

pass=0
fail=0

check() {
  local label="$1" expected="$2" got="$3"
  if [ "$got" = "$expected" ]; then
    pass=$((pass + 1))
    echo "ok   $label"
  else
    fail=$((fail + 1))
    echo "FAIL $label — expected '$expected', got '$got'"
  fi
}

# ─── list-driven cases (CHANGED_FILES bypasses git) ────────────────────────────
list_case() {
  local label="$1" expected="$2" files="$3"
  local got
  got="$(CHANGED_FILES="$files" bash "$CLASSIFY" 2>/dev/null)"
  check "$label" "$expected" "$got"
}

list_case "blessed file alone"            true  "$BLESSED"
list_case "blessed listed twice"          true  "$BLESSED
$BLESSED"
list_case "empty set fails closed"        false ""
list_case "code file alone"               false "harness-od/src/harness_od/sampling_mode.py"
list_case "blessed + code"                false "$BLESSED
harness-od/src/harness_od/sampling_mode.py"
list_case "blessed + another doc"         false "$BLESSED
.harness/arc-ledger.yaml"
list_case "suffix trap (.bak)"            false "${BLESSED}.bak"
list_case "prefix trap (x-prefixed)"      false "x${BLESSED}"
list_case "sibling archive is not blessed" false ".harness/roadmap-next-action-archive.md"
list_case "workflow change is not blessed" false ".github/workflows/ci.yml"

# ─── git-range cases (real fixture repos) ──────────────────────────────────────
mk_repo() {
  local dir
  dir="$(mktemp -d)"
  git -C "$dir" init -q
  git -C "$dir" config user.email t@example.com
  git -C "$dir" config user.name t
  mkdir -p "$dir/.harness" "$dir/src"
  echo seed >"$dir/src/seed.txt"
  git -C "$dir" add -A
  git -C "$dir" commit -qm seed
  echo "$dir"
}

# (1) THE REGRESSION THIS SUITE EXISTS FOR: a multi-commit push whose LAST commit touches
# only the blessed file, but an EARLIER commit in the same push touches code. `HEAD^ HEAD`
# would say true (fast path, blocking jobs skipped on a code change); the whole-range
# comparison must say false.
repo="$(mk_repo)"
before="$(git -C "$repo" rev-parse HEAD)"
echo change >>"$repo/src/seed.txt"
git -C "$repo" commit -qam "code commit"
echo refresh >"$repo/$BLESSED"
git -C "$repo" add -A
git -C "$repo" commit -qm "refresh commit"
got="$(cd "$repo" && PUSH_BEFORE="$before" bash "$CLASSIFY" 2>/dev/null)"
check "multi-commit push: code then refresh" false "$got"

# ...and the single-commit refresh push in the same repo shape IS the fast path.
before2="$(git -C "$repo" rev-parse HEAD)"
echo refresh2 >"$repo/$BLESSED"
git -C "$repo" commit -qam "second refresh"
got="$(cd "$repo" && PUSH_BEFORE="$before2" bash "$CLASSIFY" 2>/dev/null)"
check "single-commit refresh push" true "$got"

# (2) Unusable PUSH_BEFORE values must fail closed, not fall back to a guess.
got="$(cd "$repo" && PUSH_BEFORE=0000000000000000000000000000000000000000 bash "$CLASSIFY" 2>/dev/null)"
check "all-zero PUSH_BEFORE (branch creation)" false "$got"
got="$(cd "$repo" && PUSH_BEFORE=deadbeefdeadbeefdeadbeefdeadbeefdeadbeef bash "$CLASSIFY" 2>/dev/null)"
check "unreachable PUSH_BEFORE (force-push)" false "$got"
got="$(cd "$repo" && bash "$CLASSIFY" 2>/dev/null)"
check "no range at all" false "$got"

# (3) PR shape: BASE_SHA...HEAD over a branch carrying a refresh-only commit.
before3="$(git -C "$repo" rev-parse HEAD)"
git -C "$repo" checkout -qb topic
echo refresh3 >"$repo/$BLESSED"
git -C "$repo" commit -qam "pr refresh"
got="$(cd "$repo" && BASE_SHA="$before3" bash "$CLASSIFY" 2>/dev/null)"
check "PR base...HEAD, refresh only" true "$got"
echo more >>"$repo/src/seed.txt"
git -C "$repo" commit -qam "pr code"
got="$(cd "$repo" && BASE_SHA="$before3" bash "$CLASSIFY" 2>/dev/null)"
check "PR base...HEAD, refresh + code" false "$got"

# (4) GITHUB_OUTPUT is actually written, not just echoed — the workflow reads that file.
outfile="$(mktemp)"
CHANGED_FILES="$BLESSED" GITHUB_OUTPUT="$outfile" bash "$CLASSIFY" >/dev/null 2>&1
check "writes refresh_only to GITHUB_OUTPUT" "refresh_only=true" "$(cat "$outfile")"

command rm -rf "$repo" "$outfile"

echo "---"
echo "classify-refresh-scope: $pass passed, $fail failed"
[ "$fail" -eq 0 ]

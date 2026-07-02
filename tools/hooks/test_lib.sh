#!/usr/bin/env bash
# Unit tests for tools/hooks/lib.sh. Hermetic (no network; temp git repo for the
# branch/loop-marker cases). Exits non-zero on any failed assertion (CI-friendly).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/lib.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
eq()  { [ "$2" = "$3" ] && ok "$1 ($2)" || bad "$1: got '$2' want '$3'"; }

# hook_state_hash — deterministic 12-hex, matches the raw recipe.
WANT=$(printf '%s|%s|%s|%s' a b c d | shasum -a 256 | head -c 12)
eq "hook_state_hash matches recipe" "$(hook_state_hash a b c d)" "$WANT"
[ "$(hook_state_hash a b c d | wc -c | tr -d ' ')" = "12" ] && ok "hash is 12 chars" || bad "hash not 12 chars"

# hook_is_dashboard_only_set — §12.2.1 closed-set: EXACTLY {roadmap_status.md} OR
# EXACTLY {roadmap_status.md, roadmap.html}. Inputs mirror the callers' `sort -u`
# output ('.harness/…' sorts before 'tools/…' / 'other…'). The two-file case is the
# regression this fix targets (HTML-regenerating refresh wrongly read as substantive).
_STATUS=".harness/roadmap_status.md"
_HTML="tools/dashboard/roadmap.html"
is_set()  { hook_is_dashboard_only_set "$1" && ok "dashboard-only: $2" || bad "expected dashboard-only ($2): '$1'"; }
not_set() { hook_is_dashboard_only_set "$1" && bad "expected NOT dashboard-only ($2): '$1'" || ok "not dashboard-only: $2"; }
is_set  "$_STATUS"                              "status-only refresh"
is_set  "$(printf '%s\n%s' "$_STATUS" "$_HTML")" "status + regenerated HTML (the fix)"
not_set "$(printf '%s\n%s' "$_STATUS" "other.txt")" "status + a foreign file (mis-titled substantive)"
not_set "$_HTML"                               "HTML alone (status absent)"
not_set ""                                     "empty set"
not_set "$(printf '%s\n%s\n%s' "$_STATUS" "$_HTML" "src/x.py")" "status + HTML + extra → closed-set rejects"

# hook_json — extracts a path; empty default on miss.
eq "hook_json extracts command" "$(hook_json '{"tool_input":{"command":"echo hi"}}' '.tool_input.command')" "echo hi"
eq "hook_json empty on miss"    "$(hook_json '{"a":1}' '.tool_input.command')" ""
eq "hook_json empty on junk"    "$(hook_json 'not json' '.x')" ""

# hook_read_stdin — round-trips stdin.
eq "hook_read_stdin round-trips" "$(printf 'payload-x' | hook_read_stdin)" "payload-x"

# hook_emit — emits the additionalContext JSON and exits 0 (captured in a subshell).
OUT=$(hook_emit "SessionStart" "hello world")
echo "$OUT" | jq -e '.hookSpecificOutput.hookEventName=="SessionStart" and .hookSpecificOutput.additionalContext=="hello world"' >/dev/null \
  && ok "hook_emit JSON shape" || bad "hook_emit bad JSON: $OUT"

# hook_bounded — a fast command returns 0; a slow command is killed within the bound.
hook_bounded 5 true && ok "hook_bounded fast cmd rc=0" || bad "hook_bounded fast cmd nonzero"
SECONDS=0
hook_bounded 1 sleep 10 >/dev/null 2>&1; RC=$?
EL=$SECONDS
{ [ "$EL" -lt 5 ] && [ "$RC" -ne 0 ]; } && ok "hook_bounded kills slow cmd (~${EL}s, rc=$RC)" \
  || bad "hook_bounded did not bound: elapsed=${EL}s rc=$RC"

# hook_project_dir — honors CLAUDE_PROJECT_DIR override.
eq "hook_project_dir honors env" "$(CLAUDE_PROJECT_DIR=/tmp/xyz hook_project_dir)" "/tmp/xyz"

# hook_bounded — force-kills a TERM-ignoring command within the bound (escalation).
SECONDS=0
hook_bounded 1 bash -c 'trap "" TERM; sleep 30' >/dev/null 2>&1; RC2=$?
EL2=$SECONDS
{ [ "$EL2" -lt 8 ] && [ "$RC2" -ne 0 ]; } && ok "hook_bounded escalates TERM->KILL (~${EL2}s, rc=$RC2)" \
  || bad "hook_bounded did not force-kill TERM-ignorer: elapsed=${EL2}s rc=$RC2"

# Temp repo for default-branch + loop-mode marker tests.
REPO="$(mktemp -d)"
{ [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
git -C "$REPO" init -q -b main; git -C "$REPO" config user.email t@t.t; git -C "$REPO" config user.name t
( cd "$REPO" && echo x > f && git add -A && git commit -qm base )

# hook_default_branch — falls back to main when no origin/HEAD symref.
eq "hook_default_branch fallback main" "$(cd "$REPO" && hook_default_branch)" "main"

# hook_roadmap_next — scopes to the `## Next action` section, so a STALE bolded R-id
# in a later narrative section does NOT shadow the live pointer (the whole-file
# head -1 bug). It also ignores range/banner tokens like `R-410..R-440`; those are
# menus, not actionable roadmap units. Fixture mirrors the real dashboard: a
# backticked range banner + a backticked concrete pointer in the section + a strict
# `**`R-OLD`**` token AFTER the `---` rule.
DASHF="$REPO/dash.md"
cat > "$DASHF" <<'EOF'
# dash
| `git_head` | `abc12345` (main) |
## Next action
> directive prose; pick the highest-value item `R-410..R-440` then `R-300-x`.
---
## Recently completed
**`R-OLD-stale-narrative`** was closed earlier (must NOT be picked).
EOF
eq "hook_roadmap_next skips range token and picks concrete pointer" "$(hook_roadmap_next "$DASHF")" "R-300-x"
cat > "$DASHF" <<'EOF'
# dash
## Next action
**Current next action.** Continue the memory substrate build. U-MEM-09 is merged; the next implementable unit is U-MEM-10, the Information-substrate derived retrieval indexes unit.

**Recurring lanes** continue on cadence: `R-600-pattern-bake-in-sweep` and `R-IF-roadmap-refresh`.
---
EOF
eq "hook_roadmap_next picks U-MEM frontier before recurring R lane" "$(hook_roadmap_next "$DASHF")" "U-MEM-10"
# Absent section / file → empty (callers default to '?').
eq "hook_roadmap_next empty on missing file" "$(hook_roadmap_next "$REPO/nope.md")" ""
printf '# d\nno next-action heading here\n' > "$DASHF"
eq "hook_roadmap_next empty when no section" "$(hook_roadmap_next "$DASHF")" ""

# loop_mode_active — off by default; on via env; on via marker file.
( cd "$REPO"; unset HARNESS_LOOP; CLAUDE_PROJECT_DIR="$REPO" loop_mode_active ) \
  && bad "loop_mode_active true with no gate" || ok "loop_mode_active off by default"
( cd "$REPO"; HARNESS_LOOP=1 loop_mode_active ) && ok "loop_mode_active on via env" || bad "loop_mode_active env ignored"
mkdir -p "$REPO/.harness"; : > "$REPO/.harness/.loop-active"
( cd "$REPO"; unset HARNESS_LOOP; CLAUDE_PROJECT_DIR="$REPO" loop_mode_active ) \
  && ok "loop_mode_active on via marker file" || bad "loop_mode_active marker ignored"

# hook_write_checkpoint (U-HK-27 shared snapshot writer): writes precompact-latest.md with
# the label; skip_gh omits the open-PRs gh lookup (fast path — no network in this test).
CLAUDE_PROJECT_DIR="$REPO" hook_write_checkpoint "Test snapshot" skip_gh
LATEST="$REPO/.harness/.checkpoints/precompact-latest.md"
[ -f "$LATEST" ] && ok "hook_write_checkpoint wrote precompact-latest.md" || bad "no checkpoint file"
grep -q "Test snapshot" "$LATEST" 2>/dev/null && ok "checkpoint carries the label" || bad "label missing"
grep -q "skipped — fast path" "$LATEST" 2>/dev/null && ok "skip_gh omits gh PR lookup" || bad "skip_gh not honored"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

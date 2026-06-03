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

# Temp repo for default-branch + loop-mode marker tests.
REPO="$(mktemp -d)"; trap 'rm -rf "$REPO"' EXIT
git -C "$REPO" init -q -b main; git -C "$REPO" config user.email t@t.t; git -C "$REPO" config user.name t
( cd "$REPO" && echo x > f && git add -A && git commit -qm base )

# hook_default_branch — falls back to main when no origin/HEAD symref.
eq "hook_default_branch fallback main" "$(cd "$REPO" && hook_default_branch)" "main"

# loop_mode_active — off by default; on via env; on via marker file.
( cd "$REPO"; unset HARNESS_LOOP; CLAUDE_PROJECT_DIR="$REPO" loop_mode_active ) \
  && bad "loop_mode_active true with no gate" || ok "loop_mode_active off by default"
( cd "$REPO"; HARNESS_LOOP=1 loop_mode_active ) && ok "loop_mode_active on via env" || bad "loop_mode_active env ignored"
mkdir -p "$REPO/.harness"; : > "$REPO/.harness/.loop-active"
( cd "$REPO"; unset HARNESS_LOOP; CLAUDE_PROJECT_DIR="$REPO" loop_mode_active ) \
  && ok "loop_mode_active on via marker file" || bad "loop_mode_active marker ignored"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

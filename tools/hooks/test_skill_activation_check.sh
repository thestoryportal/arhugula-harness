#!/usr/bin/env bash
# Hermetic test for skill-activation-check.sh (U-HK-21). Asserts: known skills +
# built-ins + namespaced + non-commands are SILENT, and only an unknown near-miss of a
# real skill emits a "did you mean" hint. HOME is overridden so the user-skills lookup
# is hermetic (no dependence on the dev's real ~/.claude/skills).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/skill-activation-check.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"; HOMED="$(mktemp -d)"
{ [ -d "$REPO" ] && [ -d "$HOMED" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO" "$HOMED"' EXIT
# Controlled project skill set: council + resolve. Empty user skill set.
mkdir -p "$REPO/.claude/skills/council" "$REPO/.claude/skills/resolve" "$HOMED/.claude/skills"
: > "$REPO/.claude/skills/council/SKILL.md"
: > "$REPO/.claude/skills/resolve/SKILL.md"

run() { # $1 = prompt text
  printf '%s' "{\"hook_event_name\":\"UserPromptSubmit\",\"prompt\":$(jq -Rn --arg p "$1" '$p')}" \
    | CLAUDE_PROJECT_DIR="$REPO" HOME="$HOMED" bash "$HOOK" \
    | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null
}

# 1) known project skill → silent.
OUT=$(run "please /council on this tension")
[ -z "$OUT" ] && ok "known skill /council silent" || bad "spoke on known skill: $OUT"

# 2) built-in command → silent.
OUT=$(run "/clear")
[ -z "$OUT" ] && ok "built-in /clear silent" || bad "spoke on built-in: $OUT"

# 3) unknown near-miss of a real skill → hint.
OUT=$(run "/resolv this")
printf '%s' "$OUT" | grep -q "/resolv->/resolve?" && ok "typo /resolv hints /resolve ($OUT)" \
  || bad "no hint for /resolv typo: $OUT"

# 4) unknown with NO plausible correction → silent.
OUT=$(run "/xyzzy go")
[ -z "$OUT" ] && ok "unknown-no-nearmatch /xyzzy silent" || bad "spoke on unmatchable cmd: $OUT"

# 5) plugin-namespaced command → silent (can't validate locally).
OUT=$(run "/gstack:foo run it")
[ -z "$OUT" ] && ok "namespaced /gstack:foo silent" || bad "spoke on namespaced cmd: $OUT"

# 6) no slash-command → silent.
OUT=$(run "continue to wave 3")
[ -z "$OUT" ] && ok "no-command prompt silent" || bad "spoke on plain prompt: $OUT"

# 7) path fragment, not a command (preceded by non-space) → silent.
OUT=$(run "open tools/hooks/lib.sh")
[ -z "$OUT" ] && ok "path fragment not treated as command" || bad "spoke on path fragment: $OUT"

# 8) a leading /tmp path-ish token with no near-match → silent (no false positive).
OUT=$(run "/tmp/scratch")
[ -z "$OUT" ] && ok "leading /tmp token silent (no near-match)" || bad "spoke on /tmp: $OUT"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

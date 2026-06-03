#!/usr/bin/env bash
# Hermetic test for skill-activation-check.sh (U-HK-21). Asserts: known skills (incl.
# NESTED ones) + built-ins + namespaced + non-commands are SILENT, and only a
# prefix-anchored near-miss (length >= 4) of a real skill emits a "did you mean" hint.
# HOME is overridden so the user-skills lookup is hermetic.
#
# Regression coverage for the two out-of-family Codex findings on the first cut:
#   P2 — nested skills under a grouping dir (.claude/skills/council/<voice>/SKILL.md)
#        must be discovered (recursive walk + frontmatter `name:`), else a typo of them
#        gets no hint.
#   P3 — short / suffix-only substring matches (`/pr`->ship-pr) are noise; the hook must
#        stay silent on them (prefix-anchored + length floor).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/skill-activation-check.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"; HOMED="$(mktemp -d)"
{ [ -d "$REPO" ] && [ -d "$HOMED" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO" "$HOMED"' EXIT
# Controlled skill set mirroring the real layout: top-level resolve + ship-pr, and a
# NESTED council voice (the P2 case). Empty user skill set.
mkdir -p "$REPO/.claude/skills/resolve" "$REPO/.claude/skills/ship-pr" \
         "$REPO/.claude/skills/council/council-orchestrator" "$HOMED/.claude/skills"
printf -- '---\nname: resolve\n---\n'              > "$REPO/.claude/skills/resolve/SKILL.md"
printf -- '---\nname: ship-pr\n---\n'              > "$REPO/.claude/skills/ship-pr/SKILL.md"
printf -- '---\nname: council-orchestrator\n---\n' > "$REPO/.claude/skills/council/council-orchestrator/SKILL.md"

run() { # $1 = prompt text
  printf '%s' "{\"hook_event_name\":\"UserPromptSubmit\",\"prompt\":$(jq -Rn --arg p "$1" '$p')}" \
    | CLAUDE_PROJECT_DIR="$REPO" HOME="$HOMED" bash "$HOOK" \
    | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null
}
silent() { local o; o=$(run "$1"); [ -z "$o" ] && ok "silent '$1'" || bad "spoke on '$1' -> $o"; }
hints()  { local o; o=$(run "$1"); printf '%s' "$o" | grep -q "$2" && ok "hint '$1' -> $2" || bad "expected '$2' for '$1', got: $o"; }

# --- knowns / built-ins / structure: SILENT ---
silent "please /resolve this"                       # top-level known
silent "convene the /council-orchestrator"          # NESTED known (P2: recursive discovery)
silent "/clear"                                      # built-in
silent "/gstack:foo run it"                          # plugin-namespaced (can't validate)
silent "continue to wave 3"                          # no slash-command
silent "open tools/hooks/lib.sh"                     # path fragment (preceded by non-space)
silent "/tmp/scratch"                                # leading /tmp, no near-match

# --- genuine prefix-anchored typos (>=4 chars): HINT ---
hints "/resolv this"            "/resolv->/resolve?"
hints "/ship the change"        "/ship->/ship-pr?"
hints "/council-orchestrat go"  "/council-orchestrat->/council-orchestrator?"   # P2: nested in _known

# --- P3: short / suffix-only matches must be SILENT (the Codex false-positives) ---
silent "/pr"        # suffix of ship-pr, len 2 -> noise, must be silent
silent "/shi"       # len 3 (< 4 floor) -> silent even though prefix of ship-pr
silent "/xyzzy go"  # no plausible correction

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

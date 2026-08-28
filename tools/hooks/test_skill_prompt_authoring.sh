#!/usr/bin/env bash
# Wiring test for the laws:prompt authoring rule (U-SR-03, charter WR-08a).
#
# The rule is one paragraph copied into every skill that fans subagents out. Copies are
# permitted only because this test SYNCHRONISES them: it extracts the paragraph from each
# carrier and requires the extractions to be byte-identical, so an edit to one carrier reds
# here instead of silently becoming a second, divergent authority ([LAW:one-source-of-truth]
# -- a derived copy is legal exactly when something mechanical keeps it derived).
#
# It also pins the two facts the paragraph asserts about the world, because prose can go
# stale against the mechanism it describes: the advisory hook it names must exist, and the
# merge-gate carrier's binding instruction must be the by-file form (WR-09), not the
# paste-the-values form the change replaced.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/../.." && pwd)"

CARRIERS=(
  ".claude/skills/merge-gate/SKILL.md"
  ".claude/skills/fan-out/SKILL.md"
  ".claude/skills/council/council-orchestrator/SKILL.md"
)
ANCHOR='**Subagent prompts are authored under `laws:prompt` (U-SR-03, charter WR-08).**'

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

# The paragraph = the anchor line through the first blank line after it.
extract() { awk -v a="$ANCHOR" '
  index($0, a) { on = 1 }
  on && /^[[:space:]]*$/ { exit }
  on { print }
' "$1"; }

REF=""; REF_FROM=""
for rel in "${CARRIERS[@]}"; do
  path="$REPO/$rel"
  [ -f "$path" ] || { bad "carrier missing: $rel"; continue; }
  block=$(extract "$path")
  if [ -z "$block" ]; then
    bad "$rel does not carry the authoring rule"
    continue
  fi
  ok "$rel carries the authoring rule"
  if [ -z "$REF" ]; then
    REF="$block"; REF_FROM="$rel"
  elif [ "$block" = "$REF" ]; then
    ok "$rel is byte-identical to $REF_FROM"
  else
    bad "$rel has DRIFTED from $REF_FROM"
    # `diff` exits 1 whenever the files differ, which is precisely this branch, so its
    # status carries no information here and is not consulted. Its stderr is left alone:
    # a diff that cannot run should say so rather than silently print nothing.
    printf '%s\n' "$REF" > /tmp/_apa_ref.$$
    printf '%s\n' "$block" > /tmp/_apa_got.$$
    diff /tmp/_apa_ref.$$ /tmp/_apa_got.$$ | sed 's/^/      /'
    rm -f /tmp/_apa_ref.$$ /tmp/_apa_got.$$
  fi
done

# The paragraph must actually say the three things it exists to say.
printf '%s' "$REF" | grep -q 'skill-canonical template' \
  && ok "rule states the inline exception" || bad "rule omits the skill-canonical-template exception"
printf '%s' "$REF" | grep -q 'never denies' \
  && ok "rule states the hook is advisory" || bad "rule omits that the hook never denies"

# The mechanism the paragraph names must exist.
[ -x "$REPO/tools/hooks/agent-prompt-advisory.sh" ] \
  && ok "the advisory hook the rule names is present and executable" \
  || bad "rule names agent-prompt-advisory but the hook is missing/not executable"

# WR-09: neither merge-gate carrier may still tell the reader to paste the values.
for rel in ".claude/skills/merge-gate/SKILL.md" ".agents/skills/merge-gate/SKILL.md"; do
  text=$(cat "$REPO/$rel")
  printf '%s' "$text" | grep -qi 'paste the six\|include the six printed values' \
    && bad "$rel still instructs hand-copying the binding values" \
    || ok "$rel does not instruct hand-copying the binding values"
  printf '%s' "$text" | grep -q 'merge-gate-binding' \
    && ok "$rel still routes through the binding recipe" \
    || bad "$rel lost the binding recipe reference"
done

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

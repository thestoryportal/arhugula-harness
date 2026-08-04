#!/usr/bin/env bash
# Hermetic test for the U-WT-05 red-first skill. Asserts the ritual's load-bearing contract
# is present in BOTH carriers — the Claude skill at `.claude/skills/red-first/SKILL.md` and
# its Codex-native projection at `.agents/skills/red-first/SKILL.md` (the .agents tree
# encodes its rituals independently, so a Claude-only skill is undiscoverable from the Codex
# flow — the parity failure this test exists to catch).
#
# Six contract elements per carrier, each with a per-carrier FIXED-STRING needle that the
# file's sibling prose cannot satisfy (a bare "PR body" or "sha256" is satisfied by the
# surrounding narration; the needles below name the specific obligation):
#   1. Adversary role section        4. opt-in-only statement
#   2. Implementer role section      5. sha256 handoff fence
#   3. not-the-adversarial-reviewer  6. `# mutation-probe:` annotation format
# plus the fail-closed verdict protocol, the CUT-no-Breaker statement, the probe command the
# completion gate runs, and the red-evidence-in-PR-body requirement.
#
# Doc-text assertions run against the REAL repo SKILL.md files resolved from SCRIPT_DIR (no
# scratch repo: the artifact under test IS the checked-in skill text).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_SKILL="$SCRIPT_DIR/../../.claude/skills/red-first/SKILL.md"
CODEX_SKILL="$SCRIPT_DIR/../../.agents/skills/red-first/SKILL.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$CLAUDE_SKILL" "$CODEX_SKILL"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

# $1 = file, $2 = carrier label, $3 = contract element, $4 = fixed-string needle
needle() {
  if grep -qF -- "$4" "$1"; then
    ok "$2 carries $3"
  else
    bad "$2 missing $3 (needle: $4)"
  fi
}

# line number of the first line matching a fixed string, empty if absent
lineno() { grep -nF -- "$2" "$1" | head -1 | cut -d: -f1; }

# --- 1. Claude carrier: frontmatter + the six contract elements -------------------------
needle "$CLAUDE_SKILL" "claude red-first" "its skill name in frontmatter" 'name: red-first'
needle "$CLAUDE_SKILL" "claude red-first" "the Adversary role section" \
  '## Phase 1 — Adversary (a plain Agent-tool subagent)'
needle "$CLAUDE_SKILL" "claude red-first" "the Implementer role section" \
  "## Phase 2 — Implementer (may not edit the adversary's test file)"
needle "$CLAUDE_SKILL" "claude red-first" "the not-the-adversarial-reviewer constraint" \
  'The Adversary is NOT the `harness-adversarial-reviewer` skill.'
needle "$CLAUDE_SKILL" "claude red-first" "the opt-in-only statement" \
  '**Opt-in only — never auto-invoked from `roadmap-continue` or `ship-pr`.**'
needle "$CLAUDE_SKILL" "claude red-first" "the sha256 handoff fence" \
  "record the test file's \`sha256\` and re-compare it at the completion gate"
needle "$CLAUDE_SKILL" "claude red-first" "the mutation-probe annotation format" \
  '# mutation-probe: <file>:<lines>'

# --- 2. Claude carrier: gate mechanics + verdict protocol -------------------------------
needle "$CLAUDE_SKILL" "claude red-first" "the fence-is-not-a-permission-deny statement" \
  'recorded-digest fence, not a permission-guard deny'
needle "$CLAUDE_SKILL" "claude red-first" "the completion-gate probe command" \
  'just mutation-probe --file F --lines A-B --test'
needle "$CLAUDE_SKILL" "claude red-first" "the red-evidence-in-PR-body requirement" \
  'paste the failing output verbatim into the PR body'
needle "$CLAUDE_SKILL" "claude red-first" "the CUT-no-Breaker statement" \
  '**CUT: no Breaker role.**'
needle "$CLAUDE_SKILL" "claude red-first" "the BLOCK verdict line" \
  'RED-FIRST: BLOCK: <one-sentence reason>'
needle "$CLAUDE_SKILL" "claude red-first" "the fail-closed unparseable-verdict rule" \
  'RED-FIRST: BLOCK: unparseable verdict'

# --- 3. Claude carrier: Adversary precedes Implementer ----------------------------------
C_ADV=$(lineno "$CLAUDE_SKILL" '## Phase 1 — Adversary')
C_IMP=$(lineno "$CLAUDE_SKILL" '## Phase 2 — Implementer')
C_GATE=$(lineno "$CLAUDE_SKILL" '## Completion gate')
if [ -n "$C_ADV" ] && [ -n "$C_IMP" ] && [ -n "$C_GATE" ] \
   && [ "$C_ADV" -lt "$C_IMP" ] && [ "$C_IMP" -lt "$C_GATE" ]; then
  ok "claude red-first orders Adversary($C_ADV) < Implementer($C_IMP) < gate($C_GATE)"
else
  bad "claude red-first ordering: adversary='$C_ADV' implementer='$C_IMP' gate='$C_GATE'"
fi

# --- 4. Codex carrier: frontmatter + the six contract elements ---------------------------
# Independently phrased: the .agents tree writes plain markdown with no Claude-specific tool
# names, so these needles are NOT the Claude ones re-used.
needle "$CODEX_SKILL" "codex-native red-first" "its skill name in frontmatter" 'name: red-first'
needle "$CODEX_SKILL" "codex-native red-first" "the Adversary role section" \
  '## Adversary phase'
needle "$CODEX_SKILL" "codex-native red-first" "the Implementer role section" \
  '## Implementer phase'
needle "$CODEX_SKILL" "codex-native red-first" "the not-the-adversarial-reviewer constraint" \
  'The adversary must not be the harness-adversarial-reviewer skill.'
needle "$CODEX_SKILL" "codex-native red-first" "the opt-in-only statement" \
  'This skill is opt-in. Never invoke it automatically from roadmap-continue or ship-pr.'
needle "$CODEX_SKILL" "codex-native red-first" "the sha256 handoff fence" \
  'Record the sha256 of the adversary test file at handoff'
needle "$CODEX_SKILL" "codex-native red-first" "the mutation-probe annotation format" \
  '# mutation-probe: <file>:<lines>'

# --- 5. Codex carrier: gate mechanics + verdict protocol --------------------------------
needle "$CODEX_SKILL" "codex-native red-first" "the fence-is-not-a-permission-deny statement" \
  'not a permission-guard deny'
needle "$CODEX_SKILL" "codex-native red-first" "the completion-gate probe command" \
  'just mutation-probe --file F --lines A-B --test'
needle "$CODEX_SKILL" "codex-native red-first" "the red-evidence-in-PR-body requirement" \
  'Paste the verbatim failing output into the PR body'
needle "$CODEX_SKILL" "codex-native red-first" "the no-Breaker statement" \
  'No Breaker role exists, deliberately.'
needle "$CODEX_SKILL" "codex-native red-first" "the BLOCK verdict line" \
  'RED-FIRST: BLOCK: <one-sentence reason>'
needle "$CODEX_SKILL" "codex-native red-first" "the fail-closed verdict rule" \
  'Missing, malformed, truncated, or ambiguous output is `RED-FIRST: BLOCK`.'

# --- 6. Codex carrier: Adversary precedes Implementer -----------------------------------
A_ADV=$(lineno "$CODEX_SKILL" '## Adversary phase')
A_IMP=$(lineno "$CODEX_SKILL" '## Implementer phase')
A_GATE=$(lineno "$CODEX_SKILL" '## Completion gate')
if [ -n "$A_ADV" ] && [ -n "$A_IMP" ] && [ -n "$A_GATE" ] \
   && [ "$A_ADV" -lt "$A_IMP" ] && [ "$A_IMP" -lt "$A_GATE" ]; then
  ok "codex-native red-first orders Adversary($A_ADV) < Implementer($A_IMP) < gate($A_GATE)"
else
  bad "codex-native red-first ordering: adversary='$A_ADV' implementer='$A_IMP' gate='$A_GATE'"
fi

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

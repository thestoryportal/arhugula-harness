#!/usr/bin/env bash
# Hermetic test for the U-WT-05 red-first skill, asserted across BOTH carriers — but they
# carry DIFFERENT contracts, which is the point of this file:
#
#   * `.claude/skills/red-first/SKILL.md` is the CANONICAL body. It must carry the ritual in
#     full: both roles, the not-the-adversarial-reviewer constraint, the opt-in statement, the
#     sha256 handoff fence, the `# mutation-probe:` annotation format (including how an
#     annotation is resolved when the pinned lines do not exist yet), the completion gate's
#     probe invocation, and the fail-closed verdict lines.
#   * `.agents/skills/red-first/SKILL.md` is a POINTER BRIDGE, not an independent projection.
#     red-first is not one of the three Codex-native workflows
#     ({merge-gate, roadmap-continue, ship-pr}), so the non-native-bridge test in
#     `tools/test_codex_workflow_parity.py` requires it to name the canonical path, defer to
#     it completely, and apply runner translations only. Duplicating the role/gate sections
#     here is the defect this asserts against — a second copy of the contract is a second
#     thing to drift.
#
# Needles are per-carrier FIXED STRINGS chosen so the file's sibling prose cannot satisfy them
# (a bare "PR body" or "sha256" is satisfied by the surrounding narration; the needles below
# name the specific obligation). Doc-text assertions run against the REAL repo SKILL.md files
# resolved from SCRIPT_DIR (no scratch repo: the artifact under test IS the checked-in text).

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

# $1 = file, $2 = carrier label, $3 = what must be absent, $4 = fixed-string needle
absent() {
  if grep -qF -- "$4" "$1"; then
    bad "$2 must not carry $3 (found: $4)"
  else
    ok "$2 omits $3"
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
needle "$CLAUDE_SKILL" "claude red-first" "the operator-request-only invocation rule" \
  '**It fires only on an operator'
needle "$CLAUDE_SKILL" "claude red-first" "the sha256 handoff fence" \
  "record the test file's \`sha256\` and re-compare it at the completion gate"
needle "$CLAUDE_SKILL" "claude red-first" "the mutation-probe annotation format" \
  '# mutation-probe: <file>:<lines>'

# --- 2. Claude carrier: fence semantics, honestly stated --------------------------------
# The digest proves byte-identity of the FINAL file, which a perfect revert satisfies by
# definition. The earlier "distinguishes an untouched test from an edited one" claim was
# false (identical bytes → identical digest) and must not come back.
needle "$CLAUDE_SKILL" "claude red-first" "the byte-identity claim the digest actually makes" \
  'final test file is byte-identical to what the Adversary handed off'
needle "$CLAUDE_SKILL" "claude red-first" "the fence-is-not-a-permission-deny statement" \
  'recorded-digest fence, not a permission-guard deny'
absent "$CLAUDE_SKILL" "claude red-first" "the falsified edit-detection claim" \
  'distinguishes an untouched adversary test from an edited one'

# --- 3. Claude carrier: post-green resolution of EVERY annotation ------------------------
# Ranges are literal current line numbers to mutation_probe.py, so ANY pre-implementation
# number is stale by gate time (additive units: the lines don't exist; existing files: an
# insertion above the range shifts it). The resolution pass therefore covers every
# annotation, and it moves the digest forward — the gate compares against the LATEST
# Adversary-recorded digest, not the handoff one.
needle "$CLAUDE_SKILL" "claude red-first" "the prose-anchor form for absent line numbers" \
  'prose anchor'
needle "$CLAUDE_SKILL" "claude red-first" "the post-green Adversary-owned resolution pass" \
  'post-green, Adversary-owned resolution'
needle "$CLAUDE_SKILL" "claude red-first" "the every-annotation scope of the resolution pass" \
  "EVERY annotation's numeric range against the final implementation"
needle "$CLAUDE_SKILL" "claude red-first" "the new-digest rule for a resolution pass" \
  'to supersede the previous one'
needle "$CLAUDE_SKILL" "claude red-first" "the latest-digest comparison at the gate" \
  'latest Adversary-recorded digest'
needle "$CLAUDE_SKILL" "claude red-first" "the pre-resolution old-digest verification" \
  'verify it still equals the previous Adversary digest'
needle "$CLAUDE_SKILL" "claude red-first" "the annotation-lines-only resolution delta rule" \
  'only `# mutation-probe:` annotation lines'
needle "$CLAUDE_SKILL" "claude red-first" "the preserved-bytes mechanical delta check" \
  'copy the pre-resolution file'
needle "$CLAUDE_SKILL" "claude red-first" "the exit-1 misresolved-range correction path" \
  'misresolved range gets an annotation-only correction'

# --- 4. Claude carrier: gate mechanics + verdict protocol -------------------------------
# The probe MUST be run per-test, not per-file: mutation_probe.py accepts ANY test failure in
# the command it is given, so a file-level `--test` clears the probe on a SIBLING test's red
# while the annotated test stays green — a vacuous annotation passing the gate.
needle "$CLAUDE_SKILL" "claude red-first" "the probe invocation" \
  'just mutation-probe --file F --lines A-B --test'
needle "$CLAUDE_SKILL" "claude red-first" "the node-specific command the Adversary must report" \
  '**per test, the narrowest command that runs ONLY that test**'
needle "$CLAUDE_SKILL" "claude red-first" "the cannot-isolate-is-a-BLOCK rule" \
  'A test whose command cannot isolate it is itself a'
needle "$CLAUDE_SKILL" "claude red-first" "the no-file-level-probe rule" \
  "**Use that annotation's own node-specific command, never a file-level one.**"
needle "$CLAUDE_SKILL" "claude red-first" "why a file-level probe is vacuous" \
  'run clears the probe when a **sibling** test in the same file goes red'
needle "$CLAUDE_SKILL" "claude red-first" "the red-evidence-in-PR-body requirement" \
  'paste the failing output verbatim into the PR body'
needle "$CLAUDE_SKILL" "claude red-first" "the CUT-no-Breaker statement" \
  '**CUT: no Breaker role.**'
needle "$CLAUDE_SKILL" "claude red-first" "the BLOCK verdict line" \
  'RED-FIRST: BLOCK: <one-sentence reason>'
needle "$CLAUDE_SKILL" "claude red-first" "the fail-closed unparseable-verdict rule" \
  'RED-FIRST: BLOCK: unparseable verdict'

# --- 5. Claude carrier: Adversary precedes Implementer precedes the gate ----------------
C_ADV=$(lineno "$CLAUDE_SKILL" '## Phase 1 — Adversary')
C_IMP=$(lineno "$CLAUDE_SKILL" '## Phase 2 — Implementer')
C_GATE=$(lineno "$CLAUDE_SKILL" '## Completion gate')
if [ -n "$C_ADV" ] && [ -n "$C_IMP" ] && [ -n "$C_GATE" ] \
   && [ "$C_ADV" -lt "$C_IMP" ] && [ "$C_IMP" -lt "$C_GATE" ]; then
  ok "claude red-first orders Adversary($C_ADV) < Implementer($C_IMP) < gate($C_GATE)"
else
  bad "claude red-first ordering: adversary='$C_ADV' implementer='$C_IMP' gate='$C_GATE'"
fi

# --- 6. Codex carrier: the BRIDGE contract, not a second copy of the ritual --------------
# The first four needles are the predicates the pytest parity lane enforces for every
# non-native bridge, asserted here too so a regression is caught by this standalone hook test
# as well as by the pytest lane.
needle "$CODEX_SKILL" "codex-native red-first" "its skill name in frontmatter" 'name: red-first'
needle "$CODEX_SKILL" "codex-native red-first" "the bridge heading" \
  '# Canonical Claude Workflow Bridge'
needle "$CODEX_SKILL" "codex-native red-first" "the canonical source path" \
  'Read `.claude/skills/red-first/SKILL.md` completely'
needle "$CODEX_SKILL" "codex-native red-first" "the defer-to-canonical contract" \
  'full workflow and the source of truth'
needle "$CODEX_SKILL" "codex-native red-first" "the translations-only limit" \
  'Apply these runner translations only:'
needle "$CODEX_SKILL" "codex-native red-first" "the no-summarize pledge" \
  'does not summarize, trim, or replace it'

# --- 7. Codex carrier: the red-first-specific runner translations ------------------------
needle "$CODEX_SKILL" "codex-native red-first" "the Adversary session translation" \
  'means a fresh, separate `codex exec` session with a self-contained brief'
needle "$CODEX_SKILL" "codex-native red-first" "the not-the-adversarial-reviewer constraint" \
  'never the `harness-adversarial-reviewer` skill'
needle "$CODEX_SKILL" "codex-native red-first" "the separate-session Implementer translation" \
  'Implementer phase runs in its own separate session'
needle "$CODEX_SKILL" "codex-native red-first" "the probe invocation" \
  'just mutation-probe --file F --lines A-B --test'
needle "$CODEX_SKILL" "codex-native red-first" "the no-file-level-probe rule" \
  "Use the annotation's own node-specific command and never a file-level one"
needle "$CODEX_SKILL" "codex-native red-first" "the operator-request-only invocation rule" \
  'never chain this skill automatically from roadmap-continue or ship-pr'
needle "$CODEX_SKILL" "codex-native red-first" "the annotation format it routes to" \
  '`# mutation-probe: <file>:<lines>`'

# --- 8. Codex carrier: it must NOT re-implement the canonical body -----------------------
# A bridge that grows its own role/gate sections is a second contract to drift; the pytest
# parity lane only checks the pointer predicates, so the duplication check lives here.
absent "$CODEX_SKILL" "codex-native red-first" "a duplicated Adversary phase section" \
  '## Adversary phase'
absent "$CODEX_SKILL" "codex-native red-first" "a duplicated Implementer phase section" \
  '## Implementer phase'
absent "$CODEX_SKILL" "codex-native red-first" "a duplicated completion gate section" \
  '## Completion gate'
# ...and the CANONICAL carrier's own headings (a bridge could copy those verbatim instead;
# the three needles above only catch the bridge's former native-shape headings).
absent "$CODEX_SKILL" "codex-native red-first" "a copied canonical Adversary heading" \
  '## Phase 1 — Adversary'
absent "$CODEX_SKILL" "codex-native red-first" "a copied canonical Implementer heading" \
  '## Phase 2 — Implementer'

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

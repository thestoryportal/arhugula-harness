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

# The Codex merge-gate carrier launches its lenses through `codex exec`, not an `Agent`
# call, so the PreToolUse advisory never reaches that path and the Claude paragraph cannot
# be transplanted (laws:prompt is a Claude-plugin skill). Its TRANSLATION is therefore the
# only thing carrying the rule on that runner, and it is pinned here (codex r1 P2).
CODEX_MG="$REPO/.agents/skills/merge-gate/SKILL.md"
for needle in "canonical template" "is AUTHORING" "fresh Codex subagent" "Base case"; do
  grep -q "$needle" "$CODEX_MG" \
    && ok "Codex merge-gate carrier states: $needle" \
    || bad "Codex merge-gate carrier lost the authoring rule ($needle)"
done

# The carrier must name the templates the procedure ACTUALLY loads, and those files must
# exist -- naming "the briefs in this file" made every normal launch a departure requiring
# delegation, which is the opposite of what the rule intends (codex r2 P2).
for lens in lens1-concurrency lens2-spec-conformance lens3-test-witness; do
  [ -f "$REPO/.codex/notes/merge-gate-lenses/$lens.md" ] \
    && grep -q "$lens" "$CODEX_MG" \
    && ok "Codex carrier names its real template $lens.md" \
    || bad "Codex carrier does not name the existing template $lens.md"
done
grep -q "laws:prompt" "$CODEX_MG" \
  && ok "Codex carrier names the Claude-side rule it translates" \
  || bad "Codex carrier does not reference the rule it translates"

# The base case, without which the rule recurses forever (codex r1 P2).
printf '%s' "$REF" | grep -q 'base case' \
  && ok "rule names the delegation base case" || bad "rule has no bootstrap base case"

# WR-09: neither merge-gate carrier may hand the lens its binding values inline.
#
# Bound to the SHAPE, not to a spelling (codex r8 P2). The first version of this check
# blocklisted two phrases, so restoring the old launch tail under any other wording -- e.g.
# `these six values copied VERBATIM: head_sha=<...>` -- evaded it while the positive check
# below still passed. What actually distinguishes by-file from by-hand is whether a binding
# FIELD is assigned a value in the carrier at all: the by-file form names the fields (as
# prose or backticked identifiers) and points at a path, and never writes `field=`. This is
# the same spelling-bound-ban defect U-SR-02 carried forward as a named residual.
for rel in ".claude/skills/merge-gate/SKILL.md" ".agents/skills/merge-gate/SKILL.md"; do
  text=$(cat "$REPO/$rel")
  assigned=""
  for field in head_sha base_sha diff_digest reviewer_identity prompt_version config_hash; do
    printf '%s' "$text" | grep -Eq "$field[[:space:]]*=" && assigned="$assigned $field"
  done
  [ -z "$assigned" ] \
    && ok "$rel assigns no binding value inline" \
    || bad "$rel writes binding value(s) into the prompt:$assigned"
  printf '%s' "$text" | grep -q 'merge-gate-binding' \
    && ok "$rel still routes through the binding recipe" \
    || bad "$rel lost the binding recipe reference"
done

# The PROMPT the lens receives must carry no binding value at all -- not as an assignment
# (checked above) and not as a substituted placeholder either (codex r9 P2: the Codex launch
# tail said `head <sha>`, which the assignment check did not see, so the orchestrator still
# hand-copied the head into every lens prompt while the prose claimed it never did).
# Scoped to the fenced prompt-tail block, because the `--output-last-message` path OUTSIDE it
# legitimately carries a 40-char head that the permission guard's shape requires.
CODEX_TAIL=$(awk '/^```text$/{n++; if (n==1) {inb=1; next}} inb && /^```$/{exit} inb' "$CODEX_MG")
if [ -z "$CODEX_TAIL" ]; then
  bad "could not extract the Codex prompt tail block"
else
  ok "extracted the Codex prompt tail block"
  printf '%s' "$CODEX_TAIL" | grep -Eq '<[0-9]*-?(char-)?(head|sha)>|head[[:space:]]+<' \
    && bad "the Codex prompt tail still hands the lens a head value to transcribe" \
    || ok "the Codex prompt tail hands the lens no binding value"
fi

for rel in ".claude/skills/merge-gate/SKILL.md" ".agents/skills/merge-gate/SKILL.md"; do
  text=$(cat "$REPO/$rel")
  # ...and the positive half: it must actually tell the lens to READ the published path,
  # so deleting the by-file instruction cannot pass merely by assigning nothing.
  printf '%s' "$text" | grep -Eqi 'read (it|the values|the six)|reads? the values from it' \
    && ok "$rel instructs the lens to read the published file" \
    || bad "$rel no longer tells the lens to read the binding file"
done

# The Codex carrier tells operators to read this README and follow its launch snippet, so a
# README that contradicts the emit contract is a documented path to unrecordable verdicts
# (codex r10 P2). Both halves are pinned: the binding file must be published and named, and
# the verdict line must require its reason, because `_VERDICT_LINE` refuses a bare BLOCK.
LENS_README="$REPO/.codex/notes/merge-gate-lenses/README.md"
if [ -f "$LENS_README" ]; then
  ok "the Codex lens README exists"
  grep -q 'merge-gate-binding' "$LENS_README" \
    && ok "lens README publishes the binding before launching" \
    || bad "lens README launches reviewers without publishing a binding"
  grep -q 'VERDICT: BLOCK: <one-sentence reason>' "$LENS_README" \
    && ok "lens README requires the BLOCK reason the emitter demands" \
    || bad "lens README still permits a bare VERDICT: BLOCK that emit refuses"
else
  bad "the Codex lens README is missing"
fi

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

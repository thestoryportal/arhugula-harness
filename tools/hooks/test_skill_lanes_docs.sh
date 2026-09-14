#!/usr/bin/env bash
# Hermetic doc witness for U-HE-39 (spec-he-loop-lanes C-HE-01 / C-HE-14 / C-HE-21 / C-HE-34 /
# C-HE-35 and §8 AC#7). The four in-scope loop-skill carriers must: state the lane model at
# N ≥ 2 with no N=2 literal cap; carry the C-HE-14 rejected/blocked table byte-exact from the
# spec; cite live carriers for invariants #5/#14 and state #16 void; record the Part D
# non-goals and the K5–K8 dispositions; and name no numeric round cap.
#
# Needles name the specific obligation, never a word the sibling prose already carries: a bare
# `N ≥ 2` sat in two-lane's pilot-gate paragraph before this unit existed, so only the C-HE-01
# sentence itself can witness C-HE-01. The round-cap scan matches spelled numbers as well as
# digits — the cap this unit recast read "ten rounds", which the plan's digits-only pattern
# passed.
#
# Usage: test_skill_lanes_docs.sh [root]   (default: this checkout). The root argument lets the
# witness run against an older tree (e.g. `git archive origin/main`) to confirm it is red there.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$SCRIPT_DIR/../..}"
TL="$ROOT/.claude/skills/two-lane/SKILL.md"
RC="$ROOT/.claude/skills/roadmap-continue/SKILL.md"
MG="$ROOT/.claude/skills/merge-gate/SKILL.md"
SP="$ROOT/.claude/skills/ship-pr/SKILL.md"
SPEC="$ROOT/.harness/spec/Spec_HE_Loop_Lanes_v1.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$TL" "$RC" "$MG" "$SP" "$SPEC"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

skill() { basename "$(dirname "$1")"; }

# $1 = file, $2 = contract element, $3 = fixed-string needle (at least one line)
has() {
  if grep -qF -- "$3" "$1"; then
    ok "$(skill "$1") carries $2"
  else
    bad "$(skill "$1"): $2 missing (needle: $3)"
  fi
}

# $1 = file, $2 = what, $3 = exact line that must exist (a cite must name a live heading)
has_line() {
  if grep -qxF -- "$3" "$1"; then
    ok "$(skill "$1") has the live heading $2"
  else
    bad "$(skill "$1"): cited heading $2 is not a line in the file (want: $3)"
  fi
}

# --- 1. C-HE-01: the lane model at N ≥ 2, throughput priced, no N=2 literal cap -----------
for f in "$TL" "$RC"; do
  has "$f" "the C-HE-01 §1 lane-model sentence" \
    'N ≥ 2 lanes build concurrently in isolated worktrees'
  has "$f" "the C-HE-01 §4 throughput statement" \
    'well under N×; merges serialize; trailing lanes re-gate on head change'
  has "$f" "the prior-not-measurement qualifier" 'prior, not measurement'
  # grep exit 1 = no match; exit >= 2 = the scan did not run, which must never read as clean.
  two=$(grep -nw 'TWO' "$f"); r1=$?
  neq=$(grep -nE '(^|[^0-9A-Za-z])N ?= ?2([^0-9]|$)' "$f"); r2=$?
  if [ "$r1" -gt 1 ] || [ "$r2" -gt 1 ]; then
    bad "$(skill "$f"): N=2 scan could not run (grep exit $r1/$r2)"
  elif [ -n "$two$neq" ]; then
    bad "$(skill "$f") states an N=2 literal cap: $(printf '%s %s' "$two" "$neq" | cut -c1-160)"
  else
    ok "$(skill "$f") states no N=2 literal cap"
  fi
done

# --- 2. C-HE-14: the rejected/blocked table, byte-exact from the spec --------------------
has_line "$TL" "for C-HE-14" '## Rejected and blocked mechanisms (C-HE-14)'
rows=$(awk '/^## C-HE-14 /{f=1; next} f && /^## /{exit} f && /^\| /' "$SPEC" | tail -n +2)
n=$(printf '%s\n' "$rows" | grep -c '^| ')
# Boundedness marker: a moved anchor must fail loud, not shrink the slice to a vacuous pass.
if [ "$n" -eq 11 ]; then
  ok "spec C-HE-14 slice is bounded at 11 rows"
else
  bad "spec C-HE-14 slice yielded $n rows, want 11 (anchor moved?)"
fi
missing=0
while IFS= read -r row; do
  [ -n "$row" ] || continue
  if ! grep -qxF -- "$row" "$TL"; then
    bad "two-lane lacks a C-HE-14 row byte-exact: ${row:0:70}"
    missing=$((missing+1))
  fi
done <<< "$rows"
[ "$missing" -eq 0 ] && ok "two-lane carries every C-HE-14 row byte-exact"

# --- 3. C-HE-21: invariants by live carriage, #16 void, checkpoint not cap ---------------
has "$MG" "the live-carriage rule" 'Invariants bind by live carriage (C-HE-21 §2)'
has "$MG" "the #16-void statement" '**invariant #16 is void**'
has "$MG" "#14's carrier" '#14 is C-HE-19'
has "$MG" "the no-model-judge-gate refusal" 'No eval-harness / model-judge as a governance gate'
has_line "$MG" "cited for #5" '## Parsing — fail closed'
has_line "$SP" "cited for #5" \
  '## Pre-merge gate — CI green + decorrelated 3-lens review (before the merge door)'
has "$SP" "the live #14 carrier (CANCELLED is INCOMPLETE)" 'INCOMPLETE, never green (C-HE-19)'
for f in "$MG" "$SP"; do
  has "$f" "the checkpoint-not-cap statement" 'recorded-decision checkpoint'
done

# --- 4. C-HE-34 non-goals + C-HE-35 K5–K8 dispositions ----------------------------------
has_line "$SP" "for C-HE-34" '## Non-goals (C-HE-34)'
has "$SP" "non-goal: no round cap" 'No auto-stopping round cap'
has "$SP" "non-goal: no best-of-N" 'No best-of-N'
has "$SP" "non-goal: no fast mode" 'No fast mode for throughput'
has "$SP" "non-goal: no agent framework" 'No agent framework'
has "$SP" "non-goal: no collapsing review layers" 'No collapsing of review layers'
for k in K5 K6 K7 K8; do
  has "$MG" "the $k disposition" "- **$k —"
done
has "$MG" "the K6 no-self-suppression rule" \
  'a reviewer never acquires authority to suppress its own finding'

# --- 5. §8 AC#7: no numeric round cap in any loop skill ----------------------------------
NUM='([0-9]+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|twenty)'
CAP='(^|[^a-z])(max|cap|capped|ceiling)'
hits=$(grep -EinH -- "${CAP}[^.]{0,20}rounds?[^.]{0,10}[^a-z]${NUM}([^a-z]|$)|${CAP}[^.]{0,40}[^a-z]${NUM} (review |fix )?rounds?([^a-z]|$)" \
  "$MG" "$SP" "$RC" "$TL"); rc=$?
if [ "$rc" -gt 1 ]; then
  bad "AC#7: round-cap scan could not run (grep exit $rc)"
elif [ -z "$hits" ]; then
  ok "AC#7: no numeric round cap in the loop skills"
else
  bad "AC#7: numeric round cap found:"
  printf '%s\n' "$hits" | cut -c1-200 | sed 's/^/      /'
fi

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

#!/usr/bin/env bash
# Hermetic test for the U-WT-01 grounding-pass clause. Asserts the clause is PRESENT in
# ship-pr/SKILL.md, is ORDERED between the Green and Out-of-family-review pre-flight
# bullets (so it is read before codex round 1), is mirrored at roadmap-continue step 4,
# and names all three mechanical checks (file:line cites / count recomputation / #NNN).
# Doc-text assertions run against the REAL repo SKILL.md files resolved from SCRIPT_DIR
# (no scratch repo: the artifact under test IS the checked-in skill text).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$SCRIPT_DIR/../../.claude/skills"
SHIP="$SKILLS/ship-pr/SKILL.md"
CONT="$SKILLS/roadmap-continue/SKILL.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$SHIP" "$CONT"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

# line number of the first line matching a fixed string, empty if absent
lineno() { grep -nF -- "$2" "$1" | head -1 | cut -d: -f1; }

# --- 1. presence: the distinctive unit-tagged bullet exists ---
if grep -qF -- 'Grounding pass (U-WT-01)' "$SHIP"; then
  ok "ship-pr carries the 'Grounding pass (U-WT-01)' bullet"
else
  bad "ship-pr missing the 'Grounding pass (U-WT-01)' bullet"
fi

# --- 2. ordering: Green < grounding < Out-of-family review ---
L_GREEN=$(lineno "$SHIP" '- **Green.**')
L_GROUND=$(lineno "$SHIP" 'Grounding pass (U-WT-01)')
L_CODEX=$(lineno "$SHIP" '- **Out-of-family review.**')
if [ -n "$L_GREEN" ] && [ -n "$L_GROUND" ] && [ -n "$L_CODEX" ] \
   && [ "$L_GROUND" -gt "$L_GREEN" ] && [ "$L_GROUND" -lt "$L_CODEX" ]; then
  ok "ordering Green($L_GREEN) < grounding($L_GROUND) < out-of-family($L_CODEX)"
else
  bad "bad ordering: Green='$L_GREEN' grounding='$L_GROUND' out-of-family='$L_CODEX'"
fi

# --- 3. roadmap-continue step 4 mirrors the clause, BEFORE its codex-review clause ---
# Scoped to the step-4 block (from "4. **" to the next "5. **") so the phrase drifting
# elsewhere in the file cannot keep this green (codex round-2 mutation finding).
STEP4=$(awk '/^4\. \*\*/{f=1} /^5\. \*\*/{f=0} f' "$CONT")
S4_GROUND=$(printf '%s\n' "$STEP4" | grep -in -- 'grounding pass' | head -1 | cut -d: -f1)
S4_CODEX=$(printf '%s\n' "$STEP4" | grep -n -- 'codex-review' | head -1 | cut -d: -f1)
if [ -n "$S4_GROUND" ] && [ -n "$S4_CODEX" ] && [ "$S4_GROUND" -lt "$S4_CODEX" ]; then
  ok "roadmap-continue step 4 names the grounding pass before codex-review"
else
  bad "step-4 scoping: grounding='$S4_GROUND' codex-review='$S4_CODEX' (grounding must exist and precede)"
fi

# --- 4. all three mechanical checks are named in the ship-pr bullet ---
CLAUSE=$(awk -v s="$L_GROUND" -v e="$L_CODEX" 'NR>=s && NR<e' "$SHIP")
check_names() { # $1 = needle, $2 = label
  printf '%s' "$CLAUSE" | grep -qF -- "$1" \
    && ok "clause names $2" || bad "clause does not name $2 ('$1')"
}
check_names 'file:line' 'the file:line cite re-read'
check_names 'recompute' 'count/arithmetic recomputation'
check_names '#NNN'      'the #NNN PR-reference check'

# --- 5. Codex-native mirrors (.agents tree encodes its rituals independently) ---
ASKILLS="$SCRIPT_DIR/../../.agents/skills"
ASHIP="$ASKILLS/ship-pr/SKILL.md"
ACONT="$ASKILLS/roadmap-continue/SKILL.md"

L_AGROUND=$(lineno "$ASHIP" 'Grounding pass (U-WT-01)')
L_AREVIEW=$(lineno "$ASHIP" '## Authorship-dependent out-of-family review')
if [ -n "$L_AGROUND" ] && [ -n "$L_AREVIEW" ] && [ "$L_AGROUND" -lt "$L_AREVIEW" ]; then
  ok "codex-native ship-pr mirrors the pass before the out-of-family review section"
else
  bad "codex-native ship-pr mirror: grounding='$L_AGROUND' review-section='$L_AREVIEW'"
fi

# scoped to step 6's block (from "6. " to "7. "), pass must precede the reviewer clause
ASTEP6=$(awk '/^6\. /{f=1} /^7\. /{f=0} f' "$ACONT")
A6_GROUND=$(printf '%s\n' "$ASTEP6" | grep -n -- 'Grounding pass (U-WT-01)' | head -1 | cut -d: -f1)
A6_REVIEW=$(printf '%s\n' "$ASTEP6" | grep -n -- 'gemini-review' | head -1 | cut -d: -f1)
if [ -n "$A6_GROUND" ] && [ -n "$A6_REVIEW" ] && [ "$A6_GROUND" -lt "$A6_REVIEW" ]; then
  ok "codex-native roadmap-continue step 6 runs the pass before the review"
else
  bad "codex-native step-6 scoping: grounding='$A6_GROUND' review='$A6_REVIEW'"
fi

# --- 6. both continue mirrors carry ALL FIVE checks (round-5: stale-evidence gap) ---
# The two later checks — gates-at-current-HEAD and stated-in-PR-body — must live in the
# continue skills too, since both run review round 1 BEFORE the ship-pr handoff.
five_checks() { # $1 = block text, $2 = label
  local blk="$1" lbl="$2" miss=""
  printf '%s' "$blk" | grep -qF -- 'file:line'  || miss="$miss file:line"
  printf '%s' "$blk" | grep -qiF -- 'recompute' || miss="$miss recompute"
  printf '%s' "$blk" | grep -qF -- '#NNN'       || miss="$miss #NNN"
  printf '%s' "$blk" | grep -qF -- 'HEAD'       || miss="$miss current-HEAD"
  printf '%s' "$blk" | grep -qiF -- 'PR body'   || miss="$miss PR-body"
  if [ -z "$miss" ]; then ok "$lbl carries all five checks"; else bad "$lbl missing:$miss"; fi
}
five_checks "$STEP4"  "claude roadmap-continue step 4"
five_checks "$ASTEP6" "codex-native roadmap-continue step 6"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

#!/usr/bin/env bash
# Hermetic test for the U-WT-01 grounding-pass clause. Asserts the clause is PRESENT and
# ORDERED before review round 1 in all four carriers — Claude ship-pr / roadmap-continue
# and their Codex-native mirrors (.agents tree, which encodes its rituals independently)
# — and that EVERY carrier block names all five checks: file:line cite re-read, count
# recomputation, #NNN verification, gate freshness (HEAD for the Claude flow's committed
# diff; staged/worktree for the Codex flow's pre-commit diff), and stated-in-PR-body.
# Doc-text assertions run against the REAL repo SKILL.md files resolved from SCRIPT_DIR
# (no scratch repo: the artifact under test IS the checked-in skill text).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$SCRIPT_DIR/../../.claude/skills"
ASKILLS="$SCRIPT_DIR/../../.agents/skills"
SHIP="$SKILLS/ship-pr/SKILL.md"
CONT="$SKILLS/roadmap-continue/SKILL.md"
ASHIP="$ASKILLS/ship-pr/SKILL.md"
ACONT="$ASKILLS/roadmap-continue/SKILL.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$SHIP" "$CONT" "$ASHIP" "$ACONT"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

# line number of the first line matching a fixed string, empty if absent
lineno() { grep -nF -- "$2" "$1" | head -1 | cut -d: -f1; }

# All five U-WT-01 checks present in a carrier block. Needles are per-carrier because
# generic tokens are satisfied by sibling prose (merge-gate lens-3 + codex mutation runs):
#   $3 cite-and-source phrase — check (a) COUPLED to its flow source (HEAD for the Claude
#      committed-diff flow; staged/worktree content for the Codex pre-commit flow). A bare
#      'file:line' + separate flow token lets "re-read from memory" mutants pass because
#      the flow word survives in the check-(d) sentence. Matched whitespace-normalized
#      (the phrases wrap across hard-wrapped lines).
#   literal '*current*' — the check-(d) gate-freshness discriminator; occurs exactly once
#      per block, only inside check (d), in all four carriers.
#   $4 stated-in-PR-body needle — check (e)'s distinctive phrase for this carrier (the
#      generic 'PR body' is duplicated by check (a)'s "diff and PR body" in ship-pr).
five_checks() { # $1 = block text, $2 = label, $3 = cite-and-source phrase, $4 = check-(e) needle
  local blk="$1" lbl="$2" cite="$3" ebody="$4" miss=""
  local norm; norm=$(printf '%s' "$blk" | tr '\n' ' ' | tr -s ' ')
  printf '%s' "$norm" | grep -qF -- "$cite"     || miss="$miss cite-and-source($cite)"
  printf '%s' "$blk" | grep -qiF -- 'recompute' || miss="$miss recompute"
  printf '%s' "$blk" | grep -qF -- '#NNN'       || miss="$miss #NNN"
  printf '%s' "$blk" | grep -qF -- '*current*'  || miss="$miss gate-freshness(*current*)"
  printf '%s' "$blk" | grep -qF -- "$ebody"     || miss="$miss stated-in-PR-body($ebody)"
  if [ -z "$miss" ]; then ok "$lbl carries all five checks"; else bad "$lbl missing:$miss"; fi
}

# --- 1. Claude ship-pr: presence + ordering Green < grounding < Out-of-family ---
L_GREEN=$(lineno "$SHIP" '- **Green.**')
L_GROUND=$(lineno "$SHIP" 'Grounding pass (U-WT-01)')
L_CODEX=$(lineno "$SHIP" '- **Out-of-family review.**')
if [ -n "$L_GREEN" ] && [ -n "$L_GROUND" ] && [ -n "$L_CODEX" ] \
   && [ "$L_GROUND" -gt "$L_GREEN" ] && [ "$L_GROUND" -lt "$L_CODEX" ]; then
  ok "claude ship-pr ordering Green($L_GREEN) < grounding($L_GROUND) < out-of-family($L_CODEX)"
else
  bad "claude ship-pr ordering: Green='$L_GREEN' grounding='$L_GROUND' out-of-family='$L_CODEX'"
fi

# --- 2. Claude ship-pr: full five-check contract in the clause block ---
# Guard the anchors explicitly: a :-0 default would fail OPEN with an over-wide block
# (lines 1..L_CODEX) that sibling preamble text could satisfy (lens-3 finding).
if [ -n "$L_GROUND" ] && [ -n "$L_CODEX" ]; then
  CLAUSE=$(awk -v s="$L_GROUND" -v e="$L_CODEX" 'NR>=s && NR<e' "$SHIP")
else
  CLAUSE=""
fi
five_checks "$CLAUSE" "claude ship-pr grounding bullet" 're-read every `file:line` cite in the diff and PR body at HEAD' 'state in the PR body'

# --- 3. Claude roadmap-continue: scoped to step 4, pass precedes codex-review ---
STEP4=$(awk '/^4\. \*\*/{f=1} /^5\. \*\*/{f=0} f' "$CONT")
S4_GROUND=$(printf '%s\n' "$STEP4" | grep -in -- 'grounding pass' | head -1 | cut -d: -f1)
S4_CODEX=$(printf '%s\n' "$STEP4" | grep -n -- 'codex-review' | head -1 | cut -d: -f1)
if [ -n "$S4_GROUND" ] && [ -n "$S4_CODEX" ] && [ "$S4_GROUND" -lt "$S4_CODEX" ]; then
  ok "claude roadmap-continue step 4 names the grounding pass before codex-review"
else
  bad "claude step-4 scoping: grounding='$S4_GROUND' codex-review='$S4_CODEX'"
fi

# --- 4. Claude roadmap-continue: full five-check contract in step 4 ---
five_checks "$STEP4" "claude roadmap-continue step 4" 're-read every file:line cite at the now-current HEAD' 'state the pass in the PR body'

# --- 5. Codex ship-pr: pass section precedes the out-of-family review section ---
L_AGROUND=$(lineno "$ASHIP" 'Grounding pass (U-WT-01)')
L_AREVIEW=$(lineno "$ASHIP" '## Authorship-dependent out-of-family review')
if [ -n "$L_AGROUND" ] && [ -n "$L_AREVIEW" ] && [ "$L_AGROUND" -lt "$L_AREVIEW" ]; then
  ok "codex-native ship-pr mirrors the pass before the out-of-family review section"
else
  bad "codex-native ship-pr mirror: grounding='$L_AGROUND' review-section='$L_AREVIEW'"
fi

# --- 6. Codex ship-pr: full five-check contract in the grounding section ---
ASHIP_BLK=$(awk '/^## Grounding pass \(U-WT-01\)/{f=1;next} /^## /{f=0} f' "$ASHIP")
five_checks "$ASHIP_BLK" "codex-native ship-pr grounding section" 'cite in the diff and PR body against the exact content under review (the staged/worktree diff' 'state in the PR body'

# --- 7. Codex roadmap-continue: scoped to step 6, pass precedes the reviewer clause ---
ASTEP6=$(awk '/^6\. /{f=1} /^7\. /{f=0} f' "$ACONT")
A6_GROUND=$(printf '%s\n' "$ASTEP6" | grep -n -- 'Grounding pass (U-WT-01)' | head -1 | cut -d: -f1)
A6_REVIEW=$(printf '%s\n' "$ASTEP6" | grep -n -- 'gemini-review' | head -1 | cut -d: -f1)
if [ -n "$A6_GROUND" ] && [ -n "$A6_REVIEW" ] && [ "$A6_GROUND" -lt "$A6_REVIEW" ]; then
  ok "codex-native roadmap-continue step 6 runs the pass before the review"
else
  bad "codex-native step-6 scoping: grounding='$A6_GROUND' review='$A6_REVIEW'"
fi

# --- 8. Codex roadmap-continue: full five-check contract in step 6 ---
five_checks "$ASTEP6" "codex-native roadmap-continue step 6" 'cite against the staged/worktree content under review' 'PR body at ship-pr'

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

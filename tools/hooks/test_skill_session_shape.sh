#!/usr/bin/env bash
# Wiring witness for the U-SR-07 (WR-14) session-shape habit lines. The three lines
# land at their decision moments, not in an appendix block: read-before-grep at the
# roadmap-continue grounding step ([B] F5/d3: 33 `sed -n` + 101 grep-shaped calls, one
# API call each); the cache-warmth handoff at the background-wait instruction ([B] F4:
# one cold re-warm ≈0.7M IET); the facts-brief handoff at BOTH close-out moments —
# roadmap-continue step 6 and the ship-pr reflect block ([B] F10: S3 authored at 540k
# context cost 0.93M vs ≈0.3M fresh). Doc-text assertions run against the REAL repo
# SKILL.md files resolved from SCRIPT_DIR (the artifact under test IS the checked-in
# skill text), matched whitespace-normalized as composed phrases sibling prose cannot
# satisfy token-by-token (the test_skill_codex_check_background.sh precedent).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$SCRIPT_DIR/../../.claude/skills"
CONT="$SKILLS/roadmap-continue/SKILL.md"
SHIP="$SKILLS/ship-pr/SKILL.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$CONT" "$SHIP"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

# $1=file $2=label $3=rule-phrase $4=why-cite $5=trap-phrase — all three must sit in
# the same carrier: the composed rule phrase, its measured [B] cost, and the quoted
# rationalization it disarms. A carrier holding the rule without its why (or without
# the trap it was written to defeat) is the regression shape.
line() {
  local norm; norm=$(tr '\n' ' ' < "$1" | tr -s ' ')
  local miss=""
  printf '%s' "$norm" | grep -qF -- "$3" || miss="$miss rule-phrase"
  printf '%s' "$norm" | grep -qF -- "$4" || miss="$miss why($4)"
  printf '%s' "$norm" | grep -qF -- "$5" || miss="$miss trap-phrase"
  if [ -z "$miss" ]; then ok "$2"; else bad "$2 missing:$miss"; fi
}

line "$CONT" "roadmap-continue step 3 carries read-before-grep" \
  'Read-before-grep (U-SR-07/WR-14): for a file you will read anyway, Read it once' \
  '[B] F5/d3' \
  '"One more targeted grep is cheaper than reading it" is the trap'

line "$CONT" "roadmap-continue step 4 carries the cache-warmth handoff" \
  'Cache-warmth handoff (U-SR-07/WR-14): at >400k context, before ANY background wait expected to outlast the prompt-cache TTL' \
  '[B] F4' \
  "\"the wait costs nothing, I'm just sleeping\" is the trap"

line "$CONT" "roadmap-continue step 6 carries the facts-brief handoff" \
  'Facts-brief handoff (U-SR-07/WR-14): if the NEXT item is a heavy audit or document' \
  '[B] F10' \
  '"I already have all the context loaded" is exactly the trap'

line "$SHIP" "ship-pr reflect block carries the facts-brief handoff" \
  'Facts-brief handoff for a heavy next item (U-SR-07/WR-14).' \
  '[B] F10' \
  '"I already have all the context loaded" is the trap'

# Coupling controls — the rule must live in the SAME carrier as the moment it governs.
if grep -qF 'run_in_background' "$CONT" && grep -qF 'Cache-warmth' "$CONT"; then
  ok "roadmap-continue couples the background launch with the cache-warmth rule"
else
  bad "roadmap-continue decouples the background launch from the cache-warmth rule"
fi
if grep -qF '/context-save' "$SHIP" && grep -qF 'Facts-brief handoff' "$SHIP"; then
  ok "ship-pr couples /context-save with the facts-brief rule"
else
  bad "ship-pr decouples /context-save from the facts-brief rule"
fi
if grep -qF 'overlay-query' "$CONT" && grep -qF 'Read-before-grep' "$CONT"; then
  ok "roadmap-continue couples grounding with the read-before-grep rule"
else
  bad "roadmap-continue decouples grounding from the read-before-grep rule"
fi

# The measured baselines must appear with their figures intact — a paraphrase that
# drops the number drops the evidence ([B] is the recorded U-HE-35 baseline; assert
# the shape against these numbers, never recall).
norm_cont=$(tr '\n' ' ' < "$CONT" | tr -s ' ')
printf '%s' "$norm_cont" | grep -qF -- '134 of them that way (33 `sed -n` + 101 grep-shaped' \
  && ok "read-before-grep carries the 33+101=134 baseline" \
  || bad "read-before-grep baseline figures missing or drifted"
printf '%s' "$norm_cont" | grep -qF -- '≈0.7M IET' \
  && ok "cache-warmth carries the ≈0.7M re-warm cost" \
  || bad "cache-warmth re-warm cost missing"
printf '%s' "$norm_cont" | grep -qF -- '0.93M IET against ≈0.3M fresh' \
  && ok "facts-brief carries the 0.93M-vs-0.3M contrast (roadmap-continue)" \
  || bad "facts-brief cost contrast missing (roadmap-continue)"
norm_ship=$(tr '\n' ' ' < "$SHIP" | tr -s ' ')
printf '%s' "$norm_ship" | grep -qF -- '0.93M IET against ≈0.3M fresh' \
  && ok "facts-brief carries the 0.93M-vs-0.3M contrast (ship-pr)" \
  || bad "facts-brief cost contrast missing (ship-pr)"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

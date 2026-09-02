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
# satisfy token-by-token (the test_skill_codex_check_background.sh precedent) — and
# SECTION-SCOPED: every needle greps only the numbered step / section that is the
# line's carrier, so a paragraph relocated to an appendix reds instead of staying
# green on a whole-file match (u-sr-07 codex r1 P2).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$SCRIPT_DIR/../../.claude/skills"
CONT="$SKILLS/roadmap-continue/SKILL.md"
SHIP="$SKILLS/ship-pr/SKILL.md"
AGENTS_SKILLS="$SCRIPT_DIR/../../.agents/skills"
ACONT="$AGENTS_SKILLS/roadmap-continue/SKILL.md"
ASHIP="$AGENTS_SKILLS/ship-pr/SKILL.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$CONT" "$SHIP" "$ACONT" "$ASHIP"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

# section <file> <start-regex> <end-regex>: the carrier slice, whitespace-normalized.
# The start line is included; extraction stops BEFORE the first later line matching
# the end regex. An empty result means the anchor itself moved — every assertion on
# the slice then fails loud rather than passing on vacuous emptiness.
section() {
  awk -v s="$2" -v e="$3" '
    found && $0 ~ e { exit }
    $0 ~ s { found=1 }
    found { print }
  ' "$1" | tr '\n' ' ' | tr -s ' '
}

# Anchor regexes use character classes ([.] [*]) instead of backslash escapes:
# awk -v reprocesses backslashes in the pattern string, so `\*\*` reaches the regex
# engine as the invalid `**` and the section silently extracts empty on BSD awk.
cont_step3=$(section "$CONT" '^3[.] [*][*]Ground first' '^4[.] ')
cont_step4=$(section "$CONT" '^4[.] [*][*]Implement with tests' '^5[.] ')
cont_step6=$(section "$CONT" '^6[.] [*][*]Ship' '^## ')
ship_reflect=$(section "$SHIP" '^## Reflect' '^## Arc exit report')
# Codex-native mirrors (.agents tree) are carriers too — their own workflow text has
# the same three decision moments, and all three habits are venue-neutral (no phantom
# instrument; u-sr-07 codex r2 P2). The "Before the next arc" slice runs to EOF (no
# later heading), which is that section's real extent.
acont_ground=$(section "$ACONT" '^## Grounding' '^## Execute one arc')
acont_exec=$(section "$ACONT" '^## Execute one arc' '^## Genuine gates')
acont_next=$(section "$ACONT" '^## Before the next arc' '^## NEVER')
aship_reflect=$(section "$ASHIP" '^## Reflect and checkpoint' '^## Arc exit report')

for pair in cont_step3 cont_step4 cont_step6 ship_reflect acont_ground acont_exec acont_next aship_reflect; do
  eval "v=\${$pair}"
  [ -n "$v" ] && ok "section anchor resolves: $pair" || bad "section anchor EMPTY: $pair"
done

# $1=section-text $2=label $3=rule-phrase $4=why-cite $5=trap-phrase — all three must
# sit inside the SAME carrier section: the composed rule phrase, its measured [B]
# cost, and the quoted rationalization it disarms. A section holding the rule without
# its why (or without the trap it was written to defeat) is the regression shape.
line() {
  local miss=""
  printf '%s' "$1" | grep -qF -- "$3" || miss="$miss rule-phrase"
  printf '%s' "$1" | grep -qF -- "$4" || miss="$miss why($4)"
  printf '%s' "$1" | grep -qF -- "$5" || miss="$miss trap-phrase"
  if [ -z "$miss" ]; then ok "$2"; else bad "$2 missing:$miss"; fi
}

line "$cont_step3" "roadmap-continue step 3 carries read-before-grep" \
  'Read-before-grep (U-SR-07/WR-14): for a file you will read anyway, Read it once' \
  '[B] F5/d3' \
  '"One more targeted grep is cheaper than reading it" is the trap'

line "$cont_step4" "roadmap-continue step 4 carries the cache-warmth handoff" \
  'Cache-warmth handoff (U-SR-07/WR-14): at >400k context, before ANY background wait expected to outlast the prompt-cache TTL' \
  '[B] F4' \
  "\"the wait costs nothing, I'm just sleeping\" is the trap"

line "$cont_step6" "roadmap-continue step 6 carries the facts-brief handoff" \
  'Facts-brief handoff (U-SR-07/WR-14): if the NEXT item is a heavy audit or document' \
  '[B] F10' \
  '"I already have all the context loaded" is exactly the trap'

line "$ship_reflect" "ship-pr reflect block carries the facts-brief handoff" \
  'Facts-brief handoff for a heavy next item (U-SR-07/WR-14).' \
  '[B] F10' \
  '"I already have all the context loaded" is the trap'

line "$acont_ground" "codex roadmap-continue grounding carries read-before-grep" \
  'Read-before-grep (U-SR-07/WR-14): for a file you will read anyway, read it once' \
  '[B] F5/d3' \
  '"one more targeted grep is cheaper" stops being true'

line "$acont_exec" "codex roadmap-continue execute carries the cache-warmth handoff" \
  'Cache-warmth handoff (U-SR-07/WR-14): deep in a long session, before any background wait expected to outlast the prompt-cache TTL' \
  '[B] F4' \
  '"the wait costs nothing" bills the next call'

line "$acont_next" "codex roadmap-continue before-next-arc carries the facts-brief handoff" \
  'Facts-brief handoff (U-SR-07/WR-14): if the next item is a heavy audit or document' \
  '[B] F10' \
  '"I already have the context loaded" is the trap'

line "$aship_reflect" "codex ship-pr reflect carries the facts-brief handoff" \
  'Facts-brief handoff for a heavy next item (U-SR-07/WR-14): if the next action is a heavy audit or document' \
  '[B] F10' \
  '"I already have the context loaded" is the trap'

# Coupling controls — the rule must live in the SAME SECTION as the moment it governs
# (same-file co-occurrence proved nothing when either half could drift to an appendix).
printf '%s' "$cont_step4" | grep -qF 'run_in_background' && printf '%s' "$cont_step4" | grep -qF 'Cache-warmth' \
  && ok "step 4 couples the background launch with the cache-warmth rule" \
  || bad "step 4 decouples the background launch from the cache-warmth rule"
printf '%s' "$ship_reflect" | grep -qF '/context-save' && printf '%s' "$ship_reflect" | grep -qF 'Facts-brief handoff' \
  && ok "ship-pr reflect couples /context-save with the facts-brief rule" \
  || bad "ship-pr reflect decouples /context-save from the facts-brief rule"
printf '%s' "$cont_step3" | grep -qF 'overlay-query' && printf '%s' "$cont_step3" | grep -qF 'Read-before-grep' \
  && ok "step 3 couples grounding with the read-before-grep rule" \
  || bad "step 3 decouples grounding from the read-before-grep rule"

# The measured baselines must appear with their figures intact, inside their own
# carrier section — a paraphrase that drops the number drops the evidence ([B] is the
# recorded U-HE-35 baseline; assert the shape against these numbers, never recall).
printf '%s' "$cont_step3" | grep -qF -- '134 of them that way (33 `sed -n` + 101 grep-shaped' \
  && ok "read-before-grep carries the 33+101=134 baseline" \
  || bad "read-before-grep baseline figures missing or drifted"
printf '%s' "$cont_step4" | grep -qF -- '≈0.7M IET' \
  && ok "cache-warmth carries the ≈0.7M re-warm cost" \
  || bad "cache-warmth re-warm cost missing"
printf '%s' "$cont_step6" | grep -qF -- '0.93M IET against ≈0.3M fresh' \
  && ok "facts-brief carries the 0.93M-vs-0.3M contrast (roadmap-continue)" \
  || bad "facts-brief cost contrast missing (roadmap-continue)"
printf '%s' "$ship_reflect" | grep -qF -- '0.93M IET against ≈0.3M fresh' \
  && ok "facts-brief carries the 0.93M-vs-0.3M contrast (ship-pr)" \
  || bad "facts-brief cost contrast missing (ship-pr)"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

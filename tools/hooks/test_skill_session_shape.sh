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
HEAL="$SKILLS/self-heal/SKILL.md"
LANE="$SKILLS/two-lane/SKILL.md"
AGENTS_SKILLS="$SCRIPT_DIR/../../.agents/skills"
ACONT="$AGENTS_SKILLS/roadmap-continue/SKILL.md"
ASHIP="$AGENTS_SKILLS/ship-pr/SKILL.md"
ALOOP="$AGENTS_SKILLS/codex-autonomous-loop/SKILL.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$CONT" "$SHIP" "$HEAL" "$LANE" "$ACONT" "$ASHIP" "$ALOOP"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

# section <file> <start-regex> <end-regex>: the carrier slice, whitespace-normalized.
# The start line is included; extraction stops BEFORE the first later line matching
# the end regex. An empty result means the START anchor moved — every assertion on
# the slice then fails loud rather than passing on vacuous emptiness. The END anchor's
# failure mode is asymmetric (merge-gate witness lens, u-sr-07 gate r1): a miss does
# not empty the slice, it silently widens it to EOF — so the extractor appends a
# @@BOUNDED@@ marker ONLY when it exited via a real END match, and the boundedness
# loop below requires the marker on every slice whose section a later heading follows
# at HEAD. acont_next's end anchor is the generic '^## ' (u-sr-07 codex r9 — an
# impossible sentinel let a relocated paragraph hide in a later appendix): it stops
# at ANY next heading and legally runs to EOF only while no heading follows.
section() {
  awk -v s="$2" -v e="$3" '
    found && $0 ~ e { bounded=1; exit }
    $0 ~ s { found=1 }
    found { print }
    END { if (bounded) print "@@BOUNDED@@" }
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
# instrument; u-sr-07 codex r2 P2). The "Before the next arc" slice ends at the next
# heading if one ever appears (today none does, so it runs to EOF — its real extent);
# a paragraph relocated into a later appendix section leaves the slice, and reds.
acont_ground=$(section "$ACONT" '^## Grounding' '^## Execute one arc')
acont_exec=$(section "$ACONT" '^## Execute one arc' '^## Genuine gates')
acont_next=$(section "$ACONT" '^## Before the next arc' '^## ')
aship_reflect=$(section "$ASHIP" '^## Reflect and checkpoint' '^## Arc exit report')
# WR-14(b) carriers beyond roadmap-continue (u-sr-07 codex r5): every independently
# invocable skill that instructs a background codex-check launch is a background-wait
# moment and owes the cache-warmth rule — ship-pr's pre-flight (both runners),
# self-heal step 2, and the two-lane build half. The Codex self-heal/two-lane mirrors
# instruct no codex-check, so they carry no wait moment and owe nothing. Slices are
# ITEM-scoped, not section-scoped (u-sr-07 codex r6): the rule must sit in the same
# numbered step / bullet as the launch it governs — a within-section relocation to a
# later step reds.
ship_green=$(section "$SHIP" '^- [*][*]Green' '^- [*][*]Grounding pass')
aship_item3=$(section "$ASHIP" '^3[.] Run the narrow witness' '^4[.] ')
heal_step2=$(section "$HEAL" '^2[.] [*][*]Run the suite' '^3[.] ')
lane_setup=$(section "$LANE" '^## Lane setup' '^## The merge lane')
acont_item5=$(section "$ACONT" '^5[.] Run narrow verification' '^6[.] ')
# codex-autonomous-loop (u-sr-07 codex r7): a third independently invocable loop
# controller — codex-check at gate 7, CI waits at 13/16/18, checkpoint at gate 20,
# next-arc init — that routes through neither covered skill. Its own gates carry the
# three habits, item-scoped like the rest.
aloop_plan=$(section "$ALOOP" '^3[.] .plan.: record owned scope' '^4[.] ')
aloop_gate7=$(section "$ALOOP" '^7[.] .local_gate' '^8[.] ')
aloop_reflect=$(section "$ALOOP" '^20[.] Reflect' '^21[.] ')

for pair in cont_step3 cont_step4 cont_step6 ship_reflect acont_ground acont_exec acont_next aship_reflect ship_green aship_item3 heal_step2 lane_setup acont_item5 aloop_plan aloop_gate7 aloop_reflect; do
  eval "v=\${$pair}"
  [ -n "$v" ] && ok "section anchor resolves: $pair" || bad "section anchor EMPTY: $pair"
done

# Boundedness (u-sr-07 merge-gate witness lens): every slice must have terminated at a
# REAL end-anchor match — a slice missing @@BOUNDED@@ ran to EOF because its END anchor
# no longer matches (renamed heading, renumbered step), silently absorbing sibling
# sections. acont_next is exempt: its '^## ' anchor stops at ANY later heading, so at
# HEAD (no heading follows its section) it legally runs to EOF — either state is
# structurally valid for it, and its needle assertions above carry the content pin.
for pair in cont_step3 cont_step4 cont_step6 ship_reflect acont_ground acont_exec aship_reflect ship_green aship_item3 heal_step2 lane_setup acont_item5 aloop_plan aloop_gate7 aloop_reflect; do
  eval "v=\${$pair}"
  case "$v" in
    *@@BOUNDED@@*) ok "section terminates at its end anchor: $pair" ;;
    *) bad "section ran to EOF — end anchor no longer matches: $pair" ;;
  esac
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

line "$aloop_plan" "codex-autonomous-loop plan gate carries read-before-grep" \
  'Read-before-grep (U-SR-07/WR-14): for a file you will read anyway, read it once' \
  '[B] F5/d3' \
  '"one more targeted grep is cheaper" stops being true'

line "$aloop_gate7" "codex-autonomous-loop local_gate carries the cache-warmth handoff" \
  'Cache-warmth handoff (U-SR-07/WR-14): at >400k context, before any background wait expected to outlast the prompt-cache TTL' \
  '[B] F4' \
  '"the wait costs nothing" bills the next call'

line "$aloop_reflect" "codex-autonomous-loop reflect gate carries the facts-brief handoff" \
  'Facts-brief handoff (U-SR-07/WR-14): if the next item is a heavy audit or document' \
  '[B] F10' \
  '"I already have the context loaded" is the trap'

printf '%s' "$aloop_reflect" | grep -qF -- 'BEFORE running context-save' \
  && ok "codex-autonomous-loop facts-brief names the before-save ordering" \
  || bad "codex-autonomous-loop facts-brief lost the before-save ordering clause"

line "$acont_ground" "codex roadmap-continue grounding carries read-before-grep" \
  'Read-before-grep (U-SR-07/WR-14): for a file you will read anyway, read it once' \
  '[B] F5/d3' \
  '"one more targeted grep is cheaper" stops being true'

line "$acont_item5" "codex roadmap-continue item 5 carries the cache-warmth handoff" \
  'Cache-warmth handoff (U-SR-07/WR-14): at >400k context, before any background wait expected to outlast the prompt-cache TTL' \
  '[B] F4' \
  '"the wait costs nothing" bills the next call'

line "$ship_green" "ship-pr Green bullet carries the cache-warmth handoff" \
  'Cache-warmth handoff (U-SR-07/WR-14): at >400k context, before ANY background wait expected to outlast the prompt-cache TTL' \
  '[B] F4' \
  '"the wait costs nothing, I'"'"'m just sleeping" is the trap'

line "$aship_item3" "codex ship-pr item 3 carries the cache-warmth handoff" \
  'Cache-warmth handoff (U-SR-07/WR-14): at >400k context, before any background wait expected to outlast the prompt-cache TTL' \
  '[B] F4' \
  '"the wait costs nothing" bills the next call'

line "$heal_step2" "self-heal step 2 carries the cache-warmth handoff" \
  'Cache-warmth handoff (U-SR-07/WR-14): at >400k context, before any background wait expected to outlast the prompt-cache TTL' \
  '[B] F4' \
  '"the wait costs nothing" bills the next call'

line "$lane_setup" "two-lane build half carries the cache-warmth handoff" \
  'dead gap at [B] F6; cache-warmth handoff, U-SR-07/WR-14: at >400k context, before any background wait expected to outlast the prompt-cache TTL' \
  '[B] F4' \
  '"the wait costs nothing" bills the next call'

# WR-14(b) coupling at the sibling carriers: the launch instruction and the
# cache-warmth rule must share the ITEM-scoped slice that instructs the launch
# (u-sr-07 codex r6 — same-section co-occurrence let a later-step relocation pass;
# the two-lane needle above pins its inline adjacency to the launch parenthetical).
for spec in "ship_green:$ship_green" "aship_item3:$aship_item3" "heal_step2:$heal_step2" "acont_item5:$acont_item5" "aloop_gate7:$aloop_gate7"; do
  lbl="${spec%%:*}"; text="${spec#*:}"
  if printf '%s' "$text" | grep -qF 'codex-check' && printf '%s' "$text" | grep -qiF 'cache-warmth'; then
    ok "$lbl couples codex-check with the cache-warmth rule in the same step"
  else
    bad "$lbl decouples codex-check from the cache-warmth rule"
  fi
done

line "$acont_next" "codex roadmap-continue before-next-arc carries the facts-brief handoff" \
  'Facts-brief handoff (U-SR-07/WR-14): if the next item is a heavy audit or document' \
  '[B] F10' \
  '"I already have the context loaded" is the trap'

line "$aship_reflect" "codex ship-pr reflect carries the facts-brief handoff" \
  'Facts-brief handoff for a heavy next item (U-SR-07/WR-14): if the next action is a heavy audit or document' \
  '[B] F10' \
  '"I already have the context loaded" is the trap'

# Unconditional facts-brief contract (u-sr-07 codex r4): charter WR-14 clause (a)
# carries NO depth threshold — EVERY heavy audit/document is authored fresh from a
# brief. The >400k trigger belongs to clause (b) (cache-warmth) alone. A depth
# qualifier re-imported into any facts-brief carrier is contract drift and must red.
for spec in "cont_step6:$cont_step6" "ship_reflect:$ship_reflect" "acont_next:$acont_next" "aship_reflect:$aship_reflect" "aloop_reflect:$aloop_reflect"; do
  lbl="${spec%%:*}"; text="${spec#*:}"
  if printf '%s' "$text" | grep -qE '>400k|already deep|sits deep|deep in context'; then
    bad "$lbl facts-brief carrier re-imported a depth qualifier (WR-14 (a) is unconditional)"
  else
    ok "$lbl facts-brief carrier is unconditional (no depth qualifier)"
  fi
done

# Ordering contract (u-sr-07 codex r3): the facts brief is written BEFORE the
# checkpoint save, so the checkpoint carries it — pinned by the numbered-step order
# in the Claude carrier and by the explicit before-clause in both carriers (a reorder
# that saves first strands the fresh author without the brief).
grep -qF '3. **Facts-brief handoff for a heavy next item' "$SHIP" && grep -qF '4. **Run `/context-save`.**' "$SHIP" \
  && ok "ship-pr numbers the facts-brief step before the /context-save step" \
  || bad "ship-pr close-out order drifted: facts-brief must be step 3, /context-save step 4"
printf '%s' "$ship_reflect" | grep -qF -- 'BEFORE the `/context-save` below' \
  && ok "ship-pr facts-brief names the before-save ordering" \
  || bad "ship-pr facts-brief lost the before-save ordering clause"
printf '%s' "$aship_reflect" | grep -qF -- 'written BEFORE running context-save' \
  && ok "codex ship-pr facts-brief names the before-save ordering" \
  || bad "codex ship-pr facts-brief lost the before-save ordering clause"

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

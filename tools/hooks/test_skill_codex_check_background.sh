#!/usr/bin/env bash
# Wiring witness for the U-SR-05 (WR-12) codex-check launch shape. Every Claude loop
# skill that INSTRUCTS running `just codex-check` (roadmap-continue step 4, ship-pr
# Green, self-heal step 2) must carry the run_in_background rule WITH its why ([B] F6:
# a foreground launch hit the Bash tool's 600 s timeout — a 10-minute dead gap).
# Codex-native mirrors (.agents tree) are deliberately NOT carriers: that venue has no
# run_in_background parameter, and prose naming a phantom instrument is the WR-13
# failure mode. Doc-text assertions run against the REAL repo SKILL.md files resolved
# from SCRIPT_DIR (the artifact under test IS the checked-in skill text).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$SCRIPT_DIR/../../.claude/skills"
CONT="$SKILLS/roadmap-continue/SKILL.md"
SHIP="$SKILLS/ship-pr/SKILL.md"
HEAL="$SKILLS/self-heal/SKILL.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$CONT" "$SHIP" "$HEAL"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

# The rule must sit composed in one phrase — "ALWAYS launch … run_in_background" —
# not as scattered tokens sibling prose could satisfy. Matched whitespace-normalized
# (the phrase wraps across hard-wrapped lines). $3 is the per-carrier launch phrase.
rule() { # $1 = file, $2 = label, $3 = launch-phrase needle
  local norm; norm=$(tr '\n' ' ' < "$1" | tr -s ' ')
  local miss=""
  printf '%s' "$norm" | grep -qF -- "$3"        || miss="$miss launch-phrase($3)"
  printf '%s' "$norm" | grep -qF -- '[B] F6'    || miss="$miss why([B] F6)"
  printf '%s' "$norm" | grep -qF -- 'U-SR-05'   || miss="$miss provenance(U-SR-05)"
  if [ -z "$miss" ]; then ok "$2 carries the background-launch rule"; else bad "$2 missing:$miss"; fi
}

rule "$CONT" "roadmap-continue step 4" 'ALWAYS launch it `run_in_background` and poll the task'
rule "$SHIP" "ship-pr Green bullet"    'ALWAYS launch `just codex-check` `run_in_background` and poll the task'
rule "$HEAL" "self-heal step 2"        'ALWAYS launch it `run_in_background` and poll the task'

# Control: the rule must live in the SAME carrier as the codex-check instruction it
# governs — a carrier that names codex-check but not the rule is the regression shape.
for pair in "$CONT:roadmap-continue" "$SHIP:ship-pr" "$HEAL:self-heal"; do
  f="${pair%%:*}"; lbl="${pair#*:}"
  if grep -qF 'just codex-check' "$f" && grep -qF 'run_in_background' "$f"; then
    ok "$lbl names both codex-check and run_in_background"
  else
    bad "$lbl decouples codex-check from the launch rule"
  fi
done

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

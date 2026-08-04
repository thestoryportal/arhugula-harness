#!/usr/bin/env bash
# Hermetic test for the U-WT-04 arc-exit-report ship-pr wiring. Asserts the step is
# PRESENT in BOTH ship-pr carriers (the Claude tree and its Codex-native mirror under
# .agents/, which encodes its rituals independently — a Claude-only step is invisible to
# the Codex flow) and, in the Claude carrier, ORDERED after the reflect/`/context-save`
# block. That ordering is the unit's whole point (plan Feature 3, codex round 11): emitted
# earlier, `checkpoint{path,confirmed}` would record a stale checkpoint, and the merge
# SHA / post-merge CI conclusion / refresh commit would not exist yet.
#
# Doc-text assertions run against the REAL repo SKILL.md files resolved from SCRIPT_DIR
# (no scratch repo: the artifact under test IS the checked-in skill text). Every anchor is
# guarded explicitly — an empty lineno must FAIL, never default to 0 and let an ordering
# comparison pass open when a heading gets renamed (the U-WT-01 test's house pattern).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHIP="$SCRIPT_DIR/../../.claude/skills/ship-pr/SKILL.md"
ASHIP="$SCRIPT_DIR/../../.agents/skills/ship-pr/SKILL.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$SHIP" "$ASHIP"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

# line number of the first line matching a fixed string, empty if absent
lineno() { grep -nF -- "$2" "$1" | head -1 | cut -d: -f1; }

# --- 1. Claude ship-pr: the step exists at all ---
L_CMD=$(lineno "$SHIP" 'just arc-exit-report --pr')
if [ -n "$L_CMD" ]; then
  ok "claude ship-pr invokes the recipe (line $L_CMD)"
else
  bad "claude ship-pr does not invoke 'just arc-exit-report --pr'"
fi

# --- 2. Claude ship-pr: ordered AFTER the reflect/context-save anchor ---
# Both anchors guarded: a renamed heading or a moved context-save bullet yields an empty
# lineno and must FAIL CLOSED rather than compare against an implicit 0.
L_CTX=$(lineno "$SHIP" 'Run `/context-save`')
L_SECT=$(lineno "$SHIP" '## Arc exit report')
if [ -n "$L_CTX" ] && [ -n "$L_SECT" ] && [ -n "$L_CMD" ]; then
  if [ "$L_SECT" -gt "$L_CTX" ] && [ "$L_CMD" -gt "$L_CTX" ]; then
    ok "claude ship-pr ordering context-save($L_CTX) < exit-report section($L_SECT) < command($L_CMD)"
  else
    bad "claude ship-pr emits the exit report BEFORE context-save: ctx=$L_CTX section=$L_SECT cmd=$L_CMD"
  fi
else
  bad "claude ship-pr anchors missing: context-save='$L_CTX' section='$L_SECT' command='$L_CMD'"
fi

# --- 3. Claude ship-pr: the section states WHY the ordering is load-bearing + what to do
#        with the output. Scoped to the section block (guarded start/end), never the whole
#        file — sibling prose elsewhere must not satisfy these needles.
L_END=$(lineno "$SHIP" '## Notes')
if [ -n "$L_SECT" ] && [ -n "$L_END" ] && [ "$L_END" -gt "$L_SECT" ]; then
  BLK=$(awk -v s="$L_SECT" -v e="$L_END" 'NR>=s && NR<e' "$SHIP")
else
  BLK=""
fi
NORM=$(printf '%s' "$BLK" | tr '\n' ' ' | tr -s ' ')
miss=""
printf '%s' "$NORM" | grep -qF -- 'After** the reflect + `/context-save` block above, not before it' \
  || miss="$miss after-context-save-rationale"
printf '%s' "$NORM" | grep -qF -- 'Paste the emitted `yaml` block' || miss="$miss paste-yaml-block"
printf '%s' "$NORM" | grep -qF -- 'machine-readable closure record' || miss="$miss closure-record"
printf '%s' "$NORM" | grep -qF -- 'refresh_commit: null' || miss="$miss never-fabricated-refresh"
if [ -z "$miss" ]; then
  ok "claude ship-pr exit-report section carries the full contract"
else
  bad "claude ship-pr exit-report section missing:$miss"
fi

# --- 4. Codex-native mirror: the step exists (parity contract) ---
L_ACMD=$(lineno "$ASHIP" 'just arc-exit-report --pr')
if [ -n "$L_ACMD" ]; then
  ok "codex-native ship-pr mirrors the recipe (line $L_ACMD)"
else
  bad "codex-native ship-pr does not invoke 'just arc-exit-report --pr'"
fi

# --- 5. Codex-native mirror: ordered after its own reflect/context-save section ---
L_ACTX=$(lineno "$ASHIP" '## Reflect and checkpoint')
L_ASECT=$(lineno "$ASHIP" '## Arc exit report')
if [ -n "$L_ACTX" ] && [ -n "$L_ASECT" ] && [ -n "$L_ACMD" ]; then
  if [ "$L_ASECT" -gt "$L_ACTX" ] && [ "$L_ACMD" -gt "$L_ACTX" ]; then
    ok "codex-native ordering reflect($L_ACTX) < exit-report section($L_ASECT) < command($L_ACMD)"
  else
    bad "codex-native emits the exit report BEFORE reflect: ctx=$L_ACTX section=$L_ASECT cmd=$L_ACMD"
  fi
else
  bad "codex-native anchors missing: reflect='$L_ACTX' section='$L_ASECT' command='$L_ACMD'"
fi

# --- 6. Codex-native mirror: same substantive contract, in its own venue's voice ---
ABLK=$(awk '/^## Arc exit report/{f=1;next} /^## /{f=0} f' "$ASHIP")
ANORM=$(printf '%s' "$ABLK" | tr '\n' ' ' | tr -s ' ')
amiss=""
printf '%s' "$ANORM" | grep -qF -- 'after the reflect and `context-save` step above — never before it' \
  || amiss="$amiss after-context-save-rationale"
printf '%s' "$ANORM" | grep -qF -- 'Paste the emitted `yaml` block' || amiss="$amiss paste-yaml-block"
printf '%s' "$ANORM" | grep -qF -- 'machine-readable closure record' || amiss="$amiss closure-record"
printf '%s' "$ANORM" | grep -qF -- 'require exit 0' || amiss="$amiss validate-external-call"
if [ -z "$amiss" ]; then
  ok "codex-native exit-report section carries the full contract"
else
  bad "codex-native exit-report section missing:$amiss"
fi

# --- 7. The recipe the skills name actually exists in the justfile ---
JUSTFILE="$SCRIPT_DIR/../../justfile"
if [ -f "$JUSTFILE" ] && grep -qE '^arc-exit-report \*ARGS:' "$JUSTFILE"; then
  ok "justfile defines the arc-exit-report recipe both carriers name"
else
  bad "justfile has no 'arc-exit-report *ARGS:' recipe — both skill steps would fail"
fi

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

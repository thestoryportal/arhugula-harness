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
printf '%s' "$ANORM" | grep -qF -- 'after the reflect and `context-save` step above, never before it' \
  || amiss="$amiss after-context-save-rationale"
printf '%s' "$ANORM" | grep -qF -- 'Paste the emitted `yaml` block' || amiss="$amiss paste-yaml-block"
printf '%s' "$ANORM" | grep -qF -- 'machine-readable closure record' || amiss="$amiss closure-record"
printf '%s' "$ANORM" | grep -qF -- 'require exit 0' || amiss="$amiss validate-external-call"
if [ -z "$amiss" ]; then
  ok "codex-native exit-report section carries the full contract"
else
  bad "codex-native exit-report section missing:$amiss"
fi

# --- 6b. Both carriers skip the report for a terminating-refresh PR (codex round-1):
#         a refresh-only PR is not an arc; running the report there would mislabel its
#         structurally-absent refresh as an open obligation.
printf '%s' "$NORM" | grep -qF -- 'Skip this step entirely when the PR was itself the terminating roadmap-status refresh' \
  && ok "claude carrier skips the report on a terminating-refresh PR" \
  || bad "claude carrier missing the refresh-PR skip clause"
printf '%s' "$ANORM" | grep -qF -- 'Skip entirely for a pure terminating-refresh PR' \
  && ok "codex carrier skips the report on a terminating-refresh PR" \
  || bad "codex carrier missing the refresh-PR skip clause"

# --- 6d. Both carriers BIND the checkpoint explicitly (codex round-3 P1): the roadmap
#         authorizes a parallel frontier, so an unbound run can only report the
#         workspace-newest file as an unconfirmed heuristic. The command shape must carry
#         --checkpoint, and the rationale must name the parallel frontier — a bare flag
#         with no reason gets dropped by the next editor.
printf '%s' "$NORM" | grep -qF -- '--checkpoint <the-path-/context-save-just-reported>' \
  && ok "claude carrier binds the checkpoint on the command line" \
  || bad "claude carrier command omits --checkpoint"
printf '%s' "$NORM" | grep -qF -- 'parallel frontier' \
  && ok "claude carrier states WHY the checkpoint must be bound" \
  || bad "claude carrier missing the parallel-frontier rationale"
printf '%s' "$ANORM" | grep -qF -- '--checkpoint <the-path-context-save-just-reported>' \
  && ok "codex carrier binds the checkpoint on the command line" \
  || bad "codex carrier command omits --checkpoint"
printf '%s' "$ANORM" | grep -qF -- 'parallel frontier' \
  && ok "codex carrier states WHY the checkpoint must be bound" \
  || bad "codex carrier missing the parallel-frontier rationale"

# --- 6c. Codex carrier: next-arc launch is deferred until AFTER the report (codex
#         round-1) — the reflect section's launch sentence must name the report gate.
AREFL=$(awk '/^## Reflect and checkpoint/{f=1;next} /^## /{f=0} f' "$ASHIP")
printf '%s' "$AREFL" | tr '\n' ' ' | tr -s ' ' | grep -qF -- 'and the arc exit report below' \
  && ok "codex carrier defers next-arc launch until after the report" \
  || bad "codex carrier launches the next arc before the exit report"

# --- 6e. Codex carrier: the report runs BEFORE worktree disposition (codex round-8 P1:
#         disposition deletes the arc worktree ledger the report reads), and the
#         direct autonomous-loop flow carries its own report gate (round-8 P2: that
#         flow never routes through ship-pr, so a ship-pr-only step is unreachable).
printf '%s' "$ANORM" | grep -qF -- "BEFORE the arc worktree's disposition" \
  && ok "codex ship-pr orders the report before worktree disposition" \
  || bad "codex ship-pr missing the before-disposition ordering"
ALOOP="$SCRIPT_DIR/../../.agents/skills/codex-autonomous-loop/SKILL.md"
if [ -f "$ALOOP" ]; then
  L_LCMD=$(lineno "$ALOOP" 'just arc-exit-report --pr')
  L_LDISP=$(lineno "$ALOOP" '`worktree_disposition`: original worktree is unregistered')
  if [ -n "$L_LCMD" ] && [ -n "$L_LDISP" ] && [ "$L_LCMD" -lt "$L_LDISP" ]; then
    ok "autonomous-loop carries the report gate before disposition ($L_LCMD < $L_LDISP)"
  else
    bad "autonomous-loop report gate missing/misordered: cmd='$L_LCMD' disposition='$L_LDISP'"
  fi
else
  bad "codex-autonomous-loop SKILL.md missing"
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

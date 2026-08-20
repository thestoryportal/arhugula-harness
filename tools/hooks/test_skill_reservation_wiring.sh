#!/usr/bin/env bash
# Hermetic grep witness for U-HE-21: the reservation CLI wiring must be CARRIED by the
# skill/hook text that drives each lane (C-HE-03 §3/§4, C-HE-26 §1, C-HE-06 §4(ii)).
#
#   * `.claude/skills/roadmap-continue/SKILL.md` — arc OPEN: the instant a unit is selected,
#     BEFORE any work, the lane checks `selectable` and creates the `pending` reservation
#     with `--arc-type` declared NOW (C-HE-26 §1 open-time capture point), then exports
#     HARNESS_ARC_ID so the review wrapper's rows join the real reservation instead of the
#     `branch-*` fallback (review_wrapper_common.env_arc_and_lane).
#   * `.claude/skills/ship-pr/SKILL.md` — back-fill: `pr`/`head_sha`/`base_sha` at PR
#     creation, the full merge tuple + `attested_merge_tree` at the final gate
#     (C-HE-03 §3; consumed byte-compare at the door by C-HE-06 §4(ii)).
#   * `tools/roadmap-audit/session-start.sh` — the C-HE-03 §5 ground-truth reconcile pass
#     (`reconcile-all`) runs at session start. NOTE: the plan sketch named
#     `tools/hooks/session-start.sh`, which does not exist; the real carrier is the
#     roadmap-audit hook (registered at the plan's U-HE-18 rev item (iii)); the pass itself
#     landed with U-HE-18 — this witness pins it against removal.
#
# Needles are FIXED STRINGS naming the specific CLI obligation (a bare "reservation" is
# satisfied by narration; `reservations.py reserve --arc-id` is not). Doc-text assertions
# run against the REAL repo files resolved from SCRIPT_DIR (the artifact under test IS the
# checked-in text). Same ok/bad idiom as test_skill_two_lane.sh.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RC="$SCRIPT_DIR/../../.claude/skills/roadmap-continue/SKILL.md"
SP="$SCRIPT_DIR/../../.claude/skills/ship-pr/SKILL.md"
SS="$SCRIPT_DIR/../roadmap-audit/session-start.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$RC" "$SP" "$SS"; do
  [ -f "$f" ] || { bad "missing carrier: $f"; echo "FAILED: $FAIL failure(s)"; exit 1; }
done

echo "U-HE-21 reservation carrier wiring (C-HE-03 §3/§4, C-HE-26 §1):"

# --- roadmap-continue: arc open (C-HE-03 §4 — reserve at selection, before any work) ---
grep -q 'python tools/reservations.py reserve --arc-id' "$RC" \
  && ok "roadmap-continue reserves at selection" || bad "no reserve step in roadmap-continue"
grep -q 'python tools/reservations.py selectable --arc-id' "$RC" \
  && ok "selection checks selectable" || bad "no selectable check in roadmap-continue"
grep -q -- '--arc-type' "$RC" \
  && ok "arc_type declared at open (C-HE-26 §1)" || bad "arc_type not declared at open"
grep -q 'export HARNESS_ARC_ID' "$RC" \
  && ok "HARNESS_ARC_ID exported" || bad "no HARNESS_ARC_ID export"

# --- ship-pr: back-fill (C-HE-03 §3) + attested tree (C-HE-06 §4(ii)) ---
grep -q 'reservations.py update --arc-id .* --set pr=' "$SP" \
  && ok "ship-pr back-fills pr/head_sha/base_sha at PR creation" || bad "no pr back-fill in ship-pr"
grep -q 'attested_merge_tree=' "$SP" \
  && ok "ship-pr records attested_merge_tree at final gate" || bad "no attested_merge_tree in ship-pr"

# --- session-start: C-HE-03 §5 ground-truth reconcile pass (landed U-HE-18; pinned here) ---
grep -q 'reservations.py reconcile-all' "$SS" \
  && ok "session-start runs reconcile-all" || bad "no reconcile-all in session-start hook"

echo
if [ "$FAIL" -gt 0 ]; then
  echo "FAILED: $FAIL failure(s), $PASS passed"
  exit 1
fi
echo "PASSED: $PASS assertion(s)"

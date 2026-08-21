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

# --- roadmap-continue: round-1 codex corrections (env propagation + resume flow) ---
grep -q 'do NOT survive across Bash tool calls' "$RC" \
  && ok "env non-inheritance stated (ids restated inline)" || bad "no fresh-shell env warning"
grep -q 'show --arc-id' "$RC" \
  && ok "resume path reads the head via show" || bad "no show-based resume path"
grep -q 'WITHOUT re-reserving' "$RC" \
  && ok "same-lane resume forbids re-reserve" || bad "no same-lane resume clause"
grep -q 'do NOT reserve' "$RC" \
  && ok "other-lane path re-derives instead of reserving" || bad "no other-lane branch"
# Round-2 codex corrections:
grep -q 'mint-lane-id' "$RC" \
  && ok "lane id minted via mint-lane-id" || bad "no mint-lane-id step"
grep -q '\.harness/\.lane-id' "$RC" \
  && ok "lane id persisted per worktree (.harness/.lane-id)" || bad "no lane-id persistence"
grep -q 'HARNESS_ARC_ID=<arc-id> HARNESS_LANE_ID=<lane-id> just review-with-failover' "$RC" \
  && ok "roadmap-continue names the inline-prefixed review invocation" \
  || bad "no inline-prefixed review invocation in roadmap-continue"
grep -q 'HARNESS_ARC_ID=<arc-id> HARNESS_LANE_ID=<lane-id> just review-with-failover' "$SP" \
  && ok "ship-pr preflight review carries the inline HARNESS_* prefix (standalone runs)" \
  || bad "ship-pr preflight review lacks the inline HARNESS_* prefix"
# Round-4 codex corrections (races + headless degradation):
grep -q 'lost race' "$RC" || grep -q 'lost the race' "$RC" \
  && ok "reserve race-loss handled like the occupied path" || bad "no reserve race-loss clause"
grep -q 'NEVER overwrite' "$RC" \
  && ok "lane-id file content is authoritative (never overwrite)" || bad "no lane-id overwrite rule"
grep -q 'RE-READ the file' "$RC" \
  && ok "lane-id mint adopts the file content after write" || bad "no post-write re-read rule"
grep -q 'proceed with the arc UNRESERVED' "$RC" \
  && ok "headless denial degrades to unreserved-with-note (U-HE-19 drain bootstrap)" \
  || bad "no headless degradation clause"
# Round-5 codex corrections:
if grep -n 'just review-with-failover' "$RC" "$SP" | grep -v 'HARNESS_ARC_ID=' | grep -v 'bare' | grep -q .; then
  bad "a review-with-failover invocation lacks the inline HARNESS_* prefix (bare form writes fallback ids)"
else
  ok "EVERY review-with-failover mention is prefixed (or the marked bare headless fallback)"
fi
grep -q 'if ANY arc-open command' "$RC" \
  && ok "headless degradation triggers on ANY refused arc-open command" \
  || bad "degradation trigger covers only reserve"
grep -q 'NEVER resume a terminal head' "$RC" \
  && ok "terminal heads are never resumed (state checked before lane_id)" \
  || bad "no terminal-head refusal in the resume branches"
grep -q 'SKIP both this back-fill' "$SP" \
  && ok "ship-pr skips back-fills for an unreserved (headless-degraded) arc" \
  || bad "no unreserved-skip clause in ship-pr back-fill"
# Mandatory commands must be substitution-free single invocations (guard-compatible):
if grep -E 'reservations\.py (reserve|update|selectable|show)' "$RC" "$SP" | grep -q '\$('; then
  bad "a mandatory reservation command still uses \$( ) command substitution"
else
  ok "reservation commands are substitution-free (literal values)"
fi

# --- ship-pr: back-fill (C-HE-03 §3) + attested tree (C-HE-06 §4(ii)) ---
grep -q 'reservations.py update --arc-id .* --set pr=' "$SP" \
  && ok "ship-pr back-fills pr/head_sha/base_sha at PR creation" || bad "no pr back-fill in ship-pr"
grep -q 'attested_merge_tree=' "$SP" \
  && ok "ship-pr records attested_merge_tree at final gate" || bad "no attested_merge_tree in ship-pr"

# --- session-start: C-HE-03 §5 ground-truth reconcile pass (landed U-HE-18; pinned here) ---
grep -q 'reservations.py reconcile-all' "$SS" \
  && ok "session-start runs reconcile-all" || bad "no reconcile-all in session-start hook"

# --- guard adjudication floor (codex r3; degradation contract made explicit r7): the
# documented command shapes must NEVER be DENIED by permission-guard in loop mode. Today
# they fall through to ask (the registered U-HE-25 friction — one approval prompt each
# attended; ask→deny in the HEADLESS runner, where the carriers' explicit degradation
# contract applies: any refused arc-open command → proceed UNRESERVED + PR-body note;
# refused prefixed review → bare allowlisted review-with-failover; unreserved back-fills
# skipped — each clause grep-witnessed above, and the bare-review ALLOW floor witnessed
# below). After U-HE-25's exact-shape allowlist additions these become allow and the
# degradation goes dormant. A DENY would structurally block the loop — that regression is
# what this leg pins. The guard is exercised for real, not grepped.
GUARD="$SCRIPT_DIR/permission-guard.sh"
GREPO="$(mktemp -d)" && mkdir -p "$GREPO/.harness"
guard_dec() { # $1=command → prints permissionDecision, or "ask" (guard exit 0, no output).
  # Distinguishes a genuine fall-through ask from a crashed guard / broken jq stage
  # (codex r4 P2: an inert pipeline must not read as "never denied").
  local payload raw rc
  payload=$(jq -nc --arg c "$1" \
    '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":$c,"file_path":""}}') || { echo PIPELINE_FAILURE; return; }
  raw=$(printf '%s' "$payload" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$GREPO" bash "$GUARD"); rc=$?
  [ "$rc" -ne 0 ] && { echo PIPELINE_FAILURE; return; }
  if [ -z "$raw" ]; then echo ask; return; fi
  printf '%s' "$raw" | jq -r '.hookSpecificOutput.permissionDecision // "ask"' || echo PIPELINE_FAILURE
}
# Positive control FIRST: a crashed/inert guard must fail loudly, not pass silently
# (a gate that cannot tell "empty" from "unlooked" is no gate).
DEC="$(guard_dec 'git push --force origin main')"
[ "$DEC" = "deny" ] && ok "positive control: guard denies force-push" \
  || bad "positive control failed — guard did not deny force-push (got: $DEC)"
# The headless review FALLBACK must be allow (not merely non-deny): a bare
# `just review-with-failover` is the documented degradation when the prefixed form is
# refused, so losing its allowlist entry would strand headless review entirely.
DEC="$(guard_dec 'just review-with-failover')"
[ "$DEC" = "allow" ] && ok "bare review-with-failover adjudicates ALLOW (headless fallback floor)" \
  || bad "bare review-with-failover no longer allowlisted (got: $DEC) — headless fallback broken"
while IFS= read -r shape; do
  DEC="$(guard_dec "$shape")"
  case "$DEC" in
    allow|ask) ok "guard never denies ($DEC): $shape" ;;
    *) bad "guard adjudication failed for mandatory carrier command ($DEC): $shape" ;;
  esac
done <<'SHAPES'
uv run python tools/reservations.py mint-lane-id
uv run python tools/reservations.py selectable --arc-id u-he-21
uv run python tools/reservations.py reserve --arc-id u-he-21 --lane-id lane-a --branch feat/x --arc-type applying
uv run python tools/reservations.py show --arc-id u-he-21
uv run python tools/reservations.py update --arc-id u-he-21 --set pr=1 head_sha=abc base_sha=def
HARNESS_ARC_ID=u-he-21 HARNESS_LANE_ID=lane-a just review-with-failover
git merge-tree --write-tree origin/main HEAD
SHAPES
rm -rf "$GREPO"

echo
if [ "$FAIL" -gt 0 ]; then
  echo "FAILED: $FAIL failure(s), $PASS passed"
  exit 1
fi
echo "PASSED: $PASS assertion(s)"

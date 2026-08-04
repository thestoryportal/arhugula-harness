#!/usr/bin/env bash
# Hermetic test for the U-WT-08 two-lane pilot recipe, asserted across BOTH carriers — which
# carry DIFFERENT contracts, exactly as with U-WT-05's red-first pair:
#
#   * `.claude/skills/two-lane/SKILL.md` is the CANONICAL body. It must carry the recipe in
#     full: the `.codex-worktrees/<slug>` lane roots, the strictly-serial merge/refresh rule,
#     the explicit "§12 is unchanged" statement, the one-lane-holds-the-fixed-point rule, the
#     abandon-and-rebase conflict rule with its no-heuristics clause, the
#     safe-worktree-remove-only reaping path, the three deliberate CUTs, and the ≥3-pilot-runs
#     trigger for any follow-on orchestration.
#   * `.agents/skills/two-lane/SKILL.md` is a POINTER BRIDGE, not an independent projection.
#     two-lane is not one of the three Codex-native workflows
#     ({merge-gate, roadmap-continue, ship-pr}), so the non-native-bridge test in
#     `tools/test_codex_workflow_parity.py` requires it to name the canonical path, defer to it
#     completely, and apply runner translations only. A bridge that regrows the canonical
#     sections is a second contract to drift — §5 asserts against exactly that.
#
# Needles are per-carrier FIXED STRINGS chosen so the file's sibling prose cannot satisfy them
# (a bare "serial" or "worktree" is satisfied by the surrounding narration; the needles below
# name the specific obligation). Doc-text assertions run against the REAL repo SKILL.md files
# resolved from SCRIPT_DIR (no scratch repo: the artifact under test IS the checked-in text).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_SKILL="$SCRIPT_DIR/../../.claude/skills/two-lane/SKILL.md"
CODEX_SKILL="$SCRIPT_DIR/../../.agents/skills/two-lane/SKILL.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$CLAUDE_SKILL" "$CODEX_SKILL"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

# $1 = file, $2 = carrier label, $3 = contract element, $4 = fixed-string needle.
# Requires EXACTLY ONE matching line: a needle satisfied twice means the contract statement was
# duplicated (two places to drift), and a needle satisfied zero times means it is gone.
needle() {
  local hits
  hits=$(grep -cF -- "$4" "$1")
  if [ "$hits" -eq 1 ]; then
    ok "$2 carries $3"
  else
    bad "$2: $3 matched $hits lines, want exactly 1 (needle: $4)"
  fi
}

# $1 = file, $2 = carrier label, $3 = what must be absent, $4 = fixed-string needle
absent() {
  if grep -qF -- "$4" "$1"; then
    bad "$2 must not carry $3 (found: $4)"
  else
    ok "$2 omits $3"
  fi
}

# line number of the first line matching a fixed string, empty if absent
lineno() { grep -nF -- "$2" "$1" | head -1 | cut -d: -f1; }

# --- 1. Claude carrier: frontmatter, opt-in, lane roots ---------------------------------
needle "$CLAUDE_SKILL" "claude two-lane" "its skill name in frontmatter" 'name: two-lane'
needle "$CLAUDE_SKILL" "claude two-lane" "the opt-in-only statement" \
  '**Opt-in only — never auto-invoked from `roadmap-continue` or `ship-pr`.**'
needle "$CLAUDE_SKILL" "claude two-lane" "the ignored lane-root path" \
  'own worktree under `.codex-worktrees/<slug>`'
needle "$CLAUDE_SKILL" "claude two-lane" "the both-lanes-off-one-main rule" \
  'Both lanes branch off the **same** fresh `origin/main`'
needle "$CLAUDE_SKILL" "claude two-lane" "the build-half-is-not-serialized statement" \
  'Nothing about the build half is serialized.'

# --- 2. Claude carrier: the serial merge lane (the load-bearing half) --------------------
# The whole recipe reduces to this: builds parallelize, landings do not. Both halves of the
# statement must be present verbatim — "strictly serial" without "§12 unchanged" reads as a
# governance change, and "§12 unchanged" without "strictly serial" states no constraint.
needle "$CLAUDE_SKILL" "claude two-lane" "the strictly-serial merge+refresh rule" \
  '**Merges and terminating refreshes are STRICTLY SERIAL through `ship-pr`. §12 is unchanged by'
needle "$CLAUDE_SKILL" "claude two-lane" "the adds-no-governance clause" \
  'this recipe adds no governance, weakens no gate, and introduces no alternative'
needle "$CLAUDE_SKILL" "claude two-lane" "the one-lane-holds-the-fixed-point rule" \
  '**One lane holds the `ship-pr` fixed point at a time.**'
needle "$CLAUDE_SKILL" "claude two-lane" "the merge-gate-is-not-a-build-half-step rule" \
  '**`merge-gate` and the'
needle "$CLAUDE_SKILL" "claude two-lane" "the replay-before-gate rule for lane B" \
  "**Lane B's merge sequence starts with a replay, not a gate.**"
needle "$CLAUDE_SKILL" "claude two-lane" "the wait-for-the-REFRESH (not the content PR) rule" \
  "terminating refresh PR has merged* — not merely lane A's content"
needle "$CLAUDE_SKILL" "claude two-lane" "the explicit landing order" \
  'A content → A refresh → B content → B refresh'
needle "$CLAUDE_SKILL" "claude two-lane" "why interleaving breaks (accumulated drift)" \
  'accumulated two-commit drift'

# --- 3. Claude carrier: the conflict rule + its guard mechanics --------------------------
# "Abandon and rebase" is the whole conflict policy; the no-heuristics clause is what makes it
# a RULE rather than a suggestion, so it must not be separable from it.
needle "$CLAUDE_SKILL" "claude two-lane" "the abandon-and-rebase conflict rule" \
  "abandon the second lane's branch and"
needle "$CLAUDE_SKILL" "claude two-lane" "the no-heuristics / no-rescue clause" \
  'no merge-order heuristics, no cherry-pick rescue'
needle "$CLAUDE_SKILL" "claude two-lane" "the do-not-reorder-the-lanes prohibition" \
  'Do not reorder the lanes to make the conflict go away'
needle "$CLAUDE_SKILL" "claude two-lane" 'the guard-denied git-rebase fact' \
  '`git rebase` is hard-denied by the permission guard'
needle "$CLAUDE_SKILL" "claude two-lane" "the abandon-means-do-not-merge-it clarification" \
  'Abandoning'

# --- 4. Claude carrier: reaping + the deliberate CUTs ------------------------------------
needle "$CLAUDE_SKILL" "claude two-lane" "the safe-worktree-remove-ONLY reaping rule" \
  '**reaped ONLY via `tools/hooks/safe-worktree-remove.sh`**'
needle "$CLAUDE_SKILL" "claude two-lane" "the direct-removal-is-denied fact" \
  'Direct `git worktree remove` is hard-denied'
needle "$CLAUDE_SKILL" "claude two-lane" "the nonzero-exit-is-a-real-refusal rule" \
  'A nonzero exit is a real refusal, not a retry prompt'
needle "$CLAUDE_SKILL" "claude two-lane" "the three deliberate CUTs" \
  '**No spawner script, no merge-queue lock, no conflict automation.**'
needle "$CLAUDE_SKILL" "claude two-lane" "the depth-1 / lock-is-ceremony rationale" \
  'structurally depth-1 — a lock is ceremony'
needle "$CLAUDE_SKILL" "claude two-lane" "the no-conflict-automation rationale" \
  'automating it would'
needle "$CLAUDE_SKILL" "claude two-lane" "the >=3-pilot-runs follow-on trigger" \
  'registered only after ≥3 manual pilot runs surface a named'
needle "$CLAUDE_SKILL" "claude two-lane" "the named-not-hypothetical qualifier" \
  'not a hypothetical one'

# --- 5. Claude carrier: setup precedes the merge lane precedes the CUTs ------------------
C_SETUP=$(lineno "$CLAUDE_SKILL" '## Lane setup')
C_MERGE=$(lineno "$CLAUDE_SKILL" '## The merge lane — strictly serial')
C_CONF=$(lineno "$CLAUDE_SKILL" '## On merge conflict — abandon and rebase')
C_CUTS=$(lineno "$CLAUDE_SKILL" '## Deliberate CUTs')
if [ -n "$C_SETUP" ] && [ -n "$C_MERGE" ] && [ -n "$C_CONF" ] && [ -n "$C_CUTS" ] \
   && [ "$C_SETUP" -lt "$C_MERGE" ] && [ "$C_MERGE" -lt "$C_CONF" ] && [ "$C_CONF" -lt "$C_CUTS" ]; then
  ok "claude two-lane orders setup($C_SETUP) < merge($C_MERGE) < conflict($C_CONF) < cuts($C_CUTS)"
else
  bad "claude two-lane ordering: setup='$C_SETUP' merge='$C_MERGE' conflict='$C_CONF' cuts='$C_CUTS'"
fi

# --- 6. Codex carrier: the BRIDGE contract, not a second copy of the recipe --------------
# The first four needles are the predicates the pytest parity lane enforces for every
# non-native bridge, asserted here too so a regression is caught by this standalone hook test
# as well as by the pytest lane.
needle "$CODEX_SKILL" "codex-native two-lane" "its skill name in frontmatter" 'name: two-lane'
needle "$CODEX_SKILL" "codex-native two-lane" "the bridge heading" \
  '# Canonical Claude Workflow Bridge'
needle "$CODEX_SKILL" "codex-native two-lane" "the canonical source path" \
  'Read `.claude/skills/two-lane/SKILL.md` completely'
needle "$CODEX_SKILL" "codex-native two-lane" "the re-record-from-worktree_ready-after-replay rule" \
  '**re-run and re-record ALL gates from `worktree_ready` onward**'
needle "$CODEX_SKILL" "codex-native two-lane" "the abandoned-branch-outside-loop-state disposition" \
  'The abandoned original branch then sits OUTSIDE the loop state'
needle "$CODEX_SKILL" "codex-native two-lane" "the defer-to-canonical contract" \
  'full workflow and the source of truth'
needle "$CODEX_SKILL" "codex-native two-lane" "the translations-only limit" \
  'Apply these runner translations only:'
needle "$CODEX_SKILL" "codex-native two-lane" "the no-summarize pledge" \
  'does not summarize, trim, or replace it'

# --- 7. Codex carrier: the two-lane-specific runner translations -------------------------
needle "$CODEX_SKILL" "codex-native two-lane" "the lane-is-a-codex-exec-leg translation" \
  'one non-interactive `codex exec --profile arhugula-implementer` leg'
needle "$CODEX_SKILL" "codex-native two-lane" "the concurrency-cap-of-2 grounding" \
  'exactly the standing concurrency cap of 2'
needle "$CODEX_SKILL" "codex-native two-lane" "the fixed-point-to-loop-gates mapping" \
  "maps to this flow's autonomous-loop gates"
needle "$CODEX_SKILL" "codex-native two-lane" "the serial constraint restated in gate terms" \
  'lane B records no merge gate until lane A'
needle "$CODEX_SKILL" "codex-native two-lane" "the AskUserQuestion surface translation" \
  'use this runner'"'"'s operator-input surface instead'
needle "$CODEX_SKILL" "codex-native two-lane" "the guard-approved worktree cleanup" \
  'safe-worktree-remove.sh'
needle "$CODEX_SKILL" "codex-native two-lane" "the §12-unchanged restatement" \
  '§12 is unchanged by this skill in either runner'
needle "$CODEX_SKILL" "codex-native two-lane" "the operator-request-only invocation rule" \
  'never chain this skill automatically from roadmap-continue, ship-pr, or the autonomous loop'

# --- 8. Codex carrier: it must NOT re-implement the canonical body -----------------------
# A bridge that grows its own setup/merge/conflict/cut sections is a second contract to drift;
# the pytest parity lane only checks the pointer predicates, so the duplication check lives
# here — against the CANONICAL carrier's own headings (the shape a copy would take).
absent "$CODEX_SKILL" "codex-native two-lane" "a copied canonical lane-setup heading" \
  '## Lane setup'
absent "$CODEX_SKILL" "codex-native two-lane" "a copied canonical merge-lane heading" \
  '## The merge lane'
absent "$CODEX_SKILL" "codex-native two-lane" "a copied canonical conflict-rule heading" \
  '## On merge conflict'
absent "$CODEX_SKILL" "codex-native two-lane" "a copied canonical reaping heading" \
  '## Reaping a lane'
absent "$CODEX_SKILL" "codex-native two-lane" "a copied canonical CUTs heading" \
  '## Deliberate CUTs'
# ...and it must not smuggle the cut machinery back in as a Codex-side "translation".
absent "$CODEX_SKILL" "codex-native two-lane" "a spawner script it was never given" \
  'spawner'
absent "$CODEX_SKILL" "codex-native two-lane" "a merge-queue lock the fixed point makes moot" \
  'merge-queue lock'

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

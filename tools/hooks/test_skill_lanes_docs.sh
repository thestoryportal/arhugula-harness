#!/usr/bin/env bash
# Hermetic doc witness for U-HE-39 (spec-he-loop-lanes C-HE-01 / C-HE-14 / C-HE-21 / C-HE-34 /
# C-HE-35 and §8 AC#7). The four in-scope loop-skill carriers must: state the lane model at
# N ≥ 2 with no N=2 literal cap; carry the C-HE-14 rejected/blocked table byte-exact from the
# spec; cite live carriers for invariants #5/#14 and state #16 void; record the Part D
# non-goals and the K5–K8 dispositions; and name no numeric round cap.
#
# Every normative claim is pinned WHOLE, matched against the carrier with its whitespace
# flattened, so a sentence that wraps across lines or a list item's indent is one searchable
# string. A fragment needle leaves every clause past it invertible with the witness green:
# the merge-gate witness lens found that twice on this unit — K5/K7/K8 pinned only by their
# `- **Kn —` bullet (round 1), then K7's "shadow mode only" clause left outside a first-half
# needle (round 2). For a doc witness the mutation that matters is negating a clause, not
# deleting a line.
#
# The round-cap scan matches spelled numbers as well as digits — the cap this unit recast
# read "ten rounds", which the plan's digits-only pattern passed.
#
# Usage: test_skill_lanes_docs.sh [root]   (default: this checkout). The root argument lets the
# witness run against an older tree (e.g. `git archive origin/main`) to confirm it is red there.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$SCRIPT_DIR/../..}"
TL="$ROOT/.claude/skills/two-lane/SKILL.md"
RC="$ROOT/.claude/skills/roadmap-continue/SKILL.md"
MG="$ROOT/.claude/skills/merge-gate/SKILL.md"
SP="$ROOT/.claude/skills/ship-pr/SKILL.md"
SPEC="$ROOT/.harness/spec/Spec_HE_Loop_Lanes_v1.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$TL" "$RC" "$MG" "$SP" "$SPEC"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

skill() { basename "$(dirname "$1")"; }

# $1 = file, $2 = what, $3 = exact line that must exist (a cite must name a live heading)
has_line() {
  if grep -qxF -- "$3" "$1"; then
    ok "$(skill "$1") has the live heading $2"
  else
    bad "$(skill "$1"): cited heading $2 is not a line in the file (want: $3)"
  fi
}

# $1 = file: the file as one line, every run of newlines/tabs/spaces collapsed to one space.
flat() { tr '\n\t' '  ' < "$1" | tr -s ' '; }

file_of() {
  case "$1" in
    TL) printf '%s' "$TL" ;; RC) printf '%s' "$RC" ;;
    MG) printf '%s' "$MG" ;; SP) printf '%s' "$SP" ;;
    *) return 1 ;;
  esac
}

# --- 1. Whole claims (C-HE-01, C-HE-21, C-HE-34, C-HE-35) ---------------------------------
# One claim per line, `KEY|full sentence as it reads with whitespace flattened`.
FLAT_TL=$(flat "$TL"); FLAT_RC=$(flat "$RC"); FLAT_MG=$(flat "$MG"); FLAT_SP=$(flat "$SP")
EXPECTED_CLAIMS=30
seen=0
while IFS='|' read -r key claim; do
  [ -n "$key" ] || continue
  seen=$((seen+1))
  case "$key" in
    TL) hay=$FLAT_TL ;; RC) hay=$FLAT_RC ;; MG) hay=$FLAT_MG ;; SP) hay=$FLAT_SP ;;
    *) bad "unknown claim key '$key'"; continue ;;
  esac
  name=$(skill "$(file_of "$key")")
  if printf '%s' "$hay" | grep -qF -- "$claim"; then
    ok "$name carries the whole claim: ${claim:0:70}"
  else
    bad "$name lacks the whole claim: $claim"
  fi
done <<'CLAIMS'
TL|N ≥ 2 lanes build concurrently in isolated worktrees, each with its own gates and reviewers, and land through exactly one merge door, one arc at a time (C-HE-01 §1).
TL|N is a dial, not a constant (C-HE-01 §2).
TL|The recipe below walks two lanes, A and B, because the serial rule is pairwise: a third lane waits behind B exactly as B waits behind A.
TL|Throughput: well under N×; merges serialize; trailing lanes re-gate on head change — **prior, not measurement** until AC#10 (C-HE-28) produces a baseline.
TL|"Four lanes, four times the arcs" is exactly the claim this forbids; nothing measured supports it yet.
RC|One turn of this loop is one lane's arc.
RC|N ≥ 2 lanes build concurrently in isolated worktrees, each with its own gates and reviewers, and land through exactly one merge door, one arc at a time (C-HE-01 §1); N is a dial (§2).
RC|The step-2 reservation and disjointness gate are what let a lane run beside its siblings.
RC|Throughput: well under N×; merges serialize; trailing lanes re-gate on head change — **prior, not measurement** until AC#10 (C-HE-28) produces a baseline.
MG|**Every ten rounds is a recorded-decision checkpoint, not a cap** (period set by operator decision, 2026-08-01; recast under C-HE-21 §1, v1.5 X5, ratified 2026-08-25): an eleventh substantive disagreement stops automatic fix-and-re-gate until a recorded decision continues or holds.
MG|Continuation is unbounded — the next checkpoint falls ten rounds later — and the loop never grants its own.
MG|Both failure shapes are real: without the checkpoint, auto-fix-and-re-gate is an infinite loop in autonomous mode; with a cap, review is shortened exactly when it is still paying.
MG|Invariants bind by live carriage (C-HE-21 §2), not by an appeal to their number.
MG|- **#5 is live** (no verdict inferred from absence) in this skill's `## Parsing — fail closed` and in `ship-pr`'s `## Pre-merge gate — CI green + decorrelated 3-lens review (before the merge door)`.
MG|- **#14 is C-HE-19**: CANCELLED is INCOMPLETE, never green — carried by `ship-pr`'s post-merge CI check and by `tools/merge_door.py`.
MG|- **invariant #16 is void**: C-HE-21 §2 found no concurrent-reviewer-cap carrier in `.claude/`, `tools/`, `justfile` or CLAUDE.md. It throttles neither lenses nor lanes.
MG|A later appeal to a numbered invariant cites its live carrier the same way, or it does not bind.
MG|No flat round cap anywhere (C-HE-21 §1): the checkpoint in the gate outcome above punctuates review and never shortens it.
MG|No eval-harness / model-judge as a governance gate (C-HE-21 §4).
MG|- **K5 —** structured findings require location, observed evidence, expected contract and a reproduction basis (the C-HE-24 shape); admissible alternatives are optional, not mandated.
MG|- **K6 —** dropped: a reviewer never acquires authority to suppress its own finding by self-classifying its scope. A lens may record scope metadata; suppression belongs to a second decorrelated lens, a deterministic rule, or a logged operator override, and every suppression leaves an audit row. Ambiguous scope blocks.
MG|- **K7 —** routing by arc type and finding class is deferred until their predictiveness is measured (C-HE-26 §3); shadow mode only, if run at all.
MG|- **K8 —** a blocking post-edit hook is admitted only for fast, deterministic, low-false-positive checks at a stable boundary (C-HE-31 §3), not on every intermediate edit.
SP|automatic fix-and-re-gate pauses at a recorded-decision checkpoint every ten rounds — a checkpoint, never a cap (C-HE-21 §1): an eleventh substantive disagreement is the decision point surfaced to the operator via one `AskUserQuestion`, and its recorded answer continues review (unbounded) or holds it
SP|These are refusals, not gaps. Each will look like a speed fix at the moment an arc is dragging, and each was priced and rejected on evidence:
SP|- **No auto-stopping round cap**, and no shortening of review generically. The merge-gate ten-round checkpoint is a recorded decision to continue or hold, not a stop (C-HE-21 §1).
SP|- **No best-of-N** / parallel variant generation as a speed fix — a measured null result at this model's temperature.
SP|- **No fast mode for throughput** — 6× the price for 2.5× the throughput, and it would disturb the 98.0% cache-read the token economics rest on.
SP|- **No agent framework** for mechanization (CLAUDE.md §3.2 framework-pull discipline).
SP|- **No collapsing of review layers** — 93.4% of 679 findings across 146 PRs were single-tool catches, and merge-gate blocked 46% of 141 gated PRs.
CLAIMS
# Boundedness marker: a truncated or mis-parsed claim list must fail loud, not pass on fewer checks.
if [ "$seen" -eq "$EXPECTED_CLAIMS" ]; then
  ok "claim list is bounded at $EXPECTED_CLAIMS claims"
else
  bad "claim list yielded $seen claims, want $EXPECTED_CLAIMS"
fi

# --- 2. Live-carrier headings and the ship-pr #14 carrier --------------------------------
has_line "$MG" "cited for #5" '## Parsing — fail closed'
has_line "$SP" "cited for #5" \
  '## Pre-merge gate — CI green + decorrelated 3-lens review (before the merge door)'
has_line "$SP" "for C-HE-34" '## Non-goals (C-HE-34)'
if grep -qF -- 'INCOMPLETE, never green (C-HE-19)' "$SP"; then
  ok "ship-pr carries the live #14 carrier (CANCELLED is INCOMPLETE)"
else
  bad "ship-pr: the live #14 carrier 'INCOMPLETE, never green (C-HE-19)' is missing"
fi

# --- 3. C-HE-01: no N=2 literal cap in the lane-model carriers ---------------------------
for f in "$TL" "$RC"; do
  # grep exit 1 = no match; exit >= 2 = the scan did not run, which must never read as clean.
  two=$(grep -nw 'TWO' "$f"); r1=$?
  neq=$(grep -nE '(^|[^0-9A-Za-z])N ?= ?2([^0-9]|$)' "$f"); r2=$?
  if [ "$r1" -gt 1 ] || [ "$r2" -gt 1 ]; then
    bad "$(skill "$f"): N=2 scan could not run (grep exit $r1/$r2)"
  elif [ -n "$two$neq" ]; then
    bad "$(skill "$f") states an N=2 literal cap: $(printf '%s %s' "$two" "$neq" | cut -c1-160)"
  else
    ok "$(skill "$f") states no N=2 literal cap"
  fi
done

# --- 4. C-HE-14: the rejected/blocked table, byte-exact from the spec --------------------
has_line "$TL" "for C-HE-14" '## Rejected and blocked mechanisms (C-HE-14)'
rows=$(awk '/^## C-HE-14 /{f=1; next} f && /^## /{exit} f && /^\| /' "$SPEC" | tail -n +2)
n=$(printf '%s\n' "$rows" | grep -c '^| ')
# Boundedness marker: a moved anchor must fail loud, not shrink the slice to a vacuous pass.
if [ "$n" -eq 11 ]; then
  ok "spec C-HE-14 slice is bounded at 11 rows"
else
  bad "spec C-HE-14 slice yielded $n rows, want 11 (anchor moved?)"
fi
missing=0
while IFS= read -r row; do
  [ -n "$row" ] || continue
  if ! grep -qxF -- "$row" "$TL"; then
    bad "two-lane lacks a C-HE-14 row byte-exact: ${row:0:70}"
    missing=$((missing+1))
  fi
done <<< "$rows"
[ "$missing" -eq 0 ] && ok "two-lane carries every C-HE-14 row byte-exact"

# --- 5. §8 AC#7: no numeric round cap in any loop skill ----------------------------------
NUM='([0-9]+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|twenty)'
CAP='(^|[^a-z])(max|maximum|cap|capped|ceiling|limit|limited)'
# Three shapes: "cap ... rounds ... ten", "capped at ten rounds", and number-first
# "a ten-round limit" (the last added after U-HE-39's witness lens, round 1).
hits=$(grep -EinH -- "${CAP}[^.]{0,20}rounds?[^.]{0,10}[^a-z]${NUM}([^a-z]|$)|${CAP}[^.]{0,40}[^a-z]${NUM} (review |fix )?rounds?([^a-z]|$)|(^|[^a-z])${NUM}[- ]rounds?[- ](max|maximum|cap|ceiling|limit|threshold)([^a-z]|$)" \
  "$MG" "$SP" "$RC" "$TL"); rc=$?
if [ "$rc" -gt 1 ]; then
  bad "AC#7: round-cap scan could not run (grep exit $rc)"
elif [ -z "$hits" ]; then
  ok "AC#7: no numeric round cap in the loop skills"
else
  bad "AC#7: numeric round cap found:"
  printf '%s\n' "$hits" | cut -c1-200 | sed 's/^/      /'
fi

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

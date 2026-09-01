#!/usr/bin/env bash
# Grep witness for U-SR-06 (charter WR-13) — the advisor() reconciliation, decision #1
# RATIFIED 2026-08-26 as the REWRITE arm. `advisor()` was never provisioned in any venue
# (0 calls, 65 prose mentions — [B] §3 item 1); a discipline that cannot be followed
# trains the agent to skip disciplines. Acceptance: ZERO governance carriers name the
# phantom instrument, and the review discipline itself SURVIVES the rename (the
# regression shape is deleting the discipline instead of renaming the instrument).
#
# Scope = live instruction carriers only. Deliberately EXCLUDED, with reasons:
#   - .claude/skills/optimize-claude-md/evals/** — frozen eval fixtures + their
#     assertions form a closed specimen world, not live instructions;
#   - Project_Roadmap_v1.md ledger rows / design-substrate/** change-notes /
#     .harness/** filings — historical records; rewriting them would falsify history
#     (the roadmap's live §5-schema field semantics WERE conformed; its recorded
#     entry rows keep the token as record).
# Doc-text assertions run against the REAL repo files resolved from SCRIPT_DIR.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/../.."

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

# ── Negative half: the phantom token is gone from every live instruction carrier ──
# Explicit file enumeration (the sibling-witness convention) so a historical record
# can never be dragged into scope by a recursive default.
CARRIERS=(
  "$ROOT/CLAUDE.md"
  "$ROOT/justfile"
  "$ROOT/docs/governance/orchestration.md"
  "$ROOT/docs/governance/design-phase-principles.md"
  "$ROOT/.claude/skills/roadmap-continue/SKILL.md"
  "$ROOT/.claude/skills/merge-gate/SKILL.md"
  "$ROOT/.claude/skills/resolve/SKILL.md"
  "$ROOT/.claude/skills/self-heal/SKILL.md"
  "$ROOT/.claude/skills/fan-out/SKILL.md"
  "$ROOT/.claude/skills/optimize-claude-md/SKILL.md"
  "$ROOT/.claude/skills/optimize-claude-md/references/load-bearing.md"
  "$ROOT/.claude/skills/council/council-orchestrator/SKILL.md"
  "$ROOT/.claude/skills/council/workflows/COUNCIL-WORKFLOW.md"
  "$ROOT/.claude/skills/council/workflows/council-workflow.harness-aware.yaml"
  "$ROOT/.claude/workflows/council-workflow.generic.yaml"
  "$ROOT/.claude/commands/council-workflow.md"
  "$ROOT/.claude/commands/council-generic.md"
  # The council commands say "follow it exactly" of the .harness/council ROOT
  # canonicals — a second live home for the same workflow (codex r1 P1). Session
  # archives under .harness/council/*/ stay historical and excluded.
  "$ROOT/.harness/council/COUNCIL-WORKFLOW.md"
  "$ROOT/.harness/council/council-workflow.harness-aware.yaml"
  "$ROOT/.harness/council/council-workflow.generic.yaml"
  # Codex-venue ROOT authorities (codex r2): the venue's own reviewer-routing
  # contract lives here, not only in the .agents bridges.
  "$ROOT/AGENTS.md"
  "$ROOT/.codex/notes/claude-codex-parity.md"
  # Startup routing inventories (codex r7): AGENTS.md directs sessions through
  # these routers, so their mechanism menus are live carriers too.
  "$ROOT/CONTEXT.md"
  "$ROOT/docs/governance/README.md"
)
# The Codex-venue bridge skills carry the same discipline translated; the venue
# exposes no advisor tool either, so they are carriers at the identical bar.
for bridge in "$ROOT"/.agents/skills/*/SKILL.md; do
  CARRIERS+=("$bridge")
done

for f in "${CARRIERS[@]}"; do
  [ -f "$f" ] || { echo "FATAL: missing carrier $f"; exit 1; }
done

# Two needles. 'advisor(' catches every CALL-form — advisor() and argument
# shapes like advisor(transcript-aware) (codex r1 P1: the bare token missed the
# argument form). The BARE word catches operational reviewer identities
# ("advisor = transcript-aware guardrail check" — codex r6): the standalone
# word with no letter/underscore/hyphen/paren on either side, which spares
# "advisory", joined labels (codex-advisor, advisor-eval, advisor_required),
# and [[advisor-...]] memory slugs — proper nouns, not instrument claims.
CLEAN=1
for f in "${CARRIERS[@]}"; do
  if grep -qF 'advisor(' "$f"; then
    bad "phantom instrument call-form named at ${f#"$ROOT"/}"
    CLEAN=0
  fi
  if grep -Eq '(^|[^A-Za-z_-])advisor([^A-Za-z_(-]|$)' "$f"; then
    bad "bare advisor reviewer identity named at ${f#"$ROOT"/}"
    CLEAN=0
  fi
done
[ "$CLEAN" -eq 1 ] && ok "zero live carriers name a phantom advisor call-form or bare identity (${#CARRIERS[@]} files swept)"

# No command frontmatter may GRANT the phantom as a tool: an allowed-tools list
# containing a bare 'advisor' entry is the strongest phantom-instrument shape —
# a capability grant for a tool no venue exposes (codex r1 P1).
GRANTS=0
for f in "$ROOT"/.claude/commands/*.md; do
  if grep -E '^allowed-tools:' "$f" | grep -qE '(:|,)[[:space:]]*advisor([[:space:]]*(,|$))'; then
    bad "allowed-tools grants the phantom advisor tool at ${f#"$ROOT"/}"
    GRANTS=1
  fi
done
[ "$GRANTS" -eq 0 ] && ok "no command frontmatter grants an advisor tool"

# ── Positive half: the discipline survived — renamed, not deleted ──
# The unit's four named carriers + the relocated §13.2 matrix must carry the
# replacement instrument (fresh-context Agent reviewer on a session brief).
needs() { # $1 = file, $2 = label, $3 = needle
  local norm; norm=$(tr '\n' ' ' < "$1" | tr -s ' ')
  if printf '%s' "$norm" | grep -qF -- "$3"; then ok "$2 carries the replacement discipline"; else bad "$2 missing: $3"; fi
}
needs "$ROOT/CLAUDE.md"                                    "CLAUDE.md §13.1 row"        'Transcript-brief review at decision-forks + pre-done'
needs "$ROOT/.claude/skills/roadmap-continue/SKILL.md"     "roadmap-continue step 3"    'Run the §13.1 transcript-brief review'
needs "$ROOT/.claude/skills/merge-gate/SKILL.md"           "merge-gate honesty caveat"  'transcript-brief review (the §13.1 transcript-aware half)'
needs "$ROOT/.claude/skills/resolve/SKILL.md"              "resolve reviewer step"      'spawn a fresh-context Agent reviewer with a written brief of the session'
needs "$ROOT/docs/governance/orchestration.md"             "orchestration §13.2 matrix" 'Transcript-brief review** (Agent subagent)'
# codex r2: the canonical council workflow the /council-generic command follows
# "exactly" must itself carry the replacement mechanism — the call-form needle
# cannot prove a migration, only the absence of the old name. Pinned at BOTH
# operational sites the finding named (a loose one-mention needle survived a
# routing-rule regression in the mutation probe): the no-tension routing rule
# and the E3 reviewer role.
needs "$ROOT/.harness/council/council-workflow.generic.yaml" "canonical generic yaml routing rule" 'voice plus a transcript-brief review'
# The E3 pin is the block's UNIQUE structural key, not role prose — the role
# phrase also appears in the routing rule above, so a prose needle stays green
# when the E3 hunk alone reverts to the bare advisor schema (codex r3).
needs "$ROOT/.harness/council/council-workflow.generic.yaml" "canonical generic yaml E3 reviewer key" 'transcript_brief_reviewer:'
# The on_fail ROUTE is its own degree of freedom (codex r4): the bare
# identifier route_single_voice_plus_advisor is neither a call-form (negative
# sweep blind) nor adjacent to any pinned prose. Pin the exact key: value in
# ALL FOUR live workflow yamls — canonical pair and .claude twins.
for yml in \
  "$ROOT/.harness/council/council-workflow.generic.yaml" \
  "$ROOT/.harness/council/council-workflow.harness-aware.yaml" \
  "$ROOT/.claude/workflows/council-workflow.generic.yaml" \
  "$ROOT/.claude/skills/council/workflows/council-workflow.harness-aware.yaml"; do
  needs "$yml" "on_fail route in ${yml##*/} (${yml#"$ROOT"/})" 'on_fail: route_single_voice_plus_brief_review'
done
# codex r2: the Codex venue's second reviewer must be ISOLATED — the exact
# self-review shape the bridge rewrite forbids, pinned at both root authorities.
needs "$ROOT/AGENTS.md"                                    "AGENTS.md reviewer contract" 'never the interactive controller reviewing its own work'
needs "$ROOT/.codex/notes/claude-codex-parity.md"          "codex parity note"          'never the interactive controller reviewing its own work'
# codex r5: the COUNCIL-WORKFLOW prose companion's E3 wiring designated a bare
# "advisor" reviewer identity — pin the migrated role at BOTH live homes.
needs "$ROOT/.claude/skills/council/workflows/COUNCIL-WORKFLOW.md" "council prose E3 (.claude home)"  'the transcript-brief reviewer (in-family'
needs "$ROOT/.harness/council/COUNCIL-WORKFLOW.md"                 "council prose E3 (.harness home)" 'the transcript-brief reviewer (in-family'
# codex r5: Project_Roadmap_v1.md is excluded from the negative sweep for its
# HISTORICAL entry rows only — its LIVE checkpoint-on-pause protocol banked an
# "advisor pass" as satisfiable; pin the migrated banking clause.
needs "$ROOT/Project_Roadmap_v1.md" "roadmap checkpoint-on-pause banking clause" 'if the transcript-brief review is banked'
# codex r8: skills whose flow CONSUMES the second vote at decision time
# (resolve compares votes; optimize-claude-md needs both reviewers' acceptance)
# cannot use the deferred-routing fallback — their bridges must carry the
# fork-defers-not-the-review exception.
needs "$ROOT/.agents/skills/resolve/SKILL.md"            "resolve bridge decision-time exception"  'DECISION-TIME EXCEPTION'
needs "$ROOT/.agents/skills/optimize-claude-md/SKILL.md" "optimize bridge decision-time exception" 'DECISION-TIME EXCEPTION'

# ── Pairing control: both §13.1 halves still stand in the SAME carrier ──
# The rename must not decouple the transcript-aware half from the out-of-family
# artifact half (the R-600 division of labor).
if grep -qF 'transcript-brief' "$ROOT/CLAUDE.md" && grep -qF 'just codex-review' "$ROOT/CLAUDE.md"; then
  ok "CLAUDE.md still pairs the transcript-aware half with the codex-review artifact half"
else
  bad "CLAUDE.md decouples the two §13.1 review halves"
fi

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

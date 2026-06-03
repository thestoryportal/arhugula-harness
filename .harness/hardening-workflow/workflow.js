export const meta = {
  name: 'harden-loop-hil',
  description: 'Audit the U-HK autonomous-loop/HIL automation against its intent + this session\'s lapses; produce a capability-verified HARDENING_PLAN.md that makes each manual discipline self-enforcing.',
  whenToUse: 'Operator prompts "begin workflow" / "/begin-workflow" in a fresh session after the hardening-workflow context package is on main.',
  phases: [
    { title: 'Audit', detail: 'one agent per discipline: AUTO-vs-MANUAL + lapse evidence + proposed enforcement' },
    { title: 'Verify', detail: 'adversarial partner refutes each proposal against real hook capabilities' },
    { title: 'Synthesize', detail: 'fold surviving proposals into HARDENING_PLAN.md (barrier)' },
    { title: 'Critic', detail: 'completeness + capability-soundness pass over the plan' },
  ],
}

// ---------------------------------------------------------------------------
// Context package (read by every agent). Paths are relative to the repo root;
// run the fresh session from the MAIN checkout (/Users/robertrhu/Projects/arhugula-v2).
// ---------------------------------------------------------------------------
const PKG = '.harness/hardening-workflow'
const READ_FIRST = [
  `${PKG}/BRIEF.md`,
  `${PKG}/inventory-hooks-skills-disciplines.md`,
  `${PKG}/session-evidence.md`,
  `${PKG}/references/claude-code-hooks.md`,
  `${PKG}/references/insights-report-2026-06-03.md`,
].join(', ')

const CONSTRAINTS = `HARD CONSTRAINTS (from BRIEF.md §5):
- This workflow hardens the U-HK loop/HIL PROCESS machinery ONLY. NEVER touch design-substrate/**, H_T harness-*/src product code, or the H_T R-NNN roadmap.
- Every hook-capability claim MUST trace to ${PKG}/references/claude-code-hooks.md (real event + real control output: can it block? allow/deny? inject context? auto-approve?). Do NOT invent a hook event or an output an event does not support.
- NEVER weaken a safety guard. The permission-guard deny-list (paid LLM calls, secret/.env relocation, destructive git) is locked. Hardening = ADD enforcement, not loosen blast radius.
- Preserve the corrected rules: never-halt-unless-zero-units; defer-and-continue at a gate (tools/loop/defer.sh + advance); loop-mode-creds-available -> PROCEED (incl. paid calls); prefer the FREE local ollama daemon where it serves.
- Cite file:line or CLAUDE.md §section for every claim about what currently exists. The inventory + session-evidence are the source of truth for "what exists" and "what lapsed".`

const PREAMBLE = `You are one agent in the "harden-loop-hil" dynamic workflow. FIRST read these context files in full (they ARE your context — do not hunt elsewhere first): ${READ_FIRST}. Then do your task. Your final message IS your structured return value (no human is reading it directly).\n\n${CONSTRAINTS}`

// ---------------------------------------------------------------------------
// The disciplines to audit (the U-HK loop's intended behaviors). Each is a
// rule the loop is SUPPOSED to follow; most are MANUAL (Claude-recall) today.
// ids match session-evidence.md (D1..D13).
// ---------------------------------------------------------------------------
const DISCIPLINES = [
  { id: 'D1', title: 'codex-review as the default pre-merge out-of-family reviewer (CLAUDE.md §13.1/§13.2)', note: 'SKIPPED on both merged PRs this session (timed out 2x, then skipped). RECURRING across 201 sessions per insights-report (stalled 12+ min, used WRONG MODEL gpt-5.4 via a profile override shadowing the model flag, never returned a verdict). Design the enforcement to: (a) a PreToolUse deny on `gh pr merge` until a per-branch codex-review-passed marker exists; (b) ECHO/verify the resolved model+config before launch (guard the profile-override-shadows-flag bug); (c) an explicit timeout; (d) DIFF-SCOPE codex so it is fast enough to actually run (the monorepo-exploration is the adoption blocker); (e) a defined kill-and-proceed-with-noted-caveat fallback so a stall does not silently skip the review entirely.' },
  { id: 'D2', title: 'advisor() at every decision-fork + pre-done (CLAUDE.md §13.1)', note: 'Called ONCE this session, not per-fork/pre-done. Can a hook detect a "decision-fork" or a "declaring done" Stop and nudge/limit?' },
  { id: 'D3', title: '/resolve (Codex+advisor dual-reviewer) for reversible in-repo forks in loop mode (skills/resolve, U-HK-13)', note: 'NEVER invoked this session; forks decided solo.' },
  { id: 'D4', title: 'never-halt-unless-zero-units (CLAUDE.md §12.4.1 + the loop)', note: 'Violated: treated a single deferred item as a stop point. stop-loop.sh (U-HK-14) is the enforcement surface — does it actually prevent a premature halt in an interactive /loop-start session (vs only headless run.sh)?' },
  { id: 'D5', title: 'defer-and-continue at a gate (tools/loop/defer.sh + advance; U-HK-14/15)', note: 'Loop must build the un-gated slice, defer the gate, and advance — not stop. Was the operator-corrected rule; is it enforced or only documented in the skill?' },
  { id: 'D6', title: 'loop-mode paid-call rule: creds available -> PROCEED (incl. paid calls); missing dep -> defer + continue', note: 'Violated: deferred a runnable paid e2e instead of proceeding. The permission-guard currently HARD-DENIES paid LLM calls even in loop mode (deny-list) — that CONTRADICTS the operator-corrected rule. Reconcile: how should the guard distinguish an authorized loop-mode paid run from an unauthorized one WITHOUT loosening blast radius? (This is the subtlest item — get it right; do not just remove the deny.)' },
  { id: 'D7', title: 'autonomous git/worktree + cwd-safe hygiene (the loop manages exiting/pruning/opening/creating worktrees & branches itself)', note: 'FAILED hardest: the cwd-split (`cd <main> && git ...` while edits live in the worktree) caused 2 Bash failures, a wrong-checkout branch, a failed commit, tangled branches; the misnamed u-hk-01-hook-lib worktree was reused. U-HK-26 GCs merged worktrees at SessionStart but nothing guards mid-loop cwd-split or per-arc worktree lifecycle. Design the autonomous-hygiene + cwd-safety enforcement (e.g. a PostToolUse(Bash) guard rejecting `cd <repo-root> && git` cwd-split patterns; per-arc worktree create/exit).' },
  { id: 'D8', title: 'CLAUDE.md §12.2 + §12.2.1 post-merge fixed-point dashboard refresh', note: 'Done by hand this session (correctly). post-merge-refresh.sh (U-HK-29) is ADVISORY only. Can the terminating-refresh be more auto-enforced, or at least gated so a substantive merge cannot be left without its owed refresh?' },
  { id: 'D9', title: 'CLAUDE.md §12.1 session-start hash audit + §12.2.1 lag carve-out', note: 'AUTO via session-start.sh — mostly works. Audit for edge cases (multi-PR-between-audits, worktree vs main HEAD drift the cwd-split can introduce).' },
  { id: 'D10', title: 'posture check (CLAUDE.md §11: design-phase vs Phase-7 vs mode-agnostic)', note: 'MANUAL. Could a PreToolUse/edit-scope hook detect a mixed-posture edit set and warn/deny?' },
  { id: 'D11', title: 'memory hygiene (CLAUDE.md §12.5): save patterns at cardinality>=2, save feedback symmetrically, MEMORY.md 24,400-byte cap, verify-before-acting', note: 'MANUAL. The capture-failure hook nudges on recurrence; is the broader memory discipline enforceable, and is the MEMORY.md cap auto-guarded? (It is currently OVER cap.)' },
  { id: 'D12', title: 'completeness-check-by-execution before claiming "sufficient"/"done" (CLAUDE.md §13.1)', note: 'MANUAL. Run the path/e2e, not just unit tests. Can a Stop hook ask "did you verify by execution?"' },
  { id: 'D13', title: 'empirical cite-grounding + cross-spec drift grep (CLAUDE.md §13.1/§10.4)', note: 'MANUAL. Likely stays manual, but assess.' },
  { id: 'D14', title: 'output-token-limit resilience / loop durability (insights-report; CLAUDE.md §14.4/§14.5)', note: 'NEW from the insights report: 6+ autonomous-loop sessions were LOST to repeated output-token-limit errors (responses exceeding the cap → context summarized away → work unrecoverable). The hardened loop must survive truncation: bias toward concise responses + FREQUENT durable per-step file checkpoints (the U-HK-05/27 checkpoint substrate exists — is it triggered often enough mid-loop? does the loop write per-step progress to a file?); §14.5 chunk large writes. Assess whether capture-failure (U-HK-07, StopFailure) recovers from a mid-loop output-cap truncation. Likely the single most impactful durability fix for UNATTENDED runs.' },
]

// ---------------------------------------------------------------------------
// Prompt builders.
// ---------------------------------------------------------------------------
function auditPrompt(d) {
  return `${PREAMBLE}

TASK — audit discipline ${d.id}: ${d.title}
Session-specific note: ${d.note}

Produce a tight, cited analysis with these sections:
1. CURRENT STATE — is this AUTO (hook-enforced) or MANUAL (Claude-recall / skill-invoked)? Cite the exact mechanism (hook script file:line, skill, or CLAUDE.md §) from the inventory.
2. LAPSE EVIDENCE — did it fail/lapse this session? Cite session-evidence.md. If it held, say so.
3. ENFORCEABILITY — CAN it be moved to AUTOMATIC (hook-enforced) given references/claude-code-hooks.md? Name the EXACT hook event(s) and the EXACT control output (deny / block / inject additionalContext / permissionDecision allow|deny|ask) that would do it. If it genuinely cannot be hook-enforced (needs judgment), say why and propose the strongest skill-side / convention strengthening instead.
4. PROPOSAL — the concrete change: which file (existing hook to extend, or new hook script + settings.json wiring, or skill edit), the matcher, the check logic in plain steps, and the failure-handling (fail-open vs fail-closed). Note false-positive risk + how the proposal avoids it. For D6 specifically: do NOT propose removing the paid-call deny — propose how to distinguish an authorized loop-mode paid run (and surface the reconciliation question if it needs an operator decision).
5. LEVERAGE & RISK — how many of this session's lapses it would have prevented; implementation risk (low/medium/high) + why.

Be specific and buildable. This feeds an adversarial verifier next, then a synthesis into HARDENING_PLAN.md.`
}

function verifyPrompt(d, proposal) {
  return `${PREAMBLE}

TASK — adversarially verify the proposal below for discipline ${d.id}: ${d.title}. Your job is to REFUTE it where it is wrong; default to skepticism.

PROPOSAL UNDER REVIEW:
${proposal}

Check, citing references/claude-code-hooks.md:
1. CAPABILITY — does the proposed hook event actually exist, fire when claimed, and support the claimed control output? (e.g. PermissionRequest does NOT fire in headless -p; a Stop hook that blocks gets overridden after 8 consecutive blocks; PreToolUse "allow" cannot loosen deny rules; exit-2 vs JSON output are mutually exclusive.) Flag any capability the proposal assumes that the reference does not support.
2. SAFETY — does it weaken any locked guard (paid-call/secret/destructive-git deny-list)? Does it create a new blast-radius hole? For D6, is the reconciliation sound (authorized-paid distinguished WITHOUT a blanket loosening)?
3. NEW FAILURE MODES — false positives that would train the operator to ignore it; infinite-loop / runaway risk (Stop-continue, subagent re-trigger); cwd/worktree assumptions that break under the very split that caused this session's failures; performance (per-prompt / per-tool latency).
4. CORRECTNESS vs the preserved rules — does it respect never-halt, defer-and-continue, creds-available-proceed?
5. VERDICT — SOUND / SOUND-WITH-FIXES / REJECT, with the specific fixes or the refutation. If SOUND-WITH-FIXES, restate the corrected proposal crisply.

Return your full critique + the verdict + (if salvageable) the corrected, capability-verified proposal. The synthesis step will use your verified version, not the raw proposal.`
}

// ---------------------------------------------------------------------------
// Execution.
// ---------------------------------------------------------------------------
log(`Hardening workflow: auditing ${DISCIPLINES.length} disciplines (audit -> adversarial verify), then synthesis + completeness critic.`)

// Phase 1+2 as a pipeline (no barrier): each discipline is audited then
// adversarially verified independently; a fast discipline verifies while a
// slow one is still being audited.
const verified = await pipeline(
  DISCIPLINES,
  (d) => agent(auditPrompt(d), { label: `audit:${d.id}`, phase: 'Audit' }),
  (proposal, d) => agent(verifyPrompt(d, proposal), { label: `verify:${d.id}`, phase: 'Verify' }),
)

const verifiedBlocks = DISCIPLINES.map((d, i) => {
  const v = verified[i]
  return `=== ${d.id}: ${d.title} ===\n${v == null ? '(no verified output — agent skipped/errored; treat as UNADDRESSED)' : v}`
}).join('\n\n')

// Phase 3 — synthesis (barrier: needs ALL verified proposals to dedup + prioritize).
phase('Synthesize')
const plan = await agent(
  `${PREAMBLE}

TASK — SYNTHESIZE the definitive hardening plan and WRITE it to ${PKG}/HARDENING_PLAN.md.

You have the adversarially-verified per-discipline analyses below. Fold them into ONE prioritized, buildable plan. Do NOT just concatenate — dedup overlapping proposals (e.g. several disciplines may want the same Stop-hook or the same per-arc marker), resolve contradictions, and order by leverage × inverse risk.

Write ${PKG}/HARDENING_PLAN.md with these sections:
1. EXECUTIVE SUMMARY — the core gap (manual-vs-automatic enforcement) and the shape of the fix in 5-8 sentences.
2. PER-DISCIPLINE DISPOSITIONS — a table: discipline (D1..D13) | current (AUTO/MANUAL) | lapsed this session? | disposition (HOOK-ENFORCE / SKILL-STRENGTHEN / LEAVE-MANUAL-justified) | the concrete change (file + hook event + check) | leverage | risk.
3. NEW / CHANGED HOOKS — for each hook to add or extend: file path, hook event + matcher + settings.json wiring, the check logic (plain steps), fail-open vs fail-closed, and the capability citation (which reference section proves it's possible).
4. THE D6 RECONCILIATION — the paid-call-in-loop-mode design: exactly how the permission-guard distinguishes an authorized loop-mode paid run from an unauthorized one WITHOUT loosening the deny-list, OR a crisp operator decision question if it needs one. This is the subtlest item — be precise.
5. THE D7 GIT/WORKTREE/CWD AUTONOMY DESIGN — how the loop manages worktree/branch lifecycle autonomously and prevents the cwd-split failure class (concrete guard + convention).
6. NEVER-HALT / DEFER-AND-CONTINUE CORRECTNESS — confirm tools/loop/run.sh + stop-loop.sh actually implement never-halt-unless-zero-units in BOTH headless and interactive /loop-start modes; note any gap.
7. IMPLEMENTATION SEQUENCE — ordered: high-leverage/low-risk first; what needs an operator decision before building; what's a second-pass.
8. OPEN QUESTIONS / OPERATOR DECISIONS — anything that needs a ratification before implementation.

Cite throughout. Keep it definitive and buildable — this is the deliverable a follow-up pass (or the operator) implements. After writing the file, return a 10-line summary of what you wrote + the count of HOOK-ENFORCE vs SKILL-STRENGTHEN vs LEAVE-MANUAL dispositions.

VERIFIED PER-DISCIPLINE ANALYSES:
${verifiedBlocks}`,
  { label: 'synthesize-plan', phase: 'Synthesize' },
)

// Phase 4 — completeness critic.
phase('Critic')
const critique = await agent(
  `${PREAMBLE}

TASK — completeness + capability-soundness critic over the hardening plan just written at ${PKG}/HARDENING_PLAN.md. Read that file.

Ask and answer:
1. COVERAGE — is every discipline D1..D13 dispositioned? Is any session lapse (session-evidence.md) left without a preventive measure? Is any MANUAL discipline in the inventory that lapsed left un-considered?
2. CAPABILITY SOUNDNESS — re-check EVERY proposed hook against references/claude-code-hooks.md. Flag any that assumes a non-existent event, a wrong control output, or a headless-mode limitation (PermissionRequest absent in -p; Stop 8-block override cap; deny>ask>allow precedence).
3. SAFETY — does any proposal loosen the locked deny-list or open a blast-radius hole? Is the D6 paid-call reconciliation actually safe?
4. CONTRADICTIONS — any two proposals that conflict (e.g. a Stop-block that fights the never-halt continuation)?
5. MISSING — what's the single most important thing the plan still doesn't address?

If you find material gaps, APPEND a "## Critic addendum" section to ${PKG}/HARDENING_PLAN.md with the corrections (do not rewrite the body). Return a verdict: PLAN-SOUND or PLAN-NEEDS-REVISION + the top 3 issues.`,
  { label: 'completeness-critic', phase: 'Critic' },
)

log('Hardening workflow complete. Deliverable: .harness/hardening-workflow/HARDENING_PLAN.md')
return {
  deliverable: `${PKG}/HARDENING_PLAN.md`,
  disciplines_audited: DISCIPLINES.length,
  verified_nonnull: verified.filter(Boolean).length,
  critic_verdict_tail: typeof critique === 'string' ? critique.slice(-600) : null,
  synthesis_tail: typeof plan === 'string' ? plan.slice(-600) : null,
}

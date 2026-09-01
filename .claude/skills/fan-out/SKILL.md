---
name: fan-out
description: Generate N parallel solution variants from distinct angles, then judge them against a rubric and return a scored winner with rationale. Use when the operator says "/fan-out", "give me N approaches", "explore variants", "tournament this", or wants decorrelated attempts at a wide-open design/impl problem before committing. Spawns parallel variant subagents + a judge. Do NOT use for linear/mechanical work or a problem with one obvious approach — the parallelism is wasted there.
---

# fan-out — parallel variants + judge (U-HK-25)

For a **wide-open** problem (the solution space is genuinely divergent), generate several
independent attempts from distinct angles, then score them — beats one-attempt-iterated when
no single approach is obviously right. Lower-priority autonomy tool; reach for it
deliberately, not by default (most harness work is careful-but-linear, §13.3).

## When it fits / when it does not

- **Fits:** open design choices (a schema shape, an API surface, a refactor strategy), an
  ambiguous spec reading with multiple defensible interpretations, a "which approach" fork
  where the angles are real and distinct.
- **Does NOT fit:** linear/interdependent impl, mechanical edits, a single-fact lookup, or a
  problem with one obvious approach. If you cannot name ≥2 genuinely distinct angles in
  advance, don't fan out — solve it directly (mirrors the §10.9 nameable-tension discriminator).

## The flow

1. **Frame** the problem as a crisp brief + a **scoring rubric** (3–5 weighted criteria —
   e.g. correctness, blast-radius, simplicity, alignment-with-spec). The rubric is what makes
   the judge non-arbitrary; write it first.
2. **Pick N distinct angles** (default N=3): e.g. MVP-first / risk-first / spec-purist, or
   three concrete architectural directions. Each angle must be nameable and different.
3. **Spawn N variant subagents in parallel** — one `Agent` call per angle, **in a single
   message** so they run concurrently. Each gets the same brief but a different angle
   instruction and returns a structured proposal (approach + key decisions + tradeoffs +
   self-assessment against the rubric). Keep each variant's output bounded so it fits one
   return. (For a heavier sweep, the `Workflow` tool's parallel/judge pattern is the
   industrial form — opt-in per its rule; this skill is the lightweight `Agent`-based version.)
4. **Judge.** Spawn one judge subagent (or judge inline) that scores all N proposals against
   the rubric, picks a winner, and **synthesizes** — graft the best ideas from the runners-up
   into the winner rather than taking it whole. The judge returns: per-variant scores, the
   winner, the synthesis, and the rationale.
5. **Chunk the output (§14.5).** N variant proposals + a judge report can exceed the
   output-token cap. Stream to a file in chunks (or summarize each variant to its essentials +
   keep full proposals in a scratch file under `$CLAUDE_JOB_DIR/tmp`), then present the scored
   winner + rationale. Never emit one giant response that truncates.

## Prompt authoring — delegate under `laws:prompt`

**Subagent prompts are authored under `laws:prompt` (U-SR-03, charter WR-08).** A subagent
sees only the prompt you write — no transcript, no CLAUDE.md, no user requirement unless you
put it there. Delegate the authoring to an agent that adopts `laws:prompt` and use the prompt
it returns; composing one inline is legal ONLY when instantiating a skill-canonical template
with literal values. A freehand prompt written in a `laws:code` session is the defect this
rule exists to stop: the passive memory (`[[feedback-subagent-prompts-are-laws-prompt-medium]]`)
failed twice in 48h, and delegating costs ~1m13s / 0.11M IET — about 3% of one lens run. The
`agent-prompt-advisory` PreToolUse hook restates this at every `Agent` call; it is advisory
and never denies. The delegate's OWN invocation is the base case: launching the
laws:prompt authoring agent uses the one-line brief `Adopt laws:prompt and author the
subagent prompt described below; return only the finished prompt.` plus the task
description, and needs no further delegation -- without a named base case the rule
recurses forever, since every authoring agent would itself need an authored prompt.

This skill carries no canonical prompt template — every variant brief is written fresh per
problem, so step 3 is always the delegated path and never the inline exception. Step 4 depends
on which judge you chose: a SPAWNED judge gets a delegated prompt like any other subagent, while
judging INLINE authors no subagent prompt at all and the rule simply does not reach it (codex
u-sr-03 r10 P2 — an earlier draft said "always", which forbade a path step 4 explicitly permits).

## Guardrails

- **Subagent self-validation (U-HK-17).** Variant + judge subagents inherit the SubagentStart
  contract / SubagentStop retry guard — they validate their own output shape.
- **The judge is advisory.** It proposes a winner; the operator (or you, with `advisor()` on
  the synthesis) disposes. A close score-split is itself signal — surface it.
- **No paid/destructive side effects in variants.** Variants explore + propose; they do not
  fire paid calls, relocate secrets, or make irreversible changes
  (`[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`). Implementation
  of the winner happens after, under the normal arc.

## Notes

- Decorrelation by construction: distinct angles surface failure modes a single pass misses —
  the same thesis as the Codex/advisor pairing (§13.1), applied within-family across angles.
- Lower priority than the rest of Wave 3 — use it when the problem is genuinely wide-open.

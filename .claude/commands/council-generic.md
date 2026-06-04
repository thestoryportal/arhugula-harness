---
description: Run the generic (council-skill-agnostic) multi-agent council workflow — same shape/flow as /council-workflow but with the voice roster parameterized for ANY task that has a nameable cross-perspective tension (inside or outside this harness). Use for a wide-open design/decision worth decorrelated multi-voice + adversarial + out-of-family review.
argument-hint: <the task/decision to deliberate> [optionally name the primary + consultant perspectives, or let the command propose them]
allowed-tools: Workflow, Agent, Bash, Read, Write, Edit, advisor
---
Run the **generic council workflow** for this task:

> $ARGUMENTS

**Spec (follow it exactly):** `.harness/council/council-workflow.generic.yaml`
**Prose companion:** `.harness/council/COUNCIL-WORKFLOW.md`

Procedure:
1. **Pre-convene** — apply the nameable-tension gate (no nameable cross-perspective tension → STOP, route to a single voice + `advisor()`). Build the **voice_roster** per the spec: list the distinct perspectives the task spans; assign PRIMARIES (1-3 at the center) vs CONSULTANTS (cross-cutting: security/cost/reliability/observability/eval/UX/…); each voice may be a skill, a role-prompt, or a persona. Name the convening spine-tension. Open a charter + ledger tree.
2. **Run the stages** E1 (A1 primaries-independent → A2 consultants-react → B cross-read DEBATE) → E2 adversarial #1 → E2b reconcile → E3 out-of-family (descriptive primer ONLY) + transcript-aware `advisor()` → E3b reconcile → E4 gate → close. Every voice/reviewer is a **genuine agent invocation** adopting its role; fan out gently in small waves.
3. **Honor the `hil_gates`** — HALT for owner go-ahead before each full-council convening; primaries→consultants→cross-read ordering; decorrelated-reviewer wiring (weight divergence); reconcile-to-zero per gate. ("Without HIL" → autonomous, but stop at destructive/irreversible/outward-facing boundaries.)
4. **Close** — fold residuals; conscious versioned deliverable (vN + change-note); record where completed work is tracked; commit; review/merge per the owner's call.

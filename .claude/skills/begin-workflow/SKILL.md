---
name: begin-workflow
description: >
  Launch the prepared loop/HIL HARDENING dynamic workflow. Use when the operator
  prompts "begin workflow", "/begin-workflow", "start the workflow", "run the
  hardening workflow", or "kick off the workflow" — especially in a fresh session
  after the hardening-workflow context package has been prepared. This is the
  explicit opt-in to multi-agent orchestration: the skill loads the pre-authored
  context brief and launches the pre-authored Workflow script that audits the
  U-HK autonomous-loop/HIL automation and produces HARDENING_PLAN.md. Do NOT use
  for any other workflow or for ordinary roadmap continuation (/roadmap-continue).
---

# begin-workflow — launch the loop/HIL hardening workflow

This skill kicks off the **prepared** dynamic workflow that hardens the autonomous
loop / HIL automation (U-HK-01..29). All context was assembled in a prior session
and committed under `.harness/hardening-workflow/`. Your job here is small and
deterministic: load the brief, then launch the workflow.

## Preconditions (verify, fail loud)

1. You should be running from the **main checkout** (`/Users/robertrhu/Projects/arhugula-v2`),
   not a `.claude/worktrees/` copy. If the package files below are missing, you're
   likely in the wrong checkout or the package PR hasn't merged — say so and stop.
2. Confirm the package exists: `.harness/hardening-workflow/BRIEF.md`,
   `workflow.js`, `inventory-hooks-skills-disciplines.md`, `session-evidence.md`,
   `references/claude-code-hooks.md`.

## Steps

1. **Read the brief** — `Read` `.harness/hardening-workflow/BRIEF.md` in full. It is
   the anchor context (the goal, the manual-vs-automatic enforcement gap, this
   session's ground-truth lapses, the workflow design, the hard constraints, the
   success criteria). You do **not** need to read the other package files yourself —
   the workflow's agents read them — but skim `BRIEF.md` §6 so you know the inputs.

2. **Launch the workflow** — call the **Workflow** tool with:
   ```
   { "scriptPath": ".harness/hardening-workflow/workflow.js" }
   ```
   This is the explicit, operator-requested multi-agent orchestration (the opt-in
   condition for the Workflow tool). It runs in the background; a task notification
   arrives when it completes. The deliverable is
   `.harness/hardening-workflow/HARDENING_PLAN.md`.

3. **While it runs**, do nothing that conflicts (no edits to `tools/hooks/`,
   `tools/loop/`, `.claude/skills/`, or `.harness/hardening-workflow/` until it's
   done — the agents are auditing those). When it completes, read
   `HARDENING_PLAN.md`, relay the executive summary + the critic verdict, and ask
   the operator whether to proceed to an implementation pass (a separate workflow).

## Hard rules (carried into the launch)

- The workflow hardens the **U-HK loop/HIL process machinery ONLY**. It must not
  touch `design-substrate/**`, H_T `harness-*/src` product code, or the H_T R-NNN
  roadmap. (`BRIEF.md` §5.)
- Do **not** re-author the workflow inline — launch the committed `workflow.js` via
  `scriptPath` so it's the reviewed, deterministic version.
- If the operator wants the scope changed before launch, edit `workflow.js` (or the
  brief) first, then launch — don't improvise a different orchestration.

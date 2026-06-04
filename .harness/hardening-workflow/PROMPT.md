# Kickoff prompt — loop/HIL hardening dynamic workflow

> Paste the block below verbatim into a **fresh session**, run from the **main
> checkout** (`/Users/robertrhu/Projects/arhugula-v2`). It triggers the dynamic
> Workflow feature, which authors + runs its own multi-agent assessment from this
> prompt + the context at `.harness/hardening-workflow/`. (Nothing else to set up —
> there is no skill or pre-written script; the context is the input.)

---

Run a dynamic workflow to definitively diagnose and harden our **hook/skill/advisor-based autonomous coding workflow** — the dev-process machinery (the U-HK-01..29 Claude Code hooks + skills + loop runner in `tools/hooks/`, `tools/loop/`, `.claude/skills/`) that we use to build the harness — so the loop reliably self-enforces our engineering disciplines and we can finish building the harness.

**Read first** (the complete, pre-assembled, cited context — do NOT go hunting elsewhere before reading these): `.harness/hardening-workflow/BRIEF.md`, then `inventory-hooks-skills-disciplines.md`, `session-evidence.md`, `references/claude-code-hooks.md`, and `references/insights-report-2026-06-03.md`. Treat them as the ground truth for what exists and what lapsed.

**The problem to solve:** ~14 of the loop's engineering disciplines rely on Claude *remembering* to invoke them (MANUAL); only ~5 are actually hook-enforced (AUTOMATIC). The manual ones lapse — a real session skipped codex-review on both merges, under-used advisor, never used `/resolve`, mishandled a gate (defer-and-halt), and tangled git/worktrees via a cwd-split. Assess WHY each discipline (D1–D14, enumerated in the inventory §D + session-evidence + the insights report) lapses, and which can be moved from MANUAL to AUTOMATIC.

**Produce** a definitive, prioritized **hardening plan** at `.harness/hardening-workflow/HARDENING_PLAN.md`: for each discipline — hook-enforce (with the EXACT hook event + matcher + check + control output), skill-strengthen, or justified leave-manual; plus an ordered implementation sequence (high-leverage / low-risk first) and any operator decisions flagged. The deliverable is the plan, not the implementation.

**Hard constraints:**
- Hardens the **U-HK process machinery ONLY** — do NOT touch `design-substrate/**`, the H_T `harness-*/src` product code, or the H_T (R-NNN) roadmap.
- Every proposed hook MUST be capability-verified against `references/claude-code-hooks.md` (a real event + a real control output it supports). Reject anything that isn't expressible there.
- **Never weaken** the locked safety deny-list (paid LLM calls, secret/`.env` relocation, destructive git). Hardening only ADDS enforcement, never loosens blast radius.
- Preserve the operator-corrected rules: never-halt-unless-zero-units; defer-and-continue at a gate; **loop-mode-creds-available → PROCEED (incl. paid calls)**; prefer the free local ollama where it serves.

**Quality bar:** adversarially verify each proposed fix (refute it against the hook capabilities, the safety guards, and new failure modes — false positives, infinite-loop / Stop-block-8× cap, PermissionRequest-absent-in-`-p` — before keeping it). Give special weight to the four highest-leverage, cross-session-recurring items:
- **D6** — the permission-guard HARD-DENIES paid LLM calls even in loop mode, which **contradicts** the corrected creds-available→proceed rule. Reconcile this WITHOUT loosening the deny-list as the unauthorized-call backstop. This likely needs an operator decision — surface it crisply.
- **D7** — the cwd-split / worktree-hygiene failure class, plus an autonomous per-arc worktree/branch lifecycle (the loop should create/prune/exit worktrees itself and never tangle the working state).
- **D1** — codex-review keeps getting skipped / stalling 12+ min / using the wrong model. Make the gate fast (diff-scoped), enforced (e.g. block `gh pr merge` until a per-branch review marker exists), model-verified, and timeout-bounded with a defined kill-and-proceed-with-caveat fallback.
- **D14** — output-token-limit loop-durability (keep responses concise + frequent durable per-step checkpoints so an unattended run survives truncation).

**Be economical:** structure the workflow for efficient, decorrelated coverage; don't over-spawn agents; keep it token-aware. Decide your own structure — there is no fixed phase list to follow.

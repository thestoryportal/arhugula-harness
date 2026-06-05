# Kickoff prompt — loop/HIL hardening dynamic workflow

> Paste the block below into a **fresh session**, run from the **main checkout**
> (`/Users/robertrhu/Projects/arhugula-v2`). It triggers the dynamic Workflow
> feature, which authors + runs its own multi-agent assessment from this prompt +
> the context at `.harness/hardening-workflow/`. There is no skill or pre-written
> script — the context is the input.

---

Run a dynamic workflow to definitively diagnose and harden our **hook/skill/advisor-based autonomous coding workflow** — the dev-process machinery (the U-HK-01..29 Claude Code hooks + skills + loop runner in `tools/hooks/`, `tools/loop/`, `.claude/skills/`) we use to build the harness — so the loop reliably **self-enforces** our engineering disciplines and we can finish building the harness (H_T).

**Read the context package first** (`.harness/hardening-workflow/` — complete and cited; do NOT go hunting elsewhere before reading it):

- **The authoritative INTENT — the ratified plans, with per-unit acceptance criteria:**
  - `let-s-brainstorm-adding-additional-recursive-taco.md` — the master "Hooks-driven Autonomy + Self-Improvement" plan (Waves 1–3, U-HK-01..25): the **ratified decisions**, the load-bearing architecture, and each unit's **AC** + verification gates. This is what the loop was *supposed* to be.
  - `create-a-very-clear-serialized-wilkes.md` — the Wave 4 plan (U-HK-26..29: cleanup-family + context-recovery closure): the findings→disposition spine, the decision points, and the primary-source hook/StatusLine anchors.
- **The plan-vs-as-built reconciliation:** `hook-advisor-workflow-review.md` — §9 catalogs where the *as-built under-delivered the plan* (findings R-1..R-15: e.g. units PLANNED as enforcing that shipped advisory); §10 the Wave-4 closures.
- **The as-built enforcement map:** `inventory-hooks-skills-disciplines.md` — every shipped hook/skill/discipline classified **AUTO (hook-enforced) vs MANUAL (Claude-recall)**, cited file:line. (The disciplines are labelled D1–D14.)
- **The empirical lapses (the test set):** `session-evidence.md` — concrete failures from a real session: codex-review skipped on both merges, advisor under-used, `/resolve` never used, a defer-and-halt gate error, and a cwd-split that tangled git/worktrees (the very kind of stale-worktree cruft the Wave-4 plan was written to fix).
- **The capability ground truth:** `references/claude-code-hooks.md` — exactly what each Claude Code / Agent SDK hook event can do (block / allow-deny / inject context / auto-approve). Every proposed hook MUST be expressible here.
- **Cross-session corroboration:** `references/insights-report-2026-06-03.md` — 201 sessions confirming the recurring failures (codex stalls, defer-paid-when-creds-available, cwd-bleed) + the output-token-limit failure mode.

**The problem to solve.** The plans ratified a loop that **self-enforces** its disciplines. In practice, most of those disciplines are **MANUAL** — they depend on Claude *remembering* to invoke them — and several that were *planned as enforcing* shipped **advisory** (the §9 gaps). The result is the lapse pattern in `session-evidence.md`. **Diagnose WHY each discipline lapses** by comparing the plans' intent/ACs against the as-built (the review + the inventory) and the empirical lapses, and determine **which can be moved from MANUAL to AUTOMATIC** (hook-enforced) given the real hook capabilities.

**Produce** a definitive, prioritized **hardening plan** at `.harness/hardening-workflow/HARDENING_PLAN.md`: for each discipline — hook-enforce (with the EXACT hook event + matcher + check + control output), skill-strengthen, or justified leave-manual; an ordered implementation sequence (high-leverage / low-risk first, mirroring the plans' one-unit-per-PR + hermetic-test discipline); and any operator decisions flagged. The deliverable is the plan, not the implementation.

**Hard constraints:**
- Hardens the **U-HK process machinery ONLY** — do NOT touch `design-substrate/**`, the H_T `harness-*/src` product code, or the H_T (R-NNN) roadmap.
- Every proposed hook MUST be capability-verified against `references/claude-code-hooks.md`. Reject anything not expressible there.
- **Never weaken** the locked hard-stop deny-list (paid LLM calls, secret/`.env` relocation, destructive git). Hardening only ADDS enforcement.
- Preserve the other operator-corrected rules: never-halt-unless-zero-units; defer-and-continue at a gate; prefer the free local ollama where it serves.

**Quality bar:** adversarially verify each proposed fix (refute it against the hook capabilities, the safety guards, and new failure modes — false positives that train the operator to ignore the signal, the Stop-block-8×-override cap, PermissionRequest-absent-in-`-p`, infinite-loop risk — before keeping it). Give special weight to the highest-leverage, cross-session-recurring items:
- **D6 — the paid-call reconciliation (flag for an operator decision).** The master plan *ratified* (U-HK-12) "hard-stop paid calls even in loop mode, log to loop-status, and keep working around." The operator *later corrected* this to "loop-mode + creds-available → **PROCEED** (run the paid call)." The current `permission-guard` still hard-denies paid calls in loop mode — so the as-built matches the *old* ratified intent and contradicts the *corrected* rule. Reconcile the two: how does the guard distinguish an **authorized** loop-mode paid run from an **unauthorized** one WITHOUT loosening the deny-list as the unauthorized-call backstop? Surface the design choice crisply for the operator.
- **D1 — codex-review** keeps getting skipped / stalling 12+ min / using the wrong model. Make the gate **fast** (diff-scoped), **enforced** (e.g. block `gh pr merge` until a per-branch review-passed marker exists), **model-verified** (echo the resolved model before launch), and **timeout-bounded** with a defined kill-and-proceed-with-noted-caveat fallback.
- **D7 — the cwd-split + worktree-hygiene class.** U-HK-26 reaps stale *merged* worktrees at SessionStart, but the **mid-session cwd-split** (`cd <main> && git …` running ops in the wrong checkout) and a **per-arc worktree/branch lifecycle** are still unguarded — they caused this session's tangle. Design the guard + the autonomous lifecycle.
- **D14 — output-token-limit loop-durability** (bias to concise responses + frequent durable per-step checkpoints so an unattended run survives truncation; the U-HK-05/27 checkpoint substrate exists — is it triggered often enough mid-loop?).

**Be economical:** structure the workflow for efficient, decorrelated coverage; don't over-spawn agents; keep it token-aware. Decide your own structure — there is no fixed phase list to follow.

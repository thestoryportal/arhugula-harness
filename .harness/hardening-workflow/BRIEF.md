# Hardening Workflow — Master Brief

> **You are reading the anchor context for the "loop/HIL hardening" dynamic workflow.**
> This brief + the four files it references ARE the complete context. Do not go
> hunting elsewhere first — read these, then act. Every claim here is cited to a
> real file/line or an authoritative URL; verify before extending, never invent.

**Run it:** in a fresh session, prompt **`begin workflow`** (or `/begin-workflow`).
The `begin-workflow` skill loads this package and launches `workflow.js`.

---

## 0. TL;DR — what this workflow must do

Audit the **autonomous-loop / HIL automation** (the U-HK-01..29 hooks + skills +
loop runner) against its **stated intent**, using **this session's concrete
lapses as the ground-truth test set**, and produce a **definitive hardening plan**
(`HARDENING_PLAN.md`) that makes each currently-MANUAL discipline **self-enforcing**
so a future unattended loop run can't silently skip it.

The single most important finding to act on: **~20+ engineering disciplines the
loop is *supposed* to follow rely on Claude *remembering* to invoke them (MANUAL);
only ~5 are actually hook-enforced (AUTOMATIC).** The manual ones lapse. This
session proved it (§3). The workflow's job is to close that gap — discipline by
discipline — with concrete, capability-verified hook/skill/guard changes.

---

## 1. THE GOAL (and what it is NOT)

**Goal of the hook-based loop/HIL work (U-HK-01..29):** automate the *development
workflow itself* — an unattended loop that drives the roadmap, enforces engineering
disciplines (review, advisor, grounding, refresh), manages git/worktree hygiene,
and **never halts unless there are genuinely zero units left to implement**. This
is **meta-automation**: automating *how we build*, with guardrailed autonomy.

**This is DISTINCT from the actual product (`H_T`).** `H_T` is a multi-LLM agent
harness specified under `design-substrate/` and built as `harness-{is,as,cp,od}`
atomic units (the "R-NNN" / "U-{IS,AS,CP,OD,RT}-NN" roadmap). The U-HK work lives
in `tools/hooks/`, `tools/loop/`, `.claude/skills/`, and `.harness/`, and is tracked
as **"tooling" rows** in `.harness/roadmap_status.md` — *not* as R-NNN items.

**Scope boundary for this workflow:** it hardens the **U-HK loop/HIL automation
only**. It does NOT touch `design-substrate/**` (the H_T spec — hard X-AL-3 rule),
H_T `harness-*/src` production code, or the H_T roadmap. Its deliverable is a plan
(and, if a second pass is authorized, the implementation) for the *process
machinery*, not the product.

### 1.1 The intended loop, end-to-end (the behavior we are hardening toward)

Operator runs `/loop-start` (or `tools/loop/run.sh` for headless). Then, each
iteration, autonomously:

1. **Audit** — §12.1 session-start hash audit (AUTO via `session-start.sh`); honor
   the §12.2.1 fixed-point lag carve-out.
2. **Derive next action** — §12.4.1 no-parking: never idle while the forward
   register is non-empty; pick the highest-value forward item.
3. **Ground empirically** — verify the item's premise at HEAD; grounding reveals
   Claude-closeable slices vs genuine gates.
4. **Decide reversible forks** via `/resolve` (Codex + advisor dual-reviewer);
   call `advisor()` at decision-forks + pre-done.
5. **Implement with tests**; run `just check`; **drive `just codex-review` to
   convergence before merge**.
6. **At a gate** (missing credential OR *any* HIL-provided dependency — a running
   daemon, real infra, a design ratification, a real backend): build the un-gated
   slice, `tools/loop/defer.sh <id> '<what's needed>'`, and **CONTINUE to the next
   unit**. If creds/deps ARE available, **PROCEED** (loop mode = standing
   authorization, incl. paid calls).
7. **Ship** — PR; on merge, the §12.2 + §12.2.1 fixed-point dashboard refresh.
8. **Manage git/worktree hygiene autonomously** — create/prune/exit worktrees and
   branches as work flows; never leave the working state tangled.
9. **Halt ONLY** when HIL explicitly stops it (`/loop-stop` / operator) OR every
   forward item is deferred (genuine exhaustion, `tools/loop/halt.sh`).

Today, steps **4, 5, 6, 8** are the weakest — they depend on Claude recalling them,
and they failed this session (§3).

---

## 2. THE CORE PROBLEM — manual disciplines don't self-enforce

`inventory-hooks-skills-disciplines.md` is the full map. The headline:

| Enforcement | Examples | Reliability |
|---|---|---|
| **AUTOMATIC (hook)** | §12.1 session-start audit, cache-clear, lint-on-edit/stop, loop worktree-GC at SessionStart, permission-guard deny-list | Fires every time |
| **MANUAL (Claude recall / skill invocation)** | codex-review-per-merge, advisor-per-fork, `/resolve`, no-parking, §12.2 refresh, posture check, memory hygiene, completeness-by-execution, cite-grounding, **cwd-safe git ops** | Lapses under drift/laziness |

The `research/dynamic-workflows.md` failure modes name exactly why the manual ones
fail inside one context window: **agentic laziness** (declaring done early),
**self-preferential bias** (Claude trusting its own review), **goal drift** (losing
"don't do X" constraints over many turns). A workflow heads these off by
orchestrating independent Claudes — which is also why a workflow is the right tool
to *design the fix*.

**The workflow's central question, per discipline:** can this MANUAL discipline be
moved to AUTOMATIC (hook-enforced), and if so, *how* — using the real Claude Code
hook capabilities documented in `references/claude-code-hooks.md` (e.g. a
`PreToolUse` deny on `gh pr merge` until a codex-review marker exists; a `Stop`/`UserPromptSubmit`
nudge when a decision-fork lacks an advisor call; a `PostToolUse(Bash)` guard that
rejects `cd <main> && git …` cwd-split patterns)?

---

## 3. GROUND-TRUTH TEST SET — this session's lapses (read `session-evidence.md` for detail)

Use these as the rubric: *would the hardened loop have prevented each?*

1. **codex-review skipped on BOTH merged PRs (#281, #283).** §13.1 makes it the
   default pre-merge reviewer. Attempted once (timed out 2× exploring the monorepo),
   abandoned; skipped entirely on the second. **Nothing forced it.**
2. **advisor() called once, not per-fork / pre-done.** §13.1 wants it at every
   decision-fork and before declaring done. Called before the first build only.
3. **/resolve never used.** Reversible forks (test design, exporter approach) were
   decided solo; the Codex+advisor `/resolve` dual-reviewer was never invoked.
4. **Defer-and-HALT error.** Deferred the R-300 live paid run to the operator AND
   treated it as a stopping point — violating both the never-halt rule (§12.4.1)
   and the loop-mode paid-call rule (creds were present → should have PROCEEDED).
   The operator had to correct it.
5. **Git/worktree cwd-split failures (×2, flagged by the session-learning hook).**
   `cd <main> && git …` ran ops in the main checkout while edits lived in the
   worktree → a refresh branch was created in the wrong checkout, a commit failed,
   branches got tangled. The misnamed `u-hk-01-hook-lib` worktree was reused for
   unrelated R-300 work. **No hook caught the cwd-split.**
6. **§12.2 refreshes done by hand** (correctly, but MANUAL) — fine here, but it's
   recall-dependent.

These map to disciplines D1 (codex), D2 (advisor), D3 (/resolve), D4/D5/D6
(never-halt / defer-and-continue / paid-call rule), D7 (git/worktree+cwd hygiene),
D8 (refresh). The hardened loop should make D1–D8 self-enforcing.

---

## 4. THE WORKFLOW DESIGN (implemented in `workflow.js`)

Patterns drawn from `research/dynamic-workflows.md` (memory/rule-adherence:
"one verifier agent per rule"; adversarial verification; fan-out-and-synthesize;
completeness critic):

- **Phase 1 — Per-discipline gap audit (fan-out + adversarial verify).** One agent
  per discipline (D1..Dn from the inventory). Each: (a) classify AUTO vs MANUAL;
  (b) cite whether/how it lapsed this session; (c) judge whether it CAN be
  hook-enforced given `references/claude-code-hooks.md`; (d) propose the concrete
  enforcement mechanism (hook event + matcher + check + allow/deny/block/inject,
  or skill-side change). An **adversarial partner** then refutes each proposal:
  does the hook event actually support this? new failure modes? false-positive /
  infinite-loop risk? does it loosen a safety guard? (deny>ask>allow; Stop-block
  8× cap; PermissionRequest absent in `-p`; etc.).
- **Phase 2 — Synthesis (barrier).** Fold surviving proposals into a single,
  prioritized hardening plan: per discipline, the concrete change (file, event,
  logic), ranked by leverage (lapses prevented) × inverse risk. Plus a dedicated
  **git/worktree/cwd hygiene autonomy** design (the D7 cluster) and a **never-halt
  correctness** trace of `tools/loop/run.sh` + `stop-loop.sh`.
- **Phase 3 — Completeness critic.** "What discipline / lapse / hook-capability is
  unaddressed?" + verify NO proposal relies on a hook capability that does not
  exist in `references/claude-code-hooks.md`.

**Deliverable:** `.harness/hardening-workflow/HARDENING_PLAN.md` — the definitive,
capability-verified plan. Implementation is a separate authorized pass.

---

## 5. HARD CONSTRAINTS for every agent in this workflow

- **No `design-substrate/**` edits, no H_T `harness-*/src` edits, no H_T roadmap
  changes.** This workflow is U-HK process-machinery only.
- **Every hook-capability claim must trace to `references/claude-code-hooks.md`.**
  Do not propose a hook that fires on an event that doesn't exist, or a control
  output an event doesn't support. The reference lists exactly what each event can
  do (block? allow/deny? inject context?).
- **Never weaken a safety guard.** The permission-guard deny-list (paid calls,
  secret relocation, destructive git) is locked. Hardening = *adding* enforcement,
  not loosening blast-radius limits.
- **Preserve the corrected rules:** never-halt-unless-zero-units; defer-and-continue
  at a gate; loop-mode-creds-available → proceed (incl. paid calls); free local
  ollama preferred over paid where it serves.
- **Cite, don't invent.** File:line or §section for every claim about the current
  implementation; the inventory + session-evidence are the source of truth for
  "what exists" and "what lapsed."

---

## 6. INPUTS INDEX (the package — all in `.harness/hardening-workflow/`)

| File | What it is |
|---|---|
| `BRIEF.md` | This file — the anchor. |
| `inventory-hooks-skills-disciplines.md` | The full map: every hook (ENFORCING/ADVISORY), every skill, every CLAUDE.md §12/§13/§14 discipline + its AUTO-vs-MANUAL enforcement classification + intended enforcement point. **The primary audit target.** |
| `session-evidence.md` | This session's concrete lapses (the ground-truth test set), each tied to the discipline that failed and why the current mechanism didn't catch it. |
| `references/claude-code-hooks.md` | Authoritative Claude Code + Agent SDK hooks reference (every event, the allow/deny/block/inject protocol, settings shape, autonomous-loop + auto-approve guidance). **The capability ground truth** — every proposed hook must be expressible here. |
| `references/insights-report-2026-06-03.md` | **Cross-session corroboration** (201 sessions / 26 days): D6 (defer-paid-when-creds-available), D1 (codex stalls + wrong model), D7 (cwd-bleed) are RECURRING, not one-off — plus concrete fixes and the NEW **D14** (output-token-limit / loop-durability) failure mode. High weight. |
| `workflow.js` | The pre-authored dynamic-workflow script the `begin-workflow` skill launches (audits D1..D14). |

External (in the main repo root, untracked): `research/dynamic-workflows.md`
(the workflow-pattern model), `research/sessionend-clear-automated-loop-gemini.md`
(SessionEnd-on-/clear is unreliable → SessionStart-routing is correct).

Authoritative governance: `CLAUDE.md` §11 (posture), §12 (roadmap/loop), §13
(orchestration/advisor/codex), §14 (conventions). Status: `.harness/wave{1,2,3,4}-hooks-status.md`,
`.harness/hook-advisor-workflow-review.md` (§9 gaps / §10 closures).

---

## 7. SUCCESS CRITERIA for the workflow's output

`HARDENING_PLAN.md` is good iff:
- Every discipline in §3's test set (D1–D8) has a concrete disposition: hook-enforce
  (with the exact event + check), skill-strengthen, or justified leave-manual.
- Every proposed hook is capability-verified against `references/claude-code-hooks.md`.
- The git/worktree/cwd-split cluster (D7) has a concrete autonomous-hygiene design.
- The never-halt + defer-and-continue + paid-call rules are preserved and, where
  possible, made enforceable (not just documented).
- No safety guard is loosened; no design-substrate / H_T-product scope creep.
- A clear, ordered implementation sequence (what to build first; what's high-leverage
  / low-risk vs needs-care).

# Charter — Council Arc: Context & Memory Layer Grounding

**Arc ID:** council-context-memory-grounding
**Opened:** 2026-06-03
**Worktree / branch:** `worktree-council-context-memory`
**Status:** ✅ RE-CLOSED 2026-06-04 — **evidence-enrichment round (Round 5) COMPLETE**: `DESIGN.md` **v2 (evidence-enriched)** CLEARED-TO-COMMIT (full loop reconciled-to-zero — E1 7-voice deliberation + Phase-B cross-read → adversarial#1 → Codex+advisor → consolidated reconcile → adversarial#2 gate CLEAR-WITH-FOLD, folds applied + re-verified at HEAD; the proportionality-vs-canon spine held end-to-end — **zero new MVP workstreams; the one new mechanism G-LINK deferred**). Round-5 framing: fresh research landed in `03-evidence/` (4 docs: empirical 169-note memory-graph + NotebookLM broad/deep external canon). Council reconvened (C2/C3 primary + C1/C5/C7/C9 consultants + **C8** eval, promoted to first-class for this round because the fresh Deep-dive 5 eval-gates + WS-0 success-gate are squarely C8's) to fold the research into `DESIGN.md` through the full §5 loop. **Convening spine-tension (this round):** proportionality-vs-canon — does each piece of richer external canon (ICM folders, CoALA tiers, temporal frontmatter, consolidation daemon, eval cascade) *earn its place* against (a) the solo-developer proportionality filter (CA-2 governance-bloat irony; cluster-2 §1.11) and (b) the WS-0 drift metric? Prior closure (Rounds 1–4; `DESIGN.md` **v1** committed; adversarial #2 CLEAR-TO-COMMIT) preserved as the baseline this round enriches. *(Prior status: ✅ CLOSED — full reconciliation loop complete; `DESIGN.md` committed; handed off for a downstream execution arc.)*

> This is a **memory-persistence + handoff ledger**. Every stakeholder in the loop
> (council, adversarial reviewer, Codex+Advisor) writes its findings into its own
> sub-directory here so the work survives context truncation and hands off cleanly,
> without polluting the broader repo context.

---

## 1. Mandate (operator directive, 2026-06-03)

Ground and align the harness's **context-engineering** and **state/memory-persistence**
layers to the intended initial spec, and develop a **plan** to perform that grounding/
alignment now so forward coding work benefits. The harness spec leans heavily on
**interpretable-context methodology (folder architecture)**; drift during coding sessions
is attributed substantially to bloated/polluted context + broken context-engineering +
directory structure. This is the **first** of a planned series of domain councils.

## 2. Hard constraints

- **Additive only.** This arc writes findings to ledgers. It does **NOT** edit existing
  code, docs, or folder structure, and does **NOT** touch `design-substrate/**` content,
  `harness-*/src`, or the H_T `R-NNN` roadmap. **The deliverable is a plan, not its execution.**
- **Stakeholder ledgers in dedicated dirs** (this tree) — no pollution of broader context.
- **Grounding sources:** `/research/` (esp. cluster-2 context-prompts-memory + the Pattern
  Reference Catalog) and the NotebookLM harness corpus (`[[notebooklm-harness-corpus-url]]`)
  for any clarity gaps. Cite primary canonical at its current version.
- Preserve the operator-corrected harness rules (never-halt, defer-and-continue,
  prefer-free-ollama, the locked paid/secret/destructive deny-list). This arc does not relitigate them.

## 3. Initial operator observations (starting hunches — NOT the grounding frame)

> **These are the operator's *initial observations*, to be EXPLORED by the council — not the spine of
> the grounding, and not its scope.** The council grounds first-principles in §6's canonical sources
> (each domain specialist's *original spec* + the *research corpus*) and a **broad, first-principles
> review/analysis of the ENTIRE repo through each voice's specific domain lens** (structure · context ·
> memory). These observations are one input the council will test, confirm, refine, reframe, or set
> aside — they do not frame or bound the analysis.

1. **CLAUDE.md bloated/unfocused** — 761 lines / ~333 KB / 60 headers; does not serve its
   intended purpose (agent workflow rules, conventions, guardrails).
2. **Stale markdown polluting root / `.harness/` / `design-substrate/`** — root littered with
   `Phase_7_*Tension*`, `Adversarial_Review_*`, `Skill_Eval_*`; `.harness/` holds hundreds of
   `class_1_fork_*` / `adversarial_review_*` / `memory_audit_*` ledgers; not organized for
   context engineering (some not stale per se, but unoptimized).
3. **Stale versioned workflow files + no single source of truth** — `design-substrate/`
   `Project_Workflow_v1.8→v1.14` (7 copies), `Cross_Axis_Composition_v2.1→v2.19` (19 copies);
   none reflect the hook/skill/advisor loop actually in use. **No `WORKFLOW.md`.**
4. **No `AGENTS.md`, no `ARCHITECTURE.md`** — governance/architecture single-sources do not
   exist; CLAUDE.md does not fill the gap.
5. **No synthesized hook-system doc** — no single doc of how the hook system functions + what
   each hook triggers. For THIS arc the relevant hooks are the context/memory ones:
   SessionStart §12.1 audit, PreCompact/PostCompact checkpoint+reinject (U-HK-05/06), the
   StatusLine context-recovery (U-HK-27), UserPromptSubmit context injector (U-HK-08),
   capture-failure (U-HK-07), loop-gc (U-HK-26), session-end-cleanup (U-HK-09), MEMORY.md cap surface.

## 4. Council convening (operator-selected)

**Voices (6 — explicit operator override above the nominal cap of 5, justified by a genuinely
six-axis foundational topic):**

| Voice | Role | Stake in context/memory grounding |
|---|---|---|
| **C2 context-engineering** | **PRIMARY** | the layer's center: what goes in context, folder-architecture interpretability, CLAUDE.md/AGENTS/ARCHITECTURE/WORKFLOW |
| **C3 state-memory-persistence** | **CO-PRIMARY** | durable memory, MEMORY.md, checkpoints, the across-turn seam |
| **C1 orchestration** | consultant | session/loop lifecycle that drives context in/out |
| **C5 validation-contract** | consultant | the contract surfaces for handoff ledgers + doc single-sources |
| **C7 observability** | consultant | visibility of context/memory state |
| **C9 reliability-recovery** | consultant | checkpoint/context-recovery durability (the D14 layer) |

Consultants must **surface-tension or propose-refinement** — formulaic concurrence is rejected
(primary-collapse guard, the reason the nominal cap exists).

**Nameable tension (justifies convening):** **T-perm-2 — C2 ↔ C3** — within-turn active context
vs. across-turn durable state: the read/write seam. Resolved at H_T via the IS-spec read/write
boundaries (anchor: `Spec_Information_Substrate_v1.md`).

## 5. Cross-cutting reviewers (the reconciliation loop)

- **harness-adversarial-reviewer** — red-teams the council findings (finding-classified per
  `Project_Workflow §4.1`).
- **Codex** (`just codex-review`, gpt-5.5, out-of-family, $0 subscription) **+ advisor()**
  (transcript-aware) — the dual decorrelated evaluators (CLAUDE.md §13.1 division of labor).

**Loop (operator-clarified 2026-06-03 — the precise choreography; the Council is the hub each reviewer reconciles with PAIRWISE, in sequence; adversarial BOOKENDS):**

1. **Adversarial review #1** red-teams the council deliberation → findings (finding-classified per `Project_Workflow §4.1`) → `02-adversarial/`.
2. **Adversarial ⟷ Council reconcile to zero** — the Council (genuinely-invoked voices) responds to the adversarial findings (accept / reconcile / rebut); loop until adversarial and council are mutually reconciled. **GATE: this must close BEFORE handoff to Codex/Advisor.** Logged in `04-reconciliation/`.
3. **Codex + advisor handoff** — Codex (`just codex-review`, gpt-5.5, out-of-family, $0 subscription) **+ advisor()** (transcript-aware) evaluate the *council-reconciled* deliberation + PLAN → `03-codex-advisor/`.
4. **Codex/Advisor ⟷ Council reconcile to zero** — the Council responds to the Codex/Advisor evaluations; loop until reconciled. Logged in `04-reconciliation/`.
5. **Adversarial review #2 (gate)** — re-reviews the whole arc for residual unreconciled items. **All reconciled → commit `DESIGN.md`.** Anything still open → loop back to the relevant reconcile step.

Each handoff writes its own stakeholder ledger; `04-reconciliation/` tracks convergence (rounds, tensions opened/closed, who-reconciled-with-whom, status). All reviewer + council passes are **genuine invocations** (dedicated agents adopting their skills), not core-agent reference-reads.

**STANDING STEP — cross-cutting synthesis (operator-prompted 2026-06-03):** every isolated-voice pass (the voices run as separate parallel agents, blind to each other — deliberate anti-primary-collapse) MUST be followed by a **cross-cutting synthesis**: the voices that share a seam **cross-read each other's dispositions and reconcile the seam directly** (COHERE / flag-CONFLICT / refine), so the **council itself** closes cross-cutting tensions rather than relying on the orchestrator to stitch them or the adversarial reviewer to catch them. Rationale (empirical): in this arc the adversarial reviewer caught 2 cross-cutting tensions the isolated voices missed, and the Stage-2c cross-read then surfaced a sharp NEW finding (the memory store is not git-versioned) that no single isolated voice produced. Isolation gives decorrelated positions; the cross-read ensures no cross-cutting conflict survives. Applies to BOTH the deliberation pass and every reconcile pass.

## 6. Canonical anchors + grounding discipline (the spine)

**Grounding discipline (the spine).** Each convened voice grounds its contribution **FIRST** in (a) its
*original domain spec* (the design-substrate canonical at current version + the voice's locked spec —
e.g. C2 ← the IS context/read-seam + s5; C3 ← the IS durable-state seam + s6), and (b) the *research
corpus*; **THEN** (c) a **broad, first-principles review/analysis of the ENTIRE repo through its domain
lens** — the actual directory/folder architecture (interpretable context), every context-bearing
artifact (CLAUDE.md, `.claude/skills/`, agent instructions, design-substrate-as-context), and every
durable-state/memory artifact (MEMORY.md, `memory/`, checkpoints, the `.harness/` ledgers, git-as-state,
the 240 design-substrate files as semantic memory). The deliverable aligns the **as-is repo** to the
**intended spec**. The §3 operator observations are explored *within* this review, never used to frame
or bound it.

**Anchors:**
- **Intended spec (per domain):** `design-substrate/Spec_Information_Substrate_v1.md` (IS — the C2↔C3
  read/write boundary), `design-substrate/Architectural_Design_Document_v1_3.md` (ADD); each convened
  voice's locked spec (the s4–s12 lineage cited in the voice SKILLs).
- **Research:** `research/agent-harness-eng-research-cluster-2-context-prompts-memory.md`,
  `research/Pattern_Reference_Catalog_v1.0.md`, the cluster deep-dives 1–5; NotebookLM corpus
  (`[[notebooklm-harness-corpus-url]]`) for clarity gaps.
- **Prior memory work:** `.harness/memory_audit_2026-05-31{,_round2,_round3}.md`.
- **As-is repo (reviewed BROADLY through each domain lens, not symptom-scoped):** the full directory
  structure; root `CLAUDE.md`; `.claude/skills/`; `design-substrate/` (240 .md); `.harness/`; MEMORY.md
  + `memory/`; the hook inventory + `.harness/hardening-workflow/HARDENING_PLAN.md` (D11/D14 findings).

## 7. Ledger structure (this tree)

```
00-CHARTER.md          (this file)
01-council/            C-voice deliberation (Convening Block, CCR, contributions, TENSION block)
02-adversarial/        harness-adversarial-reviewer findings
03-codex-advisor/      Codex + advisor() evaluations, per round
04-reconciliation/     loop log: rounds, tensions opened/closed, convergence status
DESIGN.md              the reconciled grounding + alignment plan (the deliverable)
```

## 8. Deliverable

`DESIGN.md` — a reconciled, council-ratified, adversarially-reviewed, Codex+Advisor-evaluated **plan**
to ground & align the harness's **as-is** context + memory layers to the **intended** per-domain spec
(the IS read/write boundary + the interpretable-context / folder-architecture methodology). Whatever the
broad, domain-lensed repo review surfaces as the gap between as-is and intended becomes the plan — likely
(but determined by the review, not pre-scoped) the documentation architecture, CLAUDE.md altitude +
budget, the durable-memory model (MEMORY.md / `memory/` / checkpoints / ledgers / git-as-state), and the
folder/directory architecture as interpretable context — sequenced, with the C3 memory-persistence model
intact. Handed off for execution in a later arc.

---

## Process log

- **2026-06-03** — Arc opened. Worktree `worktree-council-context-memory` created (proper, replacing
  the prior misnamed/broken `u-hk-01-hook-lib` phantom, which was resolved: dir removed, session
  exited, and orphan branch `worktree-u-hk-01-hook-lib` **verified definitively-merged and DELETED**
  (operator-authorized, contingent on definitive safety): it was PR #266's head ref (mergeCommit
  `4d0baee`, an ancestor of main); all 26 authored files byte-identical to the squash commit; zero
  branch-unique files; no post-merge commits — content fully contained in main per
  `[[squash-merge-branch-prune-recipe]]`. Ledger structure created.
- **2026-06-03** — Worktree saga fully closed; `git worktree list` = main + council-context-memory only.
  Core dyad (C2/C3) grounded. Next: ground consultants (C1/C5/C7/C9) + IS read/write boundary +
  research cluster-2, then produce the six-voice deliberation → `01-council/`.
- **2026-06-03** — **Stage 1 COMPLETE.** Operator directive mid-arc: skills must be **genuinely invoked**, not
  read-as-reference for the core agent to do all the work. Restructured accordingly: each of the 6 voices ran
  as a **dedicated agent adopting its own `cN` council skill** + reviewing the repo through its lens (Workflow
  `wf_ecf4bb51-309`; 6 agents; primaries C2/C3 independent, consultants C1/C5/C7/C9 reacted to the primaries;
  read-only — orchestrator composed the envelope + wrote the ledger). Output: `01-council/DELIBERATION.md`
  (Convening Block · slim CCR · probe-first log · 6 contributions · 6-tension block · convergence diagnosis ·
  emerging PLAN shape WS-1..WS-6 + X) + `01-council/contributions/c{1,2,3,5,7,9}.md` (verbatim) +
  `04-reconciliation/reconciliation-log.md` (Round 1). 31 findings; 6 tensions (T2 probe-closed; T1/T6
  Layer-3 permanent; T3/T4/T5 reconcilable-pending). Convergent diagnosis: the harness runs its own
  context/memory PROCESS state in violation of the read/gate contracts (C-IS-07 §7.2 + §6.4 `verify_chain`)
  it authored for its PRODUCT state; the fix-patterns already exist in-repo. **Next: Stage 2 —
  `harness-adversarial-reviewer` red-teams the deliberation → `02-adversarial/`.**
- **2026-06-03** — Operator clarified the §5 reconciliation choreography (loop rewritten above): the Council
  is the hub each reviewer reconciles with PAIRWISE in sequence; adversarial BOOKENDS. Order = adversarial#1
  → **adversarial⟷council reconcile-to-zero (gate before handoff)** → Codex+advisor → **codex/advisor⟷council
  reconcile-to-zero** → **adversarial#2 gate** (residual sweep) → DESIGN.md.
- **2026-06-03** — **Stage 2 (adversarial#1) COMPLETE.** First attempt failed on a StructuredOutput-marshaling
  quirk (`wf_70ce829d`; 27 tool-calls of genuine work but no schema object emitted; transcript held only short
  narration — not recoverable). Re-launched schema-free + verification-bounded (`wf_7843e4a1`): the agent's
  final markdown IS the deliverable. Output: `02-adversarial/REVIEW.md`. **Verdict: CLEAR-to-Stage-3 with 5
  Class-2 in-arc revisions + 4 Class-1 nits; 0 Class-3; cite-verification CLEAN (every load-bearing council
  cite resolves byte-exact at HEAD); 9-item checklist 7-PASS / 2-minor-FLAG.** Class-2 = AR-1 plan/execute
  boundary, AR-2 home-of-record (decide, don't defer), AR-3 version-chain X-AL-3 execution-posture, AR-4 FM-H
  re-rate to structural-latent + detection-step-gate, AR-5 apply the proportionality filter the council named
  (MVP slice = WS-1 + G1 + WS-6/D14 + X). Sharpest miss: `AGENTS.md` auto-load risk (WS-2 could re-create the
  WS-1 bloat). **Next: Stage 2b — adversarial⟷council reconcile-to-zero (genuine council response to the AR
  findings) BEFORE Codex/advisor handoff.**
- **2026-06-03/04** — **Stage 2b + 2c COMPLETE → Adversarial ⟷ Council reconciled-to-zero** (loop step-2 gate MET).
  Stage 2b (council per-lane response, isolated): C2/C3/C5/C9 returned full dispositions; C1/C7 hit a transient
  server rate-limit. Operator then asked whether voices were convening in isolation or fleshing out cross-cutting
  issues — exposing a real gap (isolated voices relied on orchestrator-stitch + adversarial-catch for cross-cutting
  tensions). Added the **cross-cutting synthesis standing step** (§5 above) and ran **Stage 2c** (`wf_4011845e`):
  C1+C7 re-ran + cross-read; C5+C9 cross-confirmed shared seams. **All seams COHERE; zero REBUT; AR-9 count
  audited = 31.** Cross-read wins: C5↔C9 gate-vs-mode closed structurally (surface-disjoint; never-halt preserved);
  **NEW finding** — the out-of-worktree memory store is NOT git-versioned (`git rev-parse` → not a repo) →
  CLAUDE.md §12.5.1 git-provenance claim false at HEAD → FM-H lost-update currently unrecoverable → FM-H
  consequence elevated to HIGH (incidence still unconfirmed). Full record: `04-reconciliation/round2-reconciled.md`
  (incl. the reconciled PLAN-shape v2 + MVP slice). **Next: loop step 3 — Codex + advisor handoff → `03-codex-advisor/`.**
- **2026-06-04** — **Stage 3 + 3b + 4 COMPLETE → ARC CLOSED.** Loop step 3 (Codex out-of-family + advisor transcript-aware
  eval; `03-codex-advisor/`): the two decorrelated voices INDEPENDENTLY converged that the PLAN optimized byte-count not
  DRIFT — the decisive signal of the arc. Codex out-of-family caught the governance-native-bloat irony + verify-before-evict;
  one advisor↔Codex disagreement on "X" resolved toward Codex (minimal-recoverability load-bearing). Loop step 4 (Stage 3b,
  targeted 4-voice reconcile incl. the genuinely-missing **C8 eval voice**): all ACCEPT; C8 added **WS-0 drift-probe as the
  success gate** (6-class binary taxonomy + counterfactual before/after probe; byte≤cap demoted to leading-indicator) — the
  PLAN became a falsifiable drift-reduction plan, not a context-slimming plan. Loop step 5 (Stage 4 adversarial #2 gate,
  single bounded reviewer): **CLEAR-TO-COMMIT** — all CA/AR closed, WS-0 falsifiable, anti-bloat self-applied, no Class-1;
  one Class-3 grader-blinding refinement folded (zero residual). **Deliverable `DESIGN.md` committed.** Full reconciliation:
  `04-reconciliation/reconciliation-log.md` (Rounds 1-4). Arc stats: ~22 genuine agent invocations across 4 fan-out stages +
  2 decorrelated evaluators (advisor + Codex), all reviewers/voices genuinely invoked (not core-agent ventriloquism), every
  pairwise gate reconciled-to-zero. Handed off for a downstream EXECUTION arc (validated by the WS-0 probe). NOTE for that
  arc: `CLAUDE.md §12.5.1` carries a false-at-HEAD claim (memory store "provenance lives in git history" — the store is not
  git-versioned); correct it when versioning the store per X-min.
- **2026-06-04** — **ARC REOPENED → Round 5 (evidence-enrichment).** Fresh research landed in `03-evidence/` (4 docs:
  `memory-corpus-evidence-for-council.md` [empirical 169-note graph], `notebooklm-research-findings-for-council.md` [BROAD],
  `notebooklm-deep-dive-findings.md` [DEEP, 6 mechanism dives], `evidence-map.md` [router]). Operator directive: reconvene the
  context-engineering + state/memory-persistence council (+ consultant cross-cutting members) to **review the fresh research,
  surface where it enriches `DESIGN.md`, deliberate + debate cross-cutting, land an integration plan, then re-run the full §5 loop**
  (adversarial⟷council → Codex/advisor⟷council → adversarial#2 gate) — all reviewers **genuinely invoked** (skills adopted by
  dedicated agents that debate each other by name), not core-agent reference-reads. **Roster deviation logged:** C8 (eval) added to
  the charter §4 named set {C2,C3,C1,C5,C7,C9} → {…,C8} because the fresh Deep-dive 5 (eval-health gates) + WS-0 (the success gate)
  are squarely C8's domain; C4/C10/C11 remain handled-by-reference (anti-bloat discipline per CA-2). **Convening spine-tension:**
  proportionality-vs-canon (does each richer-canon item earn its place vs the solo-dev filter + the WS-0 drift metric?) — set so the
  round adjudicates *which* enrichments fold in, rather than dutifully folding all 30 citations (the very bloat the arc fights).
  Pre-substantive advisor() consulted on round structure / voice-selection / mechanism / deliverable-versioning before launch.
  `DESIGN.md` v1 preserved as baseline (git holds it); the enriched deliverable will be a **conscious versioned move** (v2 + change-note),
  not a silent overwrite. Loop ledgered additively under the existing numbered subdirs (`-evidence` / `-r5` suffixes). Round 5 stages:
  **E1** council enrichment deliberation (isolated 7-voice fan-out → cross-cutting debate) → **E2** adversarial#1 → **E2b**
  adversarial⟷council reconcile-to-zero → **E3** Codex(`just codex-review`)+advisor() → **E3b** codex/advisor⟷council reconcile →
  **E4** adversarial#2 gate → enriched `DESIGN.md` v2.
- **2026-06-04** — **ROUND 5 COMPLETE → ARC RE-CLOSED.** Full loop ran with all reviewers/voices genuinely invoked
  (dedicated agents adopting their skills, debating by name), every pairwise gate reconciled-to-zero. Stages (operator-steered,
  phase-by-phase, gates before each full-council convening): **E1-A1** primaries C2/C3 independent (`wf_07c07c77-82b`) →
  **E1-A2** consultants C1/C5/C7/C8/C9 react-to-primaries (`wf_db74601a-68d`) → **E1-B** seam-routed cross-read DEBATE +
  primary confirm-back (`wf_8fb2e418-cfe`; reconciled-to-internal-zero) → **E2** adversarial#1 (`wf_34b95aca-d0b`; CLEAR,
  cite-CLEAN, no missed tensions) → **E3** Codex out-of-family (gpt-5.5 $0-subscription; advisor wrote the descriptive
  research primer per operator directive) + advisor in-family (Codex earned decorrelation — 3 unique P2s + a P1 diverging-on-fix) →
  **consolidated reconcile** (operator-reordered E2b+E3b into one pass; `wf_be40ac24-ebe`; zero CONFLICT) → **E4** adversarial#2
  gate (`wf_de7a33be-c4e`; **CLEAR-WITH-FOLD** — 2 Class-3 folds: stale MEMORY.md over-cap premise reframed [the falsifying
  ad-hoc lossy compaction is itself the live D4 the contract prevents — reaffirms WS-3a] + 2 cite-range fixes; all re-verified
  at HEAD by the orchestrator) → **`DESIGN.md` v2 CLEARED-TO-COMMIT.** **Spine outcome:** proportionality-vs-canon held
  end-to-end — fresh canon overwhelmingly citation-enriching/confirmatory; **zero new MVP workstreams**; ~8 sharpens/riders +
  1 deferred gate (G-LINK); long canon-refusal list (ICM numbered-folders / CoALA dir-split / consolidation daemon / eval
  cascade / embedding rot-scores all refused on solo+drift grounds). ~24 genuine agent invocations + 2 decorrelated evaluators.
  Ledger: `01-council/` (DELIBERATION-2 + contributions-r5 + crossread-r5) · `02-adversarial/` (REVIEW-3 + REVIEW-4-gate-r5) ·
  `03-codex-advisor/` (advisor-eval-r5 + codex-eval-r5) · `04-reconciliation/` (round5-consolidated-responses + the Round-5 log).
  Handed off for a downstream EXECUTION arc — validated by the WS-0 probe (+ its INCOMPLETE-on-rare-class verdict), not by
  reconciliation. **NEW note for that arc:** an ad-hoc lossy MEMORY.md compaction (≈120→45 index entries) fired mid-arc at
  06:27 2026-06-04 — a concrete instance of the D4 surface WS-3a's enforced/non-lossy contract targets; the `§12.5.1:651`
  false-git-claim is re-confirmed false at HEAD (store still not git-versioned).

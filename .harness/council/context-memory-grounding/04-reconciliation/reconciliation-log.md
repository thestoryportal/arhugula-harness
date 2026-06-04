# Reconciliation Log — context-memory-grounding council

Running convergence tracker: rounds, tensions opened/closed, status. Target = zero open/unreconciled tensions before `DESIGN.md` commit.

---

## Round 1 — Stage 1 council deliberation (2026-06-03)

**Input:** genuine 6-voice invocation (C2/C3 primary; C1/C5/C7/C9 consultant). **Output:** `01-council/DELIBERATION.md` + `01-council/contributions/c{1,2,3,5,7,9}.md`. **Findings:** 31 across 6 voices. **Tensions surfaced:** 6.

| T-ID | Parties | Issue | Status after Round 1 |
|---|---|---|---|
| T1 | C2 ↔ C3 | provenance: where it lives / how much enters the prefix | **Layer-3 permanent (T-perm-2)** — H_T-resolved at C-IS-07 §7.1/§7.2; operative resolution = cut-list is co-primary C2×C3 (not closed; permanent, with a sequencing rule) |
| T2 | C5 ↔ C2 | which precedent to mirror for the byte-budget | **PROBE-RESOLVED (C5)** — cap is advisory (probe); PLAN adopts `--check`-tier gate, not advisory hook |
| T3 | C7 ↔ C2 | legibility vs attention-budget on the eviction | **surfaced — reconcilable** (resolution proposed: eviction bound to a navigable INDEX + version-state injector); confirm at Stage 2/3 |
| T4 | C9 ↔ C2 | sequencing slim-down vs recovery-completeness | **surfaced — reconcilable** (resolution proposed: WS-1 lands WITH WS-6); confirm at Stage 2/3 |
| T5 | C9 ↔ C3 | recovery of the out-of-worktree memory store | **surfaced — clean co-primary** (resolution proposed: C3 owns serialization+store, C9 confirms rollback boundary) |
| T6 | C1 ↔ C9 | loop fault-handling-as-topology | **Layer-3 permanent (T-perm-3)** — surfaced, not relitigated |

**Open / to-confirm before DESIGN.md:** T3, T4, T5 (reconcilable — proposed resolutions need adversarial + Codex/advisor confirmation). T1/T6 are permanent (carried, not closed). T2 closed-by-probe.

**Probe-first resolutions logged this round (council-orchestrator §5):**
- MEMORY.md cap = advisory (`session-end-cleanup.sh:53` / `loop-gc.sh:56` route on nothing); `substitution_ledger --check` exits 1 → T2.
- CLAUDE.md = 341,611B; 60/60 recent commits touch it → strengthens C2 cost claim.
- cache-hit-rate has no dev-loop observability home → C2 signal-b is a constraint; use git-edit-cadence proxy.

**Convergence status:** Stage 1 COMPLETE. 1 of 6 tensions closed (T2); 2 permanent (T1, T6); 3 reconcilable-pending (T3, T4, T5). **Next: Stage 2 — `harness-adversarial-reviewer` red-teams the deliberation + emerging PLAN shape → `02-adversarial/`.**

---

## Round 2 — Adversarial ⟷ Council reconcile (2026-06-03/04) — **COMPLETE, reconciled-to-zero**

Full record: **`round2-reconciled.md`**. Per-voice: `round2-council-responses/c{2,3,5,9}.md` (Stage 2b) + `round2c-crosscutting/c{1,7,5,9}.md` (Stage 2c cross-read).

- **Adversarial #1** (`02-adversarial/REVIEW.md`): CLEAR-to-Stage-3 + 5 Class-2 + 4 Class-1 + 2 missed tensions; cite-verification CLEAN.
- **Stage 2b** (council responds, per-lane, isolated): C2/C3/C5/C9 returned; C1/C7 hit a transient server rate-limit (re-run in 2c).
- **Stage 2c** (cross-cutting synthesis — the NEW standing step, operator-prompted): C1+C7 re-ran + cross-read; C5+C9 cross-confirmed shared seams. **All seams COHERE.**
- **Dispositions:** every AR finding ACCEPT or RECONCILE-compose; **zero REBUT**. AR-9 count audited = 31 (5+6+5+5+5+5).
- **Cross-cutting wins:** C5↔C9 gate-vs-mode closed structurally (surface-disjoint; never-halt preserved) — closes the adversarial's own missed-tension #1. C1×C2 HOOKS.md = 3 orthogonal lanes. Unified MVP slice cohered (C2/C3/C5/C7).
- **NEW finding (cross-read value):** the out-of-worktree memory store is NOT git-versioned (C9 `git rev-parse` → not a repo) → CLAUDE.md §12.5.1 git-provenance claim false at HEAD → FM-H lost-update currently unrecoverable → FM-H consequence elevated to HIGH (incidence still unconfirmed). Remedy: version/snapshot the store (C3), detect-gated.

| T-ID | Status after Round 2 |
|---|---|
| T1 (C2↔C3) | Layer-3 permanent — operative resolution unchanged (cut-list co-primary; sequence joint) |
| T2 (C5↔C2) | CLOSED (probe-resolved R1; re-confirmed: byte-budget = `--check` gate) |
| T3 (C7↔C2) | RECONCILED (eviction bound to navigable INDEX + version-state injector; AGENTS.md auto-load verified non-manifesting) |
| T4 (C9↔C2) | RECONCILED (WS-1 lands WITH WS-6/D14; recovery-completeness co-requisite) |
| T5 (C9↔C3) | RECONCILED + sharpened (rollback boundary RESOLVED NEGATIVE → store not git-versioned; remedy = version the store) |
| T6 (C1↔C9) | Layer-3 permanent — surfaced, not relitigated |
| **NEW C5↔C9** | RECONCILED-compose (surface-disjoint CI-gate vs runtime-mode) |
| **NEW WS-2 self-tension** | RESOLVED (AGENTS.md not auto-loaded in this H_E; forbid `@import`) |

**Convergence status:** Adversarial ⟷ Council **reconciled-to-zero** (loop step 2 gate MET). **Next: loop step 3 — Codex + advisor handoff → `03-codex-advisor/`.**

---

## Round 3 — Codex + advisor ⟷ Council (2026-06-04) — **COMPLETE, reconciled-to-zero**

Evals: `03-codex-advisor/{advisor-eval,codex-eval,SYNTHESIS}.md`. Council responses: `round3-codex-advisor-responses/c{8,2,3,5}.md`.

- **Decorrelated convergence (decisive):** advisor (in-family) + Codex (out-of-family, fresh) INDEPENDENTLY flagged the same #1 — **the PLAN optimized byte-count, not DRIFT.**
- **Out-of-family-only catches (Codex):** CA-2 governance-native-bloat irony (the de-bloat plan is itself bloat-prone); CA-3 verify-before-evict.
- **advisor↔Codex disagreement (resolved toward Codex):** CA-4 — advisor said drop "X" to detect-only; Codex said minimal-recoverability is load-bearing (store not git-versioned → unrecoverable). Adopted: minimal-recoverability-now in MVP; locking deferred.
- **Council dispositions (Stage 3b, targeted 4-voice):** all ACCEPT; zero genuine REBUT (C5's "rebut" = a scope-pin keeping G1 a deterministic byte-sum, ceding attention-modeling to C2/C8). Cross-coherence: all COHERE (C3's CA-6↔G1 duplicate-gate risk resolved-by-composition; C5 cedes attention to C2).
- **The transformation:** C8 (NEW eval voice) added **WS-0 "Drift definition + use-the-product probe" as the PLAN's success GATE** (6-class binary drift taxonomy; counterfactual before/after probe; Robert = human floor; byte≤cap demoted to leading-indicator). The plan is now a falsifiable drift-reduction plan, not a context-slimming plan.

| CA | Disposition | Owner |
|---|---|---|
| CA-1 drift-disconnect | ACCEPT → WS-0 success-gate + keep/position WS + reframe | C8 + C2 |
| CA-2 governance-bloat irony | ACCEPT (orchestrator anti-bloat filter; MVP minimal; defer hard) | all |
| CA-3 verify-before-evict | ACCEPT → WS-1 precondition (dependency-scan + versioned archive) | C2 |
| CA-4 memory rollback load-bearing | ACCEPT → minimal-recoverability MVP; locking deferred | C3 |
| CA-5 G1 guardrail-not-religion | ACCEPT (scope-pinned to @import-closure byte-sum; warn-then-fail; override) | C5 |
| CA-6 MEMORY.md retention → MVP | ACCEPT (session-loaded → MVP) | C3 |
| CA-7 reconciled≠correct | ACCEPT → falsifiability clause in DESIGN.md | C8 + orchestrator |

**Convergence status:** Codex + advisor ⟷ Council **reconciled-to-zero** (loop step-4 gate MET). **Next: loop step 5 — adversarial #2 gate (focused residual sweep) on the candidate `DESIGN.md` → then commit.**

---

## Round 4 — Adversarial #2 gate (2026-06-04) — **CLEAR-TO-COMMIT**

Verdict: `02-adversarial/REVIEW-2-gate.md`. Single bounded reviewer (the process honored CA-2's "collapse Stage-4" — not a fan-out).

- **Verdict: CLEAR-TO-COMMIT.** DESIGN.md closes the loop structurally, not nominally.
- **CA/AR closure:** all CA-1..CA-7 + AR-1..AR-9 CLOSED (gate verified each against DESIGN.md).
- **WS-0 falsifiability:** SOUND — pressure-tested on all 4 axes (counterfactual baseline, binary taxonomy, human grader, two-way-failable pass condition). "A real gate that can fail, not ceremony."
- **Anti-bloat self-application:** PASS (DESIGN.md ~115 lines; 7-row MVP; deferred tail large-on-purpose; + the gate process itself collapsed to one reviewer).
- **New Class-1:** none. Empirical claims re-verified at HEAD (MEMORY.md 27,051B; zero `@import`; store not-a-git-repo; §12.5.1 quote verbatim; `research §2.2.2` cite real).
- **One residual (Class-3, folded not punted):** the C8 grader-blinding clause dropped between Round 3 and DESIGN.md §3 → **restored** (de-identify/shuffle arm labels before grading). DESIGN.md is now zero-residual.

**LOOP COMPLETE.** adversarial#1 → adversarial⟷council (+cross-cutting) → Codex+advisor → codex/advisor⟷council → adversarial#2 gate — all pairwise gates reconciled-to-zero. **`DESIGN.md` is the committed deliverable**, handed off for a downstream execution arc (validated by the WS-0 probe, not by reconciliation).

---

## Round 5 — Evidence-enrichment (2026-06-04) — ARC REOPENED

Fresh research landed in `03-evidence/` (4 docs). Council reconvened (C2/C3 primaries + C1/C5/C7/C9 + **C8**) to fold it into `DESIGN.md` v1 → v2 through the full §5 loop. Operator clarified the convening cadence mid-round: **primaries first (A1, independent) → consultants introduced to react (A2) → seam-routed cross-read DEBATE (Phase B); halt at a gate before the full council convenes; phases run as separate workflows with orchestrator checkpoints.**

### E1 — Council deliberation #2 (`DELIBERATION-2-evidence.md`) — COMPLETE, reconciled-to-internal-zero

- **A1 primaries** (`wf_07c07c77-82b`): C2 + C3 independent. **Both resolved the spine (proportionality-vs-canon) toward PROPORTIONALITY** — mostly citation/confirmatory; C2 = 2 WS-2a sharpens (self-corrected own prior over-listing); C3 = 1 supersede-mark earner + set-aside the episodic/semantic dir-split on its own repo-empirical degree-tiering.
- **A2 consultants** (`wf_db74601a-68d`): C1/C5/C7/C8/C9 reacted to the primaries (formulaic-concurrence-rejected held — each refused the bloat its *own* lane was most tempted by). **Convergent finding:** C3/C7/C9/C1 independently surfaced the *unobservable-trigger* seam. C8 collapsed Dive-5's threshold tier under one defeater ("presupposes a judge WS-0 deletes") + surfaced the **WS-0 base-rate vacuity** original finding.
- **Phase B** (`wf_8fb2e418-cfe`): seam-routed cross-read DEBATE. B1 (C7) closed the unobservable-trigger seam (single 3-integer SessionEnd health-line rider; WS-5 stays deferred; C8-relief drops 2 signals to the gate). B2 (C5) closed the unified-gate seam (G-LINK → DEFER→MVP-on-trigger; L1 → WS-1; κ/TPR/TNR dropped). C2 + C3 confirm-back: **all ACCEPT / ACCEPT-WITH-REFINEMENT; ZERO CONFLICT.**

**Spine verdict:** all 7 voices resolved toward proportionality independently → ~8 small MVP sharpens (all riders of existing workstreams) + 1 deferred trigger-gated gate (G-LINK); long explicit canon-refusal list. The de-bloat effort did not become governance-bloat.

**E1 tensions:**

| T-ID (R5) | Parties | Status after E1 |
|---|---|---|
| unobservable-trigger | C3 ↔ C7 ↔ C9 ↔ C1 | **CLOSED** — single 3-integer SessionEnd health-line rider on WS-3a (NOT WS-5); C8-relief drops D1-fire + D5 signals to the WS-0 gate columns |
| unified-gate | C5 ↔ C2 ↔ C3 ↔ C8 ↔ C9 | **CLOSED** — G-LINK DEFER→MVP-on-trigger; L1 deterministic assertion → WS-1 verify-before-evict; κ/TPR/TNR/L2/L3 dropped (no-judge defeater) |
| supersede-mark binding | C3 ↔ C5 | **CLOSED** — MVP-without-G-LINK but names it a trigger (asymmetric bind: write-discipline now / validator on-promotion) |
| consolidation placement | C1 ↔ C3 | **CLOSED** — synchronous SessionEnd write-event (C1 fires / C3 fills Tier-4), observed-D4 trigger not episode-cadence; no daemon, no C9 |
| FM-H topology-class | C1 ↔ C3 ↔ C9 | **CLOSED** — decentralized-handoff (no lead) → serialization at store-level OCC + git-as-state; corrects false §12.5.1 claim |
| navigation guardrail | C2 ↔ C1 | **CLOSED** — closed anchor list + do-not-invent (C2) + do-not-author-WORKFLOWS.md (C1); un-anchored INDEX MVP floor |

**Residuals routed to E2 (genuinely open):** (1) C8 base-rate floor (minimum-exposure vs annotate); (2) dormant-G-LINK reinject-pointer gap (standing pointer = the one MVP-now trigger?); (3) anti-bloat self-application of the v2 aggregate; (4) C7↔C11 dashboard-sequencing (low-stakes).

**Convergence status:** E1 reconciled-to-internal-zero (primaries↔consultants closed; zero CONFLICT). **Next: E2 — `harness-adversarial-reviewer` (genuine invocation) red-teams the reconciled E1 + integration plan → `02-adversarial/`** (Round-5 review docs).

### E2 — Adversarial #1 (`02-adversarial/REVIEW-3-evidence-r5.md`, `wf_34b95aca-d0b`) — COMPLETE

**Verdict: CLEAR-to-E2b-reconcile.** Single bounded reviewer (genuine `harness-adversarial-reviewer`). **3 Class-2 in-arc revisions + 2 Class-1 nits + 0 Class-3.** Cite-verification **CLEAN** (WebFetch-verified ICM=arXiv:2603.16021v2 byte-exact; grep-verified `session-end-cleanup.sh`, `postcompact-reinject.sh`, `CLAUDE.md:651` §12.5.1, the EVID counts, the live cross-store drift). **Missed cross-cutting tensions: NONE** — the cross-read genuinely closed the seams (reviewer notes the prior arc's adversarial caught 2 *because* the isolated voices had not cross-read; this round they did). **9-item checklist: 8 PASS / 1 FLAG** (item 4 → F2-01). **Meta-attack tested + rejected (R-9):** "8 MVP sharpens" is NOT disguised over-adoption — every item maps to a drift class; 5 of 8 are riders of existing workstreams; zero new MVP workstreams; the one new mechanism (G-LINK) is DEFERRED. The proportionality discipline held in the artifact, not just asserted.

**The 3 Class-2 findings E2b (council) must reconcile — all *name-this*, no machinery:**
- **F2-01 (C5×C9):** residual (b) — resolve toward **dormant-G-LINK-is-fine**; **name the reinject-pointer self-check as an explicit MVP recovery deliverable** in DESIGN.md v2 §6 (already true at HEAD — `postcompact-reinject.sh:28` conditional guard; do NOT build G-LINK). [checklist item-4 catch]
- **F2-02 (C8):** residual (c) — the SessionEnd line closes (R-1); the **real surface is WS-0 §3 gate-accretion** — C8 adds one sentence affirming the codebook-lens (E-4) + base-rate rule (E-5) are annotations on an **unchanged** manual step (one matrix / Robert's eyes / zero new tooling).
- **F2-03 (C8):** residual (a) — hold **annotate-not-floor**; **name D6's residual base-rate blindness** as a known WS-0 limitation (distinct from D4, which the ≥4-ref health-line inventory partially mitigates).

**2 Class-1 nits (fold when MVP-3 lands; no E2b debate):** F1-01 (`session-end-cleanup.sh` cite `:49-53`→`:49-58`); F1-02 (state the canonical 3 health-line integers; note they supersede EVID Finding-4's illustrative orphan%/density/true-break triple). **+1 confirming line:** C7 to confirm-back that C2's deferred-generator/un-anchored-INDEX floor discharges C7's T3 legibility-lien.

**Convergence status:** E2 CLEAR-to-E2b. **GATE HELD before E2b** (the council re-convenes to respond to F2-01/02/03) per the operator's "halt before the full council convenes" directive — awaiting operator go-ahead.

### E3 — Codex + advisor handoff (`03-codex-advisor/{advisor,codex}-eval-r5.md`) — COMPLETE

**Operator reorder (2026-06-04):** "go ahead, convene E3" — the charter puts E2b (council reconcile) *before* Codex/advisor; the operator directed E3 next. Resolution: **gather all decorrelated reviewer input first (adversarial E2 + Codex + advisor), then ONE consolidated council reconcile** against the full set (preserves reconcile-to-zero; defers E2b into the consolidated step). Operator also directed: **advisor authors a descriptive research primer for Codex** (Codex is out-of-family, no history) — done; the primer is research-only (decorrelation discipline: no Claude-family conclusions handed to Codex; the adversarial findings + advisor eval were withheld so Codex reads cold).

- **advisor (in-family, transcript-aware):** Concur with CLEAR. Proportionality genuine (demonstrated on the artifact: 5/8 riders, G-LINK deferred, meta-attack rejected). F2-01/02/03 dispositioned correctly. **Surfaced the under-pressed question both Claude-family reviewers missed: is the heavy ~15–25-session WS-0 probe actually going to be RUN by a solo dev, or does the slim ship on faith with a decorative gate? — a "minimum viable gate" floor may be the proportionate move.** Deliberately NOT pre-empted in Codex's prompt.
- **Codex (out-of-family gpt-5.5, $0 subscription, cold read):** **SOUND-WITH-FIXES** (no P0). 5 findings — and it **earned its decorrelation**: [P1] D4/D6 exposure-floor (diverges from adversarial's "annotate-not-floor" → "minimum exposure OR mark incomplete"; CONVERGES with advisor's flagged concern); [P2] carry degree-keyed tiering (pin ≥5 / keep 1–4 / archive 39) explicitly into WS-3a (Codex-UNIQUE); [P2] promote the 2 already-triggered ≥4-ref consolidation patterns to MVP one-time hygiene (Codex-UNIQUE); [P2] minimal resolver check for standing recovery/supersede pointers MVP-now (diverges from F2-01's dormant-is-fine — the `[ -f ]` guard handles absence, not cross-store drift live at HEAD); [P3] scope L1 to WS-1-dependency-scan invariants, not the hard-coded `[i]` example.

**Three-way signal (per advisor's "weight where Codex disagrees"):** all three reviewers converge on the **WS-0 rare-class (D4/D6) vulnerability** as the decisive open risk — but **diverge on the fix** (adversarial: annotate; Codex: exposure-floor-or-incomplete; advisor: minimum-viable-gate-floor). Codex additionally surfaced **3 P2s the Claude-family reviewers missed** (degree-tiering-into-WS-3a; already-triggered-consolidation-MVP; standing-pointer-resolver-MVP). The out-of-family read paid off.

**Consolidated reconcile inputs (what E3b/the council must reconcile — adversarial + Codex + advisor merged):**
1. **WS-0 rare-class floor** (P1 + F2-03 + advisor) — C8: annotate vs minimum-exposure-floor vs mark-incomplete. *(3-reviewer convergence; the highest-value item.)*
2. **Standing-pointer resolver MVP-now?** (P2 + F2-01) — C9/C5/C3: dormant-G-LINK + `[ -f ]` self-check vs a minimal MVP-now resolver for standing recovery/supersede pointers.
3. **Degree-keyed tiering into WS-3a MVP** (P2, Codex-unique) — C3/C2.
4. **Already-triggered consolidation → MVP one-time hygiene** (P2, Codex-unique) — C1/C3.
5. **L1 scoping to dependency-scan invariants** (P3) — C2/C5/C8.
6. **F2-02 WS-0 gate-accretion re-affirmation** (adversarial) — C8 one-sentence proportionality assertion.
7. Class-1 nits F1-01 (cite range) + F1-02 (canonical 3 health-line integers) — fold, no debate. **+ C7 T3-lien confirm.**

**Convergence status:** E2 + E3 complete; all reviewer input gathered. **GATE HELD before the consolidated council reconcile** (the next full-council event) per the operator's standing "halt before the full council convenes" directive — awaiting go-ahead.

### Consolidated council reconcile (`round5-consolidated-responses/c{8,9,3,5,2,7}.md`, `wf_be40ac24-ebe`) — COMPLETE, reconciled-to-zero

The council genuinely responded to the merged adversarial + Codex + advisor findings in 3 dependency-ordered waves (C8+C9 → C3+C5 → C2+C7). **Every disposition ACCEPT or RECONCILE-with-refinement; the divergences resolved on the merits; zero unresolved CONFLICT.** Codex's out-of-family findings all landed as real refinements — it earned its keep.

| Item | Voice | Disposition | Net change to DESIGN.md v2 |
|---|---|---|---|
| **1 — WS-0 rare-class D4/D6** | C8 | RECONCILE | **NEW verdict value `INCOMPLETE-on-{D4,D6}`** when a rare class is unexercised in both arms (never a clean SOUND; operator-waiver path). **REBUT the minimum-exposure floor** (CA-2 bloat — "report coverage, don't force it"; = advisor's minimum-viable-gate). FOLD D4-vs-D6 asymmetry (D4 has the ≥4-ref standing signal; D6 has none). Zero new tooling. |
| **6 — F2-02 gate-accretion** | C8 | ACCEPT | One §3 sentence: E-4 codebook + E-5 cell-rule + the INCOMPLETE label are all reads off the one matrix — WS-0 stays one-matrix/Robert's-eyes/zero-tooling. |
| **2 — standing-pointer resolver** | C9 (×C5,C3) | REBUT(MVP-now)/RECONCILE(requirement) | **Dormant-G-LINK + `[ -f ]` absence-guard SUFFICIENT at MVP** (adversarial repo-grep proved the reinject pointer resolves at HEAD; Codex conflated the *memory-note* drift with the reinject pointer). NAME reinject-pointer-resolvability as an MVP recovery deliverable (§6); route cross-store-drift to the link-`--check` when live. **No G-LINK pulled to MVP.** Codex's absence-vs-resolution *distinction* right; *surface*+*timing* wrong. |
| **3 — degree-keyed tiering** | C3 (×C2) | RECONCILE | **FOLD the degree selection RULE into WS-3a** (KEEP-HOT ≥5 / KEEP-LINKED 1–4 / ARCHIVE-JIT the 39 zero-inbound); HOLD the dir-split set-aside; **REBUT any in-degree compute engine** (grep-by-eye). Thresholds operator-tunable against a *moving* count (C2 grep: top hub 65→83). |
| **4 — already-triggered consolidation** | C3 (×C1) | ACCEPT | **NEW one-time MVP hygiene:** write the 2 dangling ≥4-ref pattern bodies (`plan-revision-against-not-yet-built-substrate`, `strike-revision-on-refined-second-tier-reason` — both 5 refs / no note file at HEAD). The *recurring* consolidation mechanism stays DEFERRED (trigger already at zero for these 2). |
| **5 — L1 scoping** | C5 (×C2,C8) | ACCEPT | L1 asserts **WS-1-dependency-scan-discovered invariants**, NOT the hard-coded `[i]` example (demotes to a form-illustration); home unchanged (WS-1 precondition; C5 authors, C2 hosts; judge-free). Net anti-bloat. **Routing correction:** rides the `[ -f ]` guard / G-LINK target-class, NOT G1 (byte-budget ≠ link-integrity). |
| **7 — T3-lien + F1-02** | C7 | CONFIRM | The un-anchored `artifact→version` INDEX **discharges C7's T3 legibility-lien** (lien = version-discoverability, not `#section`-precision). F1-02: the 3 integers (`notes-superseded`/`notes-untouched->Ndays`/`patterns-unwritten->=4-refs`) are canonical and **supersede** EVID's illustrative orphan%/density/true-break triple. SessionEnd line stays exactly 3 integers on both wave rulings. |

**Residuals carried to E4 (adversarial #2) — all minor watch-items, no open CONFLICT:**
1. The reinject pointer + `superseded_by` surface should share the **same** link-`--check` input set when G-LINK promotes (C9+C3 — a one-line §6 scoping note, not a workstream).
2. C5's home-correction: the recovery-pointer requirement rides the `[ -f ]` guard / G-LINK target-class, **not G1** — E4 verify the §6 wording doesn't conflate them.
3. **Anti-bloat watch** (F2-02-adjacent, raised by C3+C2+C7): verify the new folds stay *rules/one-shots* — the degree-key stays grep-by-eye (not a daemon); the one-time hygiene stays a finite write (not the recurring pass); L1 stays a one-shot precondition (not a standing CI gate); the INCOMPLETE verdict stays a matrix read (not new tooling); the 3-integer line doesn't accrete to 5.
4. F1-01 (`session-end-cleanup.sh:49-53`→`:49-58`) + F1-02 canonical triple — fold when MVP-3 lands.

**Convergence status:** consolidated reconcile **reconciled-to-zero** (adversarial⟷council + codex/advisor⟷council both closed in one pass per the operator reorder). **Next: E4 — adversarial #2 gate** (single bounded reviewer; residual sweep on the reviewer-resolved plan) → then enriched `DESIGN.md` v2. E4 is a single reviewer, NOT the full council — does not trip the council-convening gate.

### E4 — Adversarial #2 gate (`02-adversarial/REVIEW-4-gate-r5.md`, `wf_de7a33be-c4e`) — COMPLETE → CLEAR-WITH-FOLD → folds applied → CLEARED-TO-COMMIT

Candidate `DESIGN.md` v2 was written (all 7 consolidated dispositions folded) and gated by a single bounded reviewer. **Verdict: CLEAR-WITH-FOLD** (no LOOP-BACK; no Class-1/2 open). Absorption check **COMPLETE** (all 7 dispositions absorbed; all 4 routed residuals closed in v2 text). Anti-bloat self-application: **5/5 PASS** (degree-key stays grep-by-eye; one-time hygiene stays a finite 2-note write; L1 stays a one-shot precondition; INCOMPLETE stays a matrix read; health-line stays exactly 3 integers — verified in the actual fold text, not just the §9 assertion). `INCOMPLETE`-verdict **falsifiability SOUND** (pressure-tested on 4 axes — it can genuinely return INCOMPLETE and block a clean SOUND; the D4-vs-D6 asymmetry is empirically grounded; "report-don't-force" protects-not-relabels; proportionate). Meta-attack (R-10: is "8 folds" disguised over-adoption?) re-tested on v2 and REJECTED (6-row MVP unchanged; every fold a rider/one-shot; only-new-mechanism G-LINK deferred).

**2 folds applied at commit (both §4.1-Class-1 drift / §2.7.6-Class-3 informational — neither loops the arc):**
- **F-G1 (material reframe):** the §5 WS-3a "over-cap now (27,051B)" premise was **stale at HEAD** — `wc -c` = **10,306B / 45 entries** (mtime 06:27 today): an **ad-hoc lossy compaction dropped ~75 index entries mid-session** (≈120 → 45). Per the gate's decisive ruling, **the falsifying event is itself a live D4 incident that REAFFIRMS WS-3a** (the enforced/non-lossy/supersede-mark contract exists to replace exactly that silent lossy drop). Folded as a **reframe** (NOT a number-bump, which would invert the headline to self-defeating): WS-3a's MVP inclusion now rests on byte-count-**independent** triggers verified live at HEAD — the 2 dangling ≥4-ref patterns (5/5, no note file — **I re-verified: both files absent**) + the store-not-git-versioned gap. *(This is the workspace's own stale-carry / sibling-staleness defect class, caught by the gate's mandated re-verify-at-HEAD — the arc's discipline catching itself.)*
- **F-G2 (trivial cites, re-verified at HEAD by orchestrator):** `session-end-cleanup.sh:49-58` → **`:49-56`** (`## MEMORY.md cap` at :49, block-close `}` at :57); `postcompact-reinject.sh:28` → **`:30`** (`:28` is the `CK=` assignment; the `[ -f "$CK" ]` absence-guard is at `:30` — confirmed by `sed`).

**LOOP COMPLETE.** Round 5: council deliberation #2 (A1 primaries → A2 consultants → Phase-B cross-read) → adversarial #1 (E2) → Codex (out-of-family) + advisor (in-family) (E3) → consolidated council reconcile → adversarial #2 gate (E4 CLEAR-WITH-FOLD) → folds applied + re-verified → **`DESIGN.md` v2 CLEARED-TO-COMMIT**. ~24 genuine agent invocations across the round + 2 decorrelated evaluators (advisor + Codex); every reviewer/voice genuinely invoked; every pairwise gate reconciled-to-zero. The proportionality-vs-canon spine held end-to-end (zero new MVP workstreams; the one new mechanism G-LINK deferred). Handed off for a downstream EXECUTION arc (validated by the WS-0 probe + its INCOMPLETE-on-rare-class verdict, not by reconciliation).

# Phase 8 Graduation — Substitution Accounting CLOSED

**Status:** ✅ **DECLARED** 2026-06-02 (operator lifted the HELD R-700 declaration).
**Authority:** `R-700-phase-8-substitution-accounting` (roadmap Surface VIII). Operator AskUserQuestion 2026-06-02 (PR #246) ratified 3 of 4 PART C items; this declaration executes item 4 (the formal close) on operator instruction to "kick off the declaration."
**Source accounting:** `.harness/R-700-phase-8-closure-accounting-draft.md` (PART A 54-row substitution log + §A.6 reconciled tally + PART C ratifications). This document is the canonical Phase-8 closure record; the draft is its working derivation.
**Closes:** Phase 7 (substitution-retirement execution). The H_E → H_T substitution gradient is accounted to completion under the X-AL-2 retirement criterion.

---

## 1. The two ratified integers (canonical going forward)

> Phase 8 graduates the **substitution accounting**, not "every capability exercised in production." Production exercise was never an X-AL-2 retirement condition (X-AL-2 = *cited units landed* ∧ *substituted H_E surface no longer invoked at the substitution site*). Many capabilities are library-complete and deliberately unexercised at the LOCAL_DEVELOPMENT MVP; that is the **post-Phase-8 activation/deployment/integration axis** (Surfaces IV/V/VI; roadmap §5.10–§5.14), not a Phase-7 gap.

| Metric | Canonical value | Notes |
|---|---|---|
| **RETIRED** | **46 / 54 (85.2%)** | accounting (i), operator-ratified (PART C item 1). The published `48/54` over-counted by 2 (un-folded CXA accounting per ledger §11.1a line 278 + the CP-17 SB-INDEF reclassification + the CP 21-vs-22 / AS-3↔AS-9 bookkeeping ambiguities). **No work regressed** — every delta is a known-deferred or bookkeeping surface. |
| **Pipeline-advanced** (RETIRED + RETIRE-READY + PARTIAL) | **49 / 54 (90.7%)** | matches the one published figure that survives reconciliation. |

**These two integers are the canonical Phase-8 headline.** The published `48/54` is superseded forward (per the forward-only ledger discipline at workspace `CLAUDE.md` §4.3 — prior batch records stand verbatim; this document is the forward supersession authority).

---

## 2. The literal must_pass gate — all 49 Meta-Architecture §5 rows accounted

The roadmap `R-700` verification gate is literally *"all 49 rows of Meta-Architecture §5 accounted"* + *"each RETIRED-AS-BOUNDED-RESIDUAL has documented operator rationale."* The §5 substitution table declares **49** entries (`Phase_7_Meta_Architecture_v1.md` §5.7, preserved verbatim through v1.5); per-axis (`CLAUDE.md` §4.1): **IS=9 / AS=6 / CP=21 / OD=8 / CXA=5 = 49**.

| Axis (Meta-Arch §5 view) | Rows | Accounting |
|---|---|---|
| IS (§5.2) | 9 | 9 RETIRED (100%) |
| AS (§5.3) | 6 | 4 fully RETIRED (AS-1/2/4/5) + AS-9 RETIRED-AS-AUTHORING-ONLY + **AS-8 (monolithic)** = 4-of-6 namespaces RETIRED (anthropic/mcp/memory/skill) + 2 namespaces indefinite-deferred (files / managed_agents) |
| CP (§5.4) | 21 | 21 RETIRED (17 substantive + 3 authoring-only + 1 bounded-residual = CP-16); CP-17 (files-primitives) indefinite-deferred |
| OD (§5.5) | 8 | 7 RETIRED (3 substantive + 3 authoring-only + 1 bounded-residual = OD-6) + OD-4 cross-axis-deferred |
| CXA (§5.6) | 5 | CXA-5 RETIRED; CXA-1/CXA-4 PARTIAL; CXA-2/CXA-3 STILL-BOUNDED (all Phase-2-runtime-deferred) |

**49-row gate: SATISFIED** — every §5 row has a disposition (RETIRED or a documented terminal sign-off, §4).

**Reconciliation to the 54-row ledger view.** The ledger-v2 view is **54** rows: the 49 Meta-Arch rows with `AS-8` decomposed into `AS-8a..AS-8f` (+5) at batch-24. `49 + 5 = 54`. The §A.6 reconciled tally (below) operates on the 54-row view; the 49-row gate above is its Meta-Arch projection. Both are satisfied.

---

## 3. The 54-row reconciled tally (operative accounting — accounting (i), ratified)

Reproduced from `R-700-...-draft.md` §A.6 (operator-ratified accounting (i): canonical CP = drop the CP-axis-local authoring extra `CP-24`; `CP-17` SB-INDEF stays inside the 54).

| Disposition class | Rows | Counted in RETIRED 46? |
|---|---|---|
| substantive-RETIRED | **36** | ✅ yes |
| RETIRED-AS-AUTHORING-ONLY | **8** (IS-4, IS-10, AS-9, CP-12, CP-23, OD-1, OD-7, OD-8) | ✅ yes |
| RETIRED-AS-BOUNDED-RESIDUAL | **2** (CP-16, OD-6) | ✅ yes |
| **→ Total RETIRED** | **46** | **the canonical integer** |
| PARTIAL | **3** (OD-4, CXA-1, CXA-4) | ❌ no (in pipeline-advanced 49) |
| STILL-BOUNDED | **2** (CXA-2, CXA-3) | ❌ no |
| STILL-BOUNDED-INDEFINITELY | **3** (AS-8e, AS-8f, CP-17) | ❌ no |
| **GRAND TOTAL** | **54** | 36 + 8 + 2 + 3 + 2 + 3 = 54 ✓ |

- **Pipeline-advanced = 46 + 0 + 3 = 49/54 = 90.7%.**
- **Non-pipeline-advanced = 5/54** (CXA-2/CXA-3 STILL-BOUNDED + AS-8e/AS-8f/CP-17 SB-INDEFINITE).

---

## 4. Terminal sign-off dispositions for the 8 non-substantive-RETIRED rows (PART C item 3, ratified)

**⚠️ Label ≠ count-membership.** The operator's PART C item-3 sign-off ratifies a terminal *disposition label* for each open row, recording *why* Phase 8 closes despite it. **A sign-off label does NOT re-tally into the RETIRED-46 integer.** Proof this is the correct reading: `OD-6` appears in the item-3 sign-off list **and** is already counted in the 46 (as RETIRED-AS-BOUNDED-RESIDUAL) — so "appears in the item-3 sign-off list" is orthogonal to "counted in the RETIRED integer." Two distinct uses of "bounded-residual" therefore coexist and must not be conflated:

- **Counted** `RETIRED-AS-BOUNDED-RESIDUAL` = CP-16, OD-6 (the 2 inside the 46; substrate landed, dormant at MVP, substantive close deferred to a real deployment surface per X-AL-2 §5.3).
- **Item-3 sign-off** "accepted-indefinite-defer (bounded-residual sign-off)" = AS-8e, AS-8f, CP-17 — **NOT counted** in the 46; they stay in the non-pipeline-advanced 5.

| Row | Terminal disposition label (ratified) | Count-membership | Rationale + pointer |
|---|---|---|---|
| **H_T-OD-4** | `RETIRED-AS-CROSS-AXIS-DEFERRED` *(NEW disposition class, PART C item 3)* | **pipeline-advanced PARTIAL — NOT in the 46** | OD-axis work done: gate (a) §13.1 per-session redaction toggle CLOSED (PR #244). Sole remaining gate (b) §13.2 opaque-token tokenization is **cross-axis** (`c10-action-safety` eval-grade pipeline, Phase-6+) → never OD-axis-Claude-closeable. R-008. |
| **H_T-AS-8e** | accepted-indefinite-defer (files.* namespace) | SB-INDEFINITE — NOT in the 46 | Files-arc Memory-only-MVP scope; runtime spec v1.17 §14.C indefinite-defer. R-005 (impl-bundled in R-810). |
| **H_T-AS-8f** | accepted-indefinite-defer (managed_agents.* namespace) | SB-INDEFINITE — NOT in the 46 | managed_agents production-only exclusion (runtime spec v1.33 AS-8f DEFER). R-006 (impl-bundled in R-820). |
| **H_T-CP-17** | accepted-indefinite-defer (files-primitives) | SB-INDEFINITE — NOT in the 46 | Files-arc indefinite-defer (batch-44, sub-species 7g). R-010 (impl-bundled in R-810). |
| **H_T-CXA-1** | Phase-2-runtime-deferred (AS→IS secret-fetch audit seam) | pipeline-advanced PARTIAL — NOT in the 46 | Typed seam wired+tested at 7c; zero production callers until an AS secret-fetch driver path lands. R-CXA-1 (grounded → DEFER-DON'T-WIRE, PR #220). |
| **H_T-CXA-4** | Phase-2-runtime-deferred (OD→multi seams) | pipeline-advanced PARTIAL — NOT in the 46 | 1 genuine typed seam wired (4 producers) + 19 convention + 6 phase-2-runtime; remaining edges deferred. R-CXA-4 (grounded → 0 wireable edges, CXA v2.19, PR #254-era). |
| **H_T-CXA-2** | Phase-2-runtime-deferred (CP→IS state-ledger seams) | STILL-BOUNDED — NOT in the 46 | 2 of 6 §16.5 composer methods fired; 4 of 6 gated by deliberately-STRUCK U-RT-111 X-AL-3 gaps (engine stubs + bootstrap-stage-ordering + HITL-disambiguator). R-CXA-2 (grounded → gates-on-engine-substrate, no wireable slice). |
| **H_T-CXA-3** | Phase-2-runtime-deferred (CP→AS runtime composer) | STILL-BOUNDED — NOT in the 46 | No runtime composer at MVP; closes via composer landing or Memory-only-scope canonical-narrowing (ledger §11.1b α/β). R-CXA-3 (deferred-by-design). |

**Every RETIRED-AS-BOUNDED-RESIDUAL row has documented operator rationale** (CP-16: memory-tool backend dormant at MVP, batch-44; OD-6: OTLP `flush_to_sqlite` dormant at MVP, batch-51 — FIRST bounded-residual close in the ledger) — the second must_pass clause is SATISFIED.

---

## 5. Disposition discipline notes

- **Forward-only supersession.** This declaration is the canonical-count authority going forward (RETIRED 46/54, pipeline-advanced 49/54). It does **not** rewrite historical batch footers (ledger §0.5 forward-only discipline) — the ledger §11.5 cumulative pointer, `harness-cp/CLAUDE.md` workspace-cumulative line, and the dashboard retirement table each gain a forward supersession pointer citing this document. Mirror precedent: ledger §11.1a CXA-5 supersession.
- **Council gate (`R-700 council_required: yes`) — convene SKIPPED, justified.** The accounting was ratified at the #246 AskUserQuestion; the one live cross-domain tension (OD-4's C10⊥C11 redaction gate — action-safety vs operator-loop) was already dispositioned at R-008 (gate (a) closed #244; gate (b) cross-axis-deferred). No nameable un-resolved tension remains for the declaration to settle, so per the §10.9 nameable-tension discriminator a convene would be ceremony. (Skip recorded, not silently dropped.)
- **X-AL-2 legitimacy.** 85.2% RETIRED + 90.7% pipeline-advanced is a *legitimate* Phase-8 close, not a shortfall: the 8 non-fully-RETIRED rows are all cross-axis-deferred (OD-4 + 4 CXA) or accepted-indefinite-defer (AS-8e/8f/CP-17) — none is an un-dispositioned open substitution. The X-AL-2 criterion (units landed ∧ H_E surface no longer invoked) is met for all 46 RETIRED rows; the remainder carry documented terminal dispositions.

---

## 6. Post-Phase-8 forward axis (for orientation — NOT Phase-7 gaps)

Phase 8 closes the substitution accounting. The forward work is **activation / deployment / integration**, tracked under the R-NNN discipline (roadmap §5.10–§5.14; `.harness/post-phase-8-forward-register.md`):

- **Surface IV (multi-LLM maturity):** R-300-routing-activation ✅ RESOLVED (PR #213); R-300-second-provider (live-creds-gated).
- **Surface V (multi-deployment):** R-410..R-440 sandbox/deploy/secrets (infra-gated). R-410's design half — the tier→mechanism execution-driver contract — is now filed as a Class 1 fork (`class_1_fork_sandbox_tier_no_execution_driver_contract.md`, PROPOSING, PR #256).
- **Surface VI (multi-tenant):** R-500 (live-gated on R-420).
- **Files / managed-agents integration:** R-810 (AS-8e + CP-17) / R-820 (AS-8f) — deferred-by-design.

These are not substitution rows and were never X-AL-2 conditions.

---

## 7. Provenance

| Event | Reference |
|---|---|
| R-700 closure-accounting draft authored | PR #207 (`d1eaf75`, 2026-06-01) — `R-700-...-draft.md` PART A + B |
| Reconciliation finding (`48/54` internally impossible; per-row 46) | draft §A.6 + Headline finding; root cause = un-folded CXA accounting (ledger §11.1a line 278) |
| Operator ratification (3 of 4 PART C items) | PR #246 (`165a0f4`, 2026-06-02) — AskUserQuestion: integer=46, CXA/CP-17 coverage closed, sign-offs ratified, declaration HELD |
| **Formal declaration (this document)** | **2026-06-02 — operator lifted the hold ("kick off the declaration"); item 4 executed** |
| Advisor pass (declaration arc) | confirmed 46 is the forced reading of the joint item-1+item-3 ratification (OD-6-in-both-lists tell); directed the label-vs-count-membership table + forward-only supersession |

**Phase 8: substitution accounting CLOSED. 46/54 RETIRED (85.2%), 49/54 pipeline-advanced (90.7%); 8 rows carry ratified terminal sign-off dispositions; zero un-dispositioned open substitutions.**

---

## §7 Forward supersession note (2026-06-08)

This document remains the historical Phase-8 declaration. A later post-Phase-8 accounting/back-flow arc opened the previously accepted-indefinite-defer Files and Managed Agents rows and live-proved them:

- R-810: AS-8e + CP-17 Files API / `files.*`
- R-820: AS-8f Managed Agents / `managed_agents.*`

Batch-52 (`.harness/phase-7d-retirement-events-batch-52.md`) moves those three rows from `SB_INDEFINITE` to `SUBSTANTIVE_RETIRED`. Batch-53 (`.harness/phase-7d-retirement-events-batch-53.md`) then moves OD-4 and CXA-4 from `PARTIAL` to `SUBSTANTIVE_RETIRED` after their runtime/bookkeeping residuals closed. The live substitution ledger therefore advances to **51/54 RETIRED** and **52/54 pipeline-advanced**. The Phase-8 close above is not rewritten; it is superseded forward for live counts by the post-Phase-8 retirement batches and `.harness/substitutions.yaml`.

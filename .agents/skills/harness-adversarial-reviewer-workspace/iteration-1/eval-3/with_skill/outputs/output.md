# Adversarial Review — Tension Record `Phase_7_Class_1_Tension_002_Topology_Pattern_Enum.md`

## Summary

- **Review type:** Adversarial review of a Phase 7 execution-time tension record (not one of the four checkpoint artifact types — ADR / ADD / spec / impl-plan). The `harness-adversarial-reviewer` discriminator-tree + V3-attack vocabulary is applied as the review instrument; the `Adversarial_Review_NN.md` template is used loosely, since the artifact under review is itself a finding-classified record, not a checkpoint deliverable.
- **Artifact reviewed:** `Phase_7_Class_1_Tension_002_Topology_Pattern_Enum.md`
- **Date:** 2026-05-15
- **Question put to the reviewer:** Does the record's **Class 1** finding classification hold up?
- **Verdict:** **The Class 1 classification holds.** The record correctly identifies a real, verbatim-confirmed three-way divergence and correctly routes it as halt-execution. Three strengthening notes follow; none of them downgrades the classification.
- **Disposition recommendation:** Classification **upheld**. Record is fit to drive an operator resolution decision, with two accuracy corrections (N-1, N-2) recommended as inline fixes and one framing tightening (N-3) recommended.

---

## Part 1 — Verification of the record's factual claims

The skill's workflow §2 discipline is "do not trust the artifact's self-description — verify against actual content." Every load-bearing claim in the record was checked against the design-substrate canonical copies.

| Record claim | Verification | Result |
|---|---|---|
| Set 1 = CP plan U-CP-22 signature `SINGLE_AGENT / SEQUENTIAL_HANDOFF / PARENT_FANOUT_AGGREGATE / RECONCILER_MESH / ROUTER_DELEGATE / PIPELINE_STAGES` | `Implementation_Plan_Control_Plane_v2_1.md` lines 1184–1192 (U-CP-22 `Signatures` block); v2.3 §2 confirms "U-CP-22 through U-CP-55 preserved verbatim from v2.2" | **Confirmed verbatim** |
| Set 2 = CP spec C-CP-10 §10.1 `single-threaded-linear / orchestrator-workers / decentralized-handoff / hierarchical-delegation / evaluator-optimizer / parallelization` | `Spec_Control_Plane_v1_2.md` §10.1 lines 840–845 (six-pattern taxonomy table); `Spec_Control_Plane_v1_3.md` line 229 confirms "§10 ... preserved verbatim from v1.2" | **Confirmed verbatim** |
| Set 3 = root `CLAUDE.md` §5 / CP-AL-1 `ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF / EVALUATOR_OPTIMIZER / PARALLELIZATION / ROUTING / SEQUENTIAL_PIPELINE` | root `CLAUDE.md` §5 line 230; `harness-cp/CLAUDE.md` §4.2 line 168; `Sub_Agent_Boundary_Specification_v1.md` §5.1 line 142; `Phase_7_Meta_Architecture_v1.md` §7.4 line 530 — all four sites carry the identical string | **Confirmed verbatim across all 4 sites** |
| "Three sets not reconcilable by case/format normalization" | Set 1 `RECONCILER_MESH` / `ROUTER_DELEGATE` / `PARENT_FANOUT_AGGREGATE` have no Set-2 or Set-3 counterpart under any casing; Set 3 `ROUTING` ≠ any Set-2 member | **Confirmed — genuine vocabulary divergence** |
| "Set 2 ∩ Set 3 = {orchestrator-workers, decentralized-handoff, evaluator-optimizer, parallelization}; Set 1 shares no member with either" | Set membership computed directly: correct | **Confirmed** |
| Spec C-CP-10 §10.3 gives an admissibility set differing from the plan's | `Spec_Control_Plane_v1_2.md` §10.3 lines 869–879 (hierarchical-delegation / decentralized-handoff / parallelization admissibility, Set-2 vocabulary) vs U-CP-22 acceptance #3 (Set-1 vocabulary) — patterns admissible-where genuinely disagree | **Confirmed — divergence is semantic, not only naming** |
| Authority chain: spec canonical over plan; C-CP-10 §10.1 traces to ADR-D4 v1.1 §1.1 | root `CLAUDE.md` §1.3 (ADR → ADD → PRD → spec → plan); `Spec_Control_Plane_v1_2.md` §10 ADR-commitment row cites "ADR-D4 v1.1 §1.1"; `ADR-D4.md` §1.1 lines 71–76 carry the six-pattern table in Set-2 vocabulary | **Confirmed — Set 2 is authority-chain-canonical** |
| Tiebreaker: confirm no ADR-D4 later than v1.1 | `ADR-D4.md` Status block: `Revision: v1 → v1.1`, Promotion P3c-CK 2026-05-11. No v1.2 exists in `design-substrate/`. ADR-D4 v1.1 §1.1 matches Set 2. | **Confirmed — tiebreaker does not invert; Set 2 stands** |
| U-CP-22 not yet implemented (halt is pre-code) | `harness-cp/src/harness_cp/` contains only `__init__.py`; no `TopologyPattern` symbol anywhere in workspace source | **Confirmed — halt surfaced before code execution, as §1 states** |

Every load-bearing factual claim in the record verified. The record does not fabricate, does not paraphrase from training data, and does not over-reach beyond the KB.

---

## Part 2 — Does the Class 1 classification hold?

### The classification is correct.

Per `Project_Workflow_v1_8.md` §2.7.6, the Phase 7 fork-classification table defines:

> **Class 1 (halt-execution)** — routing target: applicable design-phase channel (Phase 6 plan revision / Phase 5 spec revision / ...); mechanism: halt Phase 7 sub-phase execution; re-issue design-phase artifact; re-load.

The record's defect satisfies the Class 1 criterion on every dimension:

1. **Halt is warranted.** U-CP-22 acceptance #1 requires `TopologyPattern` "declares exactly six values per C-CP-10 §10.1 verbatim" (`Implementation_Plan_Control_Plane_v2_1.md` line 1205). The plan's own `Signatures` block declares Set-1 vocabulary, which is *not* verbatim from §10.1 (Set 2). The unit's plan signature **cannot be materialized in a way that satisfies its own acceptance #1**. This is not an implementer-discretion gap that code can resolve — it is a contradiction internal to the canonical plan. Proceeding would mean implementing against a self-contradicting unit. Halt is correct.

2. **Resolution requires design-phase artifact revision.** Resolving the defect requires editing `Implementation_Plan_Control_Plane_v2_3.md` (a Phase 6 artifact) and reconciling the CP-AL-1 verbatim text in three governance docs. This is the discriminator-(b) shape from the `harness-adversarial-reviewer` severity tree ("requires revising an artifact filed in a phase prior to the current phase") — applied to the Phase 7 fork table, it lands as Class 1. Not Class 2 (Class 2 is an in-session operator decision with no artifact revision); not Class 3 (Class 3 is informational and non-blocking).

3. **The defect is non-determinate at the symptom level and touches a load-bearing rule.** The record correctly notes that CP-AL-1 (which embeds Set 3) is named in `CLAUDE.md` §5 as the boundary's load-bearing anti-leakage rule, so the revision scope is multi-artifact and governance-touching. That is a real reason the fork cannot be silently absorbed.

The skill's worst-failure-mode framing — **silent absorption of a design-phase defect** (`CLAUDE.md` §4.3; SKILL.md FM-G "Smoothing") — is exactly what a Class 1 halt prevents here. Had the unit been implemented by picking one vocabulary silently, every downstream D4 unit (U-CP-23 onward, which import `TopologyPattern`) would have been built against an arbitrarily-chosen enum, and the spec/governance divergence would have propagated unresolved. The record's instinct to halt is sound.

### No severity-inflation (FM-A) and no severity-deflation (FM-B).

- **Not inflated.** The defect is genuinely blocking — a contradiction inside the canonical plan, not cosmetic drift. Class 1 is not an over-call.
- **Not deflated.** A reviewer tempted to call this Class 2 ("just an operator decision") would be wrong: the decision cannot be recorded and execution resumed without *also* revising artifacts, which is the Class 1 discriminator. The record resists that deflation correctly.

---

## Part 3 — Strengthening notes (classification stands; these refine the record)

### N-1 — The plan's §10.2/§10.3 citation is itself a second drift the record under-states

- **Location:** record §4 step 2 ("acceptance #3 admissibility matrix → align to spec §10.3"); against `Implementation_Plan_Control_Plane_v2_1.md` U-CP-22 acceptance #3 and `Implements:` line 1174.
- **Observation:** U-CP-22 `Implements:` cites `[C-CP-10 §10.1, §10.2, §10.3]`, and acceptance #3 states the admissibility matrix is "per §10.2 admissibility matrix." But in the spec, **§10.2 is "Workflow-definition surface declaration"** and the admissibility matrix actually lives at **§10.3** (`Spec_Control_Plane_v1_2.md` §10.3 "Cross-pattern admissibility per workload class"). The record's §4 recommendation to "align to spec §10.3" is correct — but the record presents this only as a vocabulary-alignment task and does not surface that the plan's own *section pointer* (§10.2 vs §10.3) is a separate citation drift. The divergence between plan and spec is one layer deeper than the record states: it is (a) vocabulary, (b) admissibility semantics, **and (c) section-number mis-citation**.
- **Why it matters:** an operator resolving this from the record alone would fix the vocabulary and the admissibility set but might leave the §10.2 pointer wrong. Surface (c) explicitly.
- **Discriminator:** classification-neutral. Does not change Class 1; it is an accuracy gap *inside* a Class 1 record.

### N-2 — Acceptance-criterion cross-references in record §2 are slightly loose

- **Location:** record §2, paragraph beginning "The divergence is also semantic..."; the parenthetical attributes the admissibility matrix to "U-CP-22 acceptance #3."
- **Observation:** This is correct (acceptance #3 *is* the admissibility criterion). But §2's earlier sentence says the three sets diverge and §3 says "acceptance #1 requires the enum 'per C-CP-10 §10.1 verbatim'" — also correct. The looseness is only that the record never states acceptance #2 exists (`CascadePolicy` "per §10.3 verbatim" — and `CascadePolicy` has its *own* divergence: plan declares `COMPLETE_ALL / CANCEL_ON_FIRST_FAIL / PAUSE_ON_FIRST_FAIL`, spec §10.3 references `cascade_policy` only via `pause / proceed / cascade-cancel` in the §10.2 `TopologyDeclaration`). The record scopes itself to `TopologyPattern` and is silent on whether `CascadePolicy` is in or out of the halt.
- **Why it matters:** U-CP-22 declares *two* enums plus a predicate. If `CascadePolicy` also diverges (it appears to), the operator should know whether the resolution covers it. The record should state explicitly: "this tension is scoped to `TopologyPattern`; `CascadePolicy` divergence is [in-scope / separately tracked / not assessed]."
- **Discriminator:** classification-neutral. A scoping-completeness gap, not a misclassification.

### N-3 — "design-authority decision, not a determinate fix" is slightly overstated

- **Location:** record §3 ("Resolution requires choosing the canonical 6-pattern vocabulary — a design-authority decision, not a determinate fix") and §4 ("operator decision required").
- **Observation:** Per `CLAUDE.md` §1.3 the authority chain is determinate: ADR > spec > plan. The record's own §4 proves this — Set 2 wins because it traces verbatim to ADR-D4 v1.1 §1.1, and the tiebreaker check confirms no later ADR-D4 exists. So the *choice of canonical vocabulary* is mechanically determinate (Set 2), not genuinely open. What actually requires operator sign-off is the **multi-artifact revision scope** — editing the canonical plan and rewriting CP-AL-1 verbatim text in three governance docs including the "most load-bearing rule at the H_E ↔ H_T boundary." That is an authorization gate, not a design-decision gate.
- **Why it matters:** The record reads as if the canonical vocabulary is up for grabs. It is not — the record itself recommends Set 2 with a sound authority-chain argument. Reframing §3/§4 as "the resolution direction is determinate (Set 2 per authority chain); operator authorization is required for the multi-artifact revision scope because CP-AL-1 is load-bearing" is more precise and gives the operator a cleaner decision.
- **Critical:** This does **not** weaken the Class 1 classification. Class 1 is earned by the *halt-execution + artifact-revision-required* criteria (§2.7.6), which both hold regardless of whether the vocabulary choice is determinate. A determinate-but-multi-artifact-revision fork is still Class 1, never Class 2 — Class 2 explicitly excludes artifact revision.
- **Discriminator:** classification-neutral framing refinement.

---

## Part 4 — Sibling assessment (record §6) spot-check

The record asserts U-CP-15, U-OD-01, U-OD-04 are unaffected. Light verification:

- **U-CP-15 (`EngineClass`):** record claims signature matches C-CP-07 §7.1 five-element taxonomy verbatim and `Depends on: [U-CP-11]` is informational. The five-element engine-class taxonomy (event-sourced-replay / save-point-checkpoint / pure-pattern-no-engine / reconciler-loop / WAL-segment) is corroborated at `ADR-D4.md` line 44. The "informational dependency" claim is plausible and consistent with the Meta-Architecture standalone-unit designation, though not independently re-verified against C-CP-07 §7.4 in this review. **No reason to doubt; flagged as not-exhaustively-verified.**
- **U-OD-01, U-OD-04:** `Depends on: []`, no topology surface. Plausibly unaffected by a `TopologyPattern` halt. **Accepted.**

The sibling section correctly preserves Phase 7 forward velocity on unrelated units — a halt should be scoped, and this one is. No objection.

---

## Findings considered and rejected (transparency — what was red-teamed)

- **V1 Silent grounding collapse** — checked whether the three enum sets are real or paraphrased from training data. All three resolve to retrievable design-substrate sources at exact line numbers. *No finding.*
- **V4 Fabricated citations** — spot-checked every cited section: C-CP-10 §10.1/§10.2/§10.3, ADR-D4 v1.1 §1.1, `CLAUDE.md` §1.3/§5, CP-AL-1 at four sites, Workflow §2.7.6. All resolve. *No finding.*
- **V8 Framing contamination** — checked whether the record imports persona/stack/deployment assumptions V3 does not commit. It does not; it stays inside the canonical authority chain. *No finding.*
- **Severity inflation (FM-A)** — checked whether Class 1 over-calls a cosmetic issue. It does not: the defect is a self-contradiction inside the canonical plan. *No finding.*
- **Severity deflation (FM-B)** — checked whether this should actually be Class 2. It should not: artifact revision is required, which is the Class 1 discriminator. *No finding.*
- **Author-mode drift (FM-C)** — checked whether the record supplies replacement enum text. It does not; §4 describes the resolution *shape* (adopt Set 2, revise plan + governance docs) and explicitly says "this record does not apply any fix." *No finding* — the record is itself disciplined here.
- **Tiebreaker soundness** — checked whether a later ADR-D4 could invert the resolution. No ADR-D4 v1.2+ exists; ADR-D4 v1.1 §1.1 matches Set 2. Tiebreaker holds. *No finding.*
- **Halt-timing** — checked whether the halt genuinely precedes code (record §1 "surfaced before code execution"). `harness-cp/src/` is empty of `TopologyPattern`. *Confirmed; no finding.*
- **Acceptance-criterion cross-reference accuracy** — surfaced **N-1** (plan §10.2-vs-§10.3 mis-citation) and **N-2** (`CascadePolicy` divergence not scoped). Both classification-neutral.
- **Determinacy framing** — surfaced **N-3** (the resolution direction is determinate via authority chain; the record over-states it as an open design decision). Classification-neutral.
- **Sibling-scope correctness** — checked whether the halt is correctly scoped to U-CP-22; U-CP-15/U-OD-01/U-OD-04 plausibly independent. *No finding* (U-CP-15 informational-dependency claim flagged as not-exhaustively-verified, not as a defect).

---

## Disposition

**The Class 1 (halt-execution) classification holds up.** It is the correct call: the defect is a self-contradiction inside the canonical CP plan (U-CP-22 acceptance #1 cannot be satisfied as written), and resolution requires revising a Phase 6 plan plus CP-AL-1 verbatim text in three governance docs — which is the `Project_Workflow_v1_8.md` §2.7.6 Class 1 discriminator (halt-execution + design-phase artifact revision). It is neither inflated nor deflated.

The record's recommended resolution direction (adopt Set 2, the spec/ADR-canonical vocabulary) is also sound and survives its own tiebreaker check.

Three refinements are recommended but **none changes the classification**:
- **N-1 / N-2** — accuracy/completeness gaps inside the record (the plan's §10.2-vs-§10.3 section mis-citation is a *third* layer of divergence the record under-states; `CascadePolicy` divergence is unscoped). Recommend inline fix to the record before it drives the operator decision.
- **N-3** — recommend reframing §3/§4: the *choice* of canonical vocabulary is determinate via the authority chain; what requires operator authorization is the multi-artifact revision scope. This is a precision improvement, not a correction of the verdict.

Recommended operator action: proceed with the record's Class 1 halt and its Set-2 resolution direction; incorporate N-1/N-2/N-3 so the operator authorizes a complete and accurately-scoped revision.

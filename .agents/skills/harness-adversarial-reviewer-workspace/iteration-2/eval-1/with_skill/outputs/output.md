# Adversarial Review — U-CP-22 plan unit vs. C-CP-10 spec contract

## Summary

- Mode: Phase-7 pre-implementation review (spec↔plan cross-check for a single unit about to land)
- Artifact reviewed: `design-substrate/Implementation_Plan_Control_Plane_v2_1.md` §2 — unit `U-CP-22` (lines 1172–1212)
- Cited contract: `design-substrate/Spec_Control_Plane_v1_2.md` §10 — `C-CP-10` §10.1 / §10.2 / §10.3 (lines 822–883)
- Date: 2026-05-15
- Finding count by class (§4.1 review-severity scale): Class 3: 3 · Class 2: 0 · Class 1: 1
- Highest-severity finding: F3-01 — `TopologyPattern` enum is a zero-overlap divergence from the cited contract
- Disposition recommendation: Fork — do **not** land U-CP-22. The plan unit is **not** faithful to the spec contract it cites. Three Class-3 (§4.1) findings; resolution requires upstream-artifact revision (Phase-5 spec or Phase-6 plan). Surface to operator as a §2.7.6 **Class 1 (halt-execution)** Phase-7 fork.

**Note on the two Class taxonomies (skill title-section disambiguation).** This report's finding classes are on the **§4.1 review-severity** scale (Class 3 = severe, phase-reopening). The disposition triggers a **§2.7.6 Phase-7 execution fork** on a *separate* scale — there it is **Class 1 (halt-execution)**. The §4.1-Class-3 findings do **not** map to a §2.7.6-Class-3 (informational) fork; they map to a §2.7.6-Class-1 (halt) fork. The two scales are not conflated.

---

## Class 3 findings (severe — requires upstream-phase artifact revision)

### F3-01 — `TopologyPattern` enum: zero-overlap value divergence from cited contract

- **Location:** Plan `Implementation_Plan_Control_Plane_v2_1.md` U-CP-22 Signatures block, lines 1185–1192 (`enum TopologyPattern { ... }`) and acceptance criterion 1, line 1205 ("`TopologyPattern` declares exactly six values per C-CP-10 §10.1 **verbatim**"). Cited contract: `Spec_Control_Plane_v1_2.md` §10.1 taxonomy table, lines 838–845.
- **Defect:** The plan unit declares a `TopologyPattern` enum with six members — `SINGLE_AGENT`, `SEQUENTIAL_HANDOFF`, `PARENT_FANOUT_AGGREGATE`, `RECONCILER_MESH`, `ROUTER_DELEGATE`, `PIPELINE_STAGES`. The cited spec §10.1 names six different patterns — `single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`, `hierarchical-delegation`, `evaluator-optimizer`, `parallelization`. **Not a single value is shared between the two sets** (case/format aside; the *semantic identifiers* differ). The cardinality matches (six) but the membership does not. Acceptance criterion 1 asserts the enum is "per C-CP-10 §10.1 verbatim" — that assertion is false against the cited spec text. A test named `test_topology_pattern_cardinality_six` (line 1210) checks count only and would pass while the unit is wholly unfaithful to the contract; `test_admissibility_per_workload_class_match_spec` would fail or be vacuous, since it cannot match a spec matrix that does not exist for these names.
- **Discriminator that classifies as Class 3:** (b) — requires upstream-phase artifact revision. The plan (Phase-6 artifact) and the spec (Phase-5 artifact) cannot both be canonical; reconciling them requires revising one artifact filed in a phase prior to Phase-7 execution.
- **Evidence:** Spec §10.1 table rows (lines 840–845): `single-threaded-linear` / `orchestrator-workers` / `decentralized-handoff` / `hierarchical-delegation` / `evaluator-optimizer` / `parallelization`. Plan enum (lines 1186–1191): `SINGLE_AGENT` / `SEQUENTIAL_HANDOFF` / `PARENT_FANOUT_AGGREGATE` / `RECONCILER_MESH` / `ROUTER_DELEGATE` / `PIPELINE_STAGES`. The spec §10.2 `TopologyDeclaration.pattern` string-literal union (lines 853–855) restates the §10.1 names verbatim, corroborating §10.1 as the spec's own internally-consistent set. The plan's `RECONCILER_MESH` / `PIPELINE_STAGES` names appear to be drawn from the *engine-class* vocabulary of C-CP-11 §11.2 (`reconciler-loop`) rather than from the topology taxonomy — i.e., the plan unit appears to have mixed a different axis's vocabulary into the topology enum.
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing / substitution) — the plan substitutes a different taxonomy under the same contract ID.
- **Axis-domain attack engaged:** CP — enum divergence from spec (the canonical "Tension 002 calibration shape": "Does this plan unit's `TopologyPattern` enum match the spec C-CP-10 §10.1 enum verbatim, or has it diverged?"). It has diverged completely.
- **Decision-claim label:** *decided* — the divergence is literal and verifiable from both files; no second reading exists. (Which artifact is canonical is an operator decision and is deliberately not chosen here — see Disposition.)
- **Resolution path:** §4.1.3 phase re-opening: revise either `Spec_Control_Plane_v1_2.md` §10.1 or `Implementation_Plan_Control_Plane_v2_1.md` U-CP-22 so the enum membership aligns byte-exact. The reviewer does **not** select which set is canonical and does **not** supply replacement values. As a Phase-7 fork this is **§2.7.6 Class 1 (halt-execution)**: U-CP-22 must not land until the contradiction is resolved. Note for operator: U-CP-22 is a foundational L0 substrate-supplying unit (plan line 3249) consumed by at least U-CP-23/24/25/40/43/50/52 — landing it unfaithfully propagates the divergence to every dependent unit (skill FM: silent absorption contaminates downstream).

### F3-02 — §10.3 admissibility matrix in acceptance criterion 3 is fabricated against the divergent enum

- **Location:** Plan U-CP-22 acceptance criterion 3, line 1207. Cited contract: `Spec_Control_Plane_v1_2.md` §10.3, lines 865–881.
- **Defect:** Plan AC 3 specifies an admissibility matrix: "SEQUENTIAL_HANDOFF and PARENT_FANOUT_AGGREGATE admissible for all four workload classes; RECONCILER_MESH admissible for content-creation + pipeline-automation; ROUTER_DELEGATE admissible for software-engineering + research; PIPELINE_STAGES admissible only for pipeline-automation." None of these five named patterns exist in spec §10.3. Spec §10.3 supplies admissibility annotations for exactly three patterns — `hierarchical-delegation`, `decentralized-handoff`, `parallelization` — and does **not** present them as a four-workload-class boolean matrix. It gives per-pattern prose annotations (e.g., `hierarchical-delegation`: "admissible at software-engineering and research workloads when scope-bounded recursion is justified"). The plan's admissibility predicate is therefore not a translation of the cited contract; it is an independent matrix authored against the plan's own (divergent, per F3-01) enum. The test `test_admissibility_per_workload_class_match_spec` (line 1210) claims to verify "match spec" but cannot — there is no spec matrix of this shape to match.
- **Discriminator that classifies as Class 3:** (b) — requires upstream-phase artifact revision; same reconciliation as F3-01.
- **Evidence:** Spec §10.3 (lines 869–879) annotates only `hierarchical-delegation`, `decentralized-handoff`, `parallelization`, in prose, with fan-out caps and cascade-policy notes — not a workload-class admissibility matrix. Plan AC 3 (line 1207) asserts a 6×4 admissibility relation over enum members the spec §10.3 never names.
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing / authored-not-translated content) — the plan authors a contract surface the cited section does not contain.
- **Axis-domain attack engaged:** CP — admissibility-matrix mismatch.
- **Decision-claim label:** *decided* — the mismatch is literal: the named patterns are absent from §10.3.
- **Resolution path:** §4.1.3 phase re-opening, bundled with F3-01: align the admissibility surface (which enum members, which workload classes, matrix-vs-prose shape) between spec §10.3 and plan U-CP-22 AC 3. Reviewer does not author the corrected matrix. §2.7.6 **Class 1 (halt-execution)**.

### F3-03 — `CascadePolicy` enum and its §10.3 citation both diverge from the spec

- **Location:** Plan U-CP-22 Signatures block lines 1194–1198 (`enum CascadePolicy { COMPLETE_ALL, CANCEL_ON_FIRST_FAIL, PAUSE_ON_FIRST_FAIL }`) and acceptance criterion 2, line 1206 ("`CascadePolicy` declares exactly three values per C-CP-10 §10.3 verbatim"). Cited contract: `Spec_Control_Plane_v1_2.md` §10.2, line 857; §10.3, lines 865–881.
- **Defect:** Two layered defects. (1) **Citation drift:** the plan cites C-CP-10 **§10.3** as the `CascadePolicy` source. Section §10.3 ("Cross-pattern admissibility per workload class") contains no `CascadePolicy` declaration. The three cascade-policy *values* in the spec appear in **§10.2**, inside the `TopologyDeclaration` schema: `cascade_policy : "pause" | "proceed" | "cascade-cancel"` (line 857). The cited section number is wrong. (2) **Value divergence:** even reading against §10.2, the spec's three values are `pause` / `proceed` / `cascade-cancel`; the plan declares `COMPLETE_ALL` / `CANCEL_ON_FIRST_FAIL` / `PAUSE_ON_FIRST_FAIL`. The cardinality matches (three) but no value corresponds verbatim. AC 2's "per C-CP-10 §10.3 verbatim" is false on both the section pointer and the values.
- **Discriminator that classifies as Class 3:** (b) — requires upstream-phase artifact revision. The value-set divergence (defect 2) cannot be resolved by an inline citation fix; it requires revising the spec or the plan, both upstream of Phase-7. (The citation-pointer error alone (defect 1) would be Class 1 drift; it is absorbed into this Class-3 finding because it co-locates with a substantive value mismatch and resolving the latter forces upstream revision.)
- **Evidence:** Spec §10.2 line 857: `cascade_policy : "pause" | "proceed" | "cascade-cancel"`. Spec §10.3 (lines 865–883) contains admissibility annotations only — no enum named `CascadePolicy`, no three-value list. Plan lines 1195–1197: `COMPLETE_ALL` / `CANCEL_ON_FIRST_FAIL` / `PAUSE_ON_FIRST_FAIL`. Plan line 1206 cites "§10.3".
- **Anti-fabrication attack engaged:** A4 (citation does not resolve to the cited section's content); A2 (value substitution under a contract ID).
- **Axis-domain attack engaged:** CP — enum divergence from spec.
- **Decision-claim label:** *decided* — both the wrong section pointer and the value mismatch are literal.
- **Resolution path:** §4.1.3 phase re-opening, bundled with F3-01/F3-02: correct the cited section pointer (§10.3 → §10.2, or wherever the spec is revised to host the enum) and align the three values. Reviewer does not supply the corrected names. §2.7.6 **Class 1 (halt-execution)**.

---

## Class 2 findings (moderate — current-phase revision)

None. Every substantive divergence found requires upstream-artifact revision and therefore classifies Class 3 under discriminator (b).

---

## Class 1 findings (minor — documentation drift)

### F1-01 — `Implements` header omits the `is_admissible` predicate's authoring section split

- **Location:** Plan U-CP-22 `Implements:` line 1174 — `[C-CP-10 §10.1, §10.2, §10.3]`.
- **Defect:** The unit's `is_admissible` signature comment (line 1201) attributes the admissibility predicate to "§10.2 admissibility predicate", while AC 3 (line 1207) attributes the admissibility matrix to "§10.2 admissibility matrix", yet the `Implements` header and the spec's own structure place admissibility at §10.3 ("Cross-pattern admissibility per workload class") and §10.2 at the workflow-definition surface. The unit's internal section attributions for the admissibility predicate (§10.2 in the signature/AC text vs. §10.3 in spec structure) are inconsistent with each other and with the spec's section layout. This is a cross-reference inconsistency, not a semantic content defect independent of F3-02/F3-03.
- **Resolution:** Inline fix in the plan unit — make the internal §10.2/§10.3 attributions consistent with the spec section that actually hosts each surface, once F3-02/F3-03 settle the spec structure. Note: this fix is downstream of the Class-3 reconciliation and should be applied as part of it, not before.

---

## Findings considered and rejected (transparency)

1. **A4 — citation resolution (file/section existence).** Both cited artifacts exist on disk (`Spec_Control_Plane_v1_2.md`, `Implementation_Plan_Control_Plane_v2_1.md`). C-CP-10 resolves to a real section §10 at spec line 822; §10.1/§10.2/§10.3 sub-sections all exist. The *file-level* citation is sound — not fabricated. (The §10.3-vs-§10.2 mis-pointer for `CascadePolicy` is captured in F3-03, not here.) No standalone A4 finding.
2. **A8 — framing contamination (project-commitment violation).** Checked: does U-CP-22 commit a stack value, persona, or deployment surface that workspace `CLAUDE.md` leaves uncommitted? It does not — the unit is a pure enum + predicate declaration. Observed adjacent: the root `CLAUDE.md` §5 (CP-AL-1) lists a *third* `TopologyPattern` value set (`ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF / EVALUATOR_OPTIMIZER / PARALLELIZATION / ROUTING / SEQUENTIAL_PIPELINE`). That is a framing-document inconsistency, not a defect *in the U-CP-22 plan unit* (the review surface), and is out of scope here — flagged as an observation for operator awareness, not a finding against U-CP-22.
3. **A1 — silent grounding collapse.** The plan unit grounds its claims in contract IDs (C-CP-10 §10.x). It does not paraphrase from training data. The grounding *mechanism* is sound; the *fidelity* of what it points to is the F3-01..03 defect — a different failure mode. No A1 finding.
4. **A5 / A7 — uncertainty signals / weak-source escalation.** N/A for an implementation-plan atomic unit; confidence-tag discipline is a spec/ADR-authoring concern, not a plan-unit signature surface. Correctly omitted.
5. **CP axis — topological-sort acyclicity.** U-CP-22 declares `Depends on: (none)` and is a foundational L0 unit (plan line 3249). No cycle, no missing predecessor. Clean.
6. **CP axis — hidden coupling.** U-CP-22 `Inputs: None`; downstream units (U-CP-23/24/25/40/43/50/52) declare U-CP-22 explicitly as a predecessor (plan lines 1218, 1313, 1392, 1609, 1810, 1996). Dependency declarations are explicit, not implicit. Clean — though note the F3-01 divergence *propagates* through these declared edges.
7. **Acceptance-criteria precision (observability from outside the unit).** AC 1–4 are observable via named tests (`test_topology_pattern_cardinality_six`, etc.); they are not in implementer-discretion language. The criteria are *precise* — the defect is that AC 1/2/3 are precise statements that are *false against the cited spec* (F3-01..03), not that they are vague. No precision finding.
8. **CP axis — admissibility predicate signature typing.** `is_admissible(pattern: TopologyPattern, workload: WorkloadClass) -> bool` has typed inputs and a typed return. Signature shape is contract-grade. Clean (the matrix *content* it implements is the F3-02 defect).
9. **Spec-coverage trace mechanism.** Plan §coverage table (lines 3447–3449) maps §10.1→U-CP-22, §10.2→U-CP-22, §10.3→U-CP-22. The trace *table* is structurally complete — every C-CP-10 sub-section has a covering unit. The coverage defect is fidelity (the unit covers them *unfaithfully*), captured in F3-01..03; the trace-table structure itself is not a finding.
10. **FM-C self-check (author-mode drift).** No finding above supplies replacement enum values, a corrected admissibility matrix, or a chosen canonical artifact. Resolution paths describe shape ("align byte-exact", "correct the section pointer") only. Confirmed clean.
11. **Class-taxonomy conflation self-check.** §4.1 finding classes and the §2.7.6 fork class are labeled with their scales separately throughout (see Summary note + each F3 resolution path). Confirmed clean.

---

## Disposition

**The plan unit U-CP-22 is NOT faithful to the spec contract C-CP-10 §10.1 it claims to implement.**

Three §4.1 **Class-3** findings (severe — phase-reopening):

- F3-01: `TopologyPattern` enum — six declared values, **zero** shared with the cited spec §10.1 taxonomy.
- F3-02: §10.3 admissibility matrix in AC 3 is authored against the plan's divergent enum; the cited spec §10.3 names none of those patterns and is prose-annotated, not a matrix.
- F3-03: `CascadePolicy` — cited section (§10.3) does not host the enum (§10.2 does), and the three declared values match none of the spec's three.

Per §4.1.3, the presence of any Class-3 finding mandates **fork to phase re-opening** rather than clearance. Resolution requires revising either the Phase-5 spec (`Spec_Control_Plane_v1_2.md` §10) or the Phase-6 plan (`Implementation_Plan_Control_Plane_v2_1.md` U-CP-22) so the topology taxonomy, the admissibility surface, and the cascade-policy enum align byte-exact across the spec↔plan boundary. The reviewer does **not** select which artifact is canonical — that is an operator/`systems-architect` tension-resolution decision.

As a **Phase-7 execution fork (§2.7.6 scale): Class 1 — halt-execution.** U-CP-22 must **not** land. Per the workspace `CLAUDE.md` §4.3 and the skill's stated worst failure mode, silently absorbing this divergence and implementing U-CP-22 against either set would propagate the contradiction to every dependent unit (U-CP-23/24/25/40/43/50/52 and the broader Cluster 4/5 D4 surface). Surface to the operator and file a `Phase_7_Class_N_Tension` record before any CP-axis topology unit is consumed.

**Adjacent observation (not a finding against U-CP-22, for operator awareness):** the root workspace `CLAUDE.md` §5 (CP-AL-1) enumerates a *third*, distinct six-value `TopologyPattern` set. Three artifacts (spec, plan, framing doc) carry three different topology vocabularies. This is a candidate systemic pattern; the operator may wish to scope the reconciliation to all three artifacts at once rather than spec↔plan only.

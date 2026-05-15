# Adversarial Review — Phase-7 pre-implementation, U-CP-22 + U-OD-04

## Summary

- Mode: Phase-7 pre-implementation review (per `harness-adversarial-reviewer` SKILL.md §"Phase-7 pre-implementation review mode")
- Units under review: **U-CP-22** (TopologyPattern enum + admissibility) and **U-OD-04** (OTel GenAI semconv base layer)
- Corpus reviewed:
  - `design-substrate/Implementation_Plan_Control_Plane_v2_1.md` §2 U-CP-22 (preserved verbatim into v2.2 / v2.3)
  - `design-substrate/Spec_Control_Plane_v1_2.md` §10 C-CP-10 (§10.1 / §10.2 / §10.3)
  - `design-substrate/ADR-D4.md` §1.1–§1.2 (topology authority chain)
  - `design-substrate/Implementation_Plan_Operational_Discipline_v2_1.md` §3.2.1 U-OD-04 (preserved verbatim into v2.4)
  - `design-substrate/Spec_Operational_Discipline_v1_2.md` §4 C-OD-04 (§4.1–§4.5; preserved verbatim into v1.3)
  - `Phase_7_Class_1_Tension_003_WorkloadClass_Undeclared.md`
  - `Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md`
- Date: 2026-05-15
- Finding count by §4.1 review-severity class: **Class 3: 1 · Class 2: 1 · Class 1: 2**
- Highest-severity finding: **F3-01** — U-CP-22 `TopologyPattern` enum + `CascadePolicy` enum + admissibility matrix diverge wholesale from spec C-CP-10 and ADR-D4 §1.1. This is a **third, independent Class 1 (§2.7.6) fork** on U-CP-22, NOT captured by Tension 003.
- Disposition recommendation: **Tensions 003 + 004 are NOT the complete blocking set.** A third fork must be filed before U-CP-22 can land — recommended record `Phase_7_Class_1_Tension_005_U-CP-22_Topology_Schema_Divergence.md`. After Tensions 003 + 004 + the new 005 are resolved, no further fork was surfaced for these two units (see Findings considered and rejected).

**Class-taxonomy disambiguation (per SKILL.md title-section).** This report's findings use the **§4.1 review-severity** scale (Class 1 = minor drift, Class 2 = moderate, Class 3 = severe). Where a finding's disposition triggers a **§2.7.6 Phase-7 execution fork**, the §2.7.6 fork class is stated explicitly and labelled as such. F3-01 is a §4.1 **Class 3** review finding whose disposition is a §2.7.6 **Class 1** (halt-execution) fork.

---

## Verification of the two filed tensions

### Tension 003 — `WorkloadClass` undeclared — **HOLDS. Correctly classified. Scoped narrowly but correctly within its stated scope.**

- **Defect verified.** U-CP-22's `is_admissible(pattern: TopologyPattern, workload: WorkloadClass) -> bool` (`Implementation_Plan_Control_Plane_v2_1.md` line 1200) references `WorkloadClass`. A grep confirms no CP-plan unit declares the type; U-CP-23 also consumes it (`PerWorkloadClassTopologyCommitment.workload_class`, line 1228). The type is consumed pervasively with no carrier unit.
- **Classification verified.** §2.7.6 Class 1 (halt-execution) is correct: the resolution requires an operator decision on the declaring unit + a Phase-6 plan revision-pass; it is not a determinate fix. Inventing the type at U-CP-22 would be a silent H_T design extension (`CLAUDE.md` I-2 / X-AL-3).
- **Scope assessment.** Tension 003 is scoped *only* to the missing `WorkloadClass` carrier unit. It is correct within that scope. It explicitly does NOT address the `TopologyPattern` / `CascadePolicy` / admissibility-matrix divergence — see §3 of the record, which discusses only the type-declaration gap, and §7 sibling assessment, which does not mention an enum divergence. **This is the gap F3-01 fills.** Tension 003's own narrowness is not a defect of Tension 003 — but it means Tension 003 alone does not unblock U-CP-22.
- One scoping note (informational, non-blocking): Tension 003 §4 states the `WorkloadClass` value set is "persona-canonical" and "not in doubt." Verified — C-CP-07 §7.3 enumerates `software-engineering | content-creation | pipeline-automation | research` per Persona §3.1, with an `extension-class` flag per Persona §3.2. The record's claim is sound.

### Tension 004 — U-OD-04 plan signature diverges from spec C-OD-04 — **HOLDS. Correctly classified. All four divergence points verified; the record is complete for U-OD-04.**

Each of the divergence rows in Tension 004 §2 was checked against `Spec_Operational_Discipline_v1_2.md` §4 and `Implementation_Plan_Operational_Discipline_v2_1.md` §3.2.1:

| # | Tension 004 claim | Verified against primary source |
|---|---|---|
| D-1 | span name: plan 2-component `{operation.name} {request.model}` vs spec 3-component | **Confirmed.** Spec §4.1 (line 282): `{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}`. Plan signature line 458: 2 components. Plan acceptance #1 claims "verbatim" — false. |
| D-2 | operations enum: plan 6 values vs spec 7 (plan omits `generate_content`) | **Confirmed.** Spec §4.2 (line 289): `{chat, text_completion, embeddings, generate_content, create_agent, invoke_agent, execute_tool}` = 7. Plan `GenAiOperation` lines 460–467 = 6, omitting `generate_content`. Plan acceptance #2 claims "6 ... verbatim" — false. |
| D-3 | attribute tiers: plan 4 (`REQUIRED/CONDITIONAL/RECOMMENDED/OPT_IN`) vs spec 3 | **Confirmed.** Spec §4.3 table (lines 293–297): Required (Stable) / Recommended (Development) / Opt-In content = 3 tiers; no Conditional. Plan `AttributeTier` lines 469–474 = 4. Plan acceptance #3 claims "exactly 4 tiers per §4.3 verbatim" — false. |
| D-3b | tier assignment: plan places `input/output_tokens` in Conditional + introduces `gen_ai.response.id` (Recommended) | **Confirmed.** Spec §4.3 places `gen_ai.usage.input_tokens` / `output_tokens` in **Recommended**; `gen_ai.response.id` is absent from spec §4.3 entirely. Plan acceptance #4 diverges. |
| D-4 | base metric: plan `gen_ai.client.token.usage` vs spec `gen_ai.client.operation.duration` (histogram) | **Confirmed.** Spec §4.5 (line 305): `gen_ai.client.operation.duration` (histogram). Plan `BASE_METRIC_NAME` line 483 + acceptance #6 = `gen_ai.client.token.usage`. Plan claims "§4.5 verbatim" — false. |

- **Classification verified.** §2.7.6 Class 1 (halt-execution) is correct: U-OD-04's acceptance criteria are internally contradictory (each claims "verbatim" against a signature that is not), so the unit cannot be materialized to satisfy its own acceptance. Resolution requires an operator decision + Phase-6 plan revision-pass. Identical in shape to Tension 002.
- **Completeness assessment.** Tension 004's four-point table is the complete divergence set for U-OD-04 §4.1–§4.5. Red-teaming surfaced no fifth divergence in the U-OD-04 corpus (see Findings considered and rejected — the §4.4 hierarchy-correlation surface, the §4.2 `retrieval` operation question, and the U-OD-04→U-OD-05 dependency were all checked clean).
- One observation in support of Tension 004's recommended direction (does not change classification): Tension 004 §4 step 3 asks the operator to tiebreaker-check that OTel GenAI semconv 1.41.0 itself matches the spec §4.x reading. That tiebreaker is correctly placed as operator-resolution territory; the reviewer does not pre-empt it. The spec internally cross-references its own §4.2 operations enum at C-OD-05 line 633 ("7 (enum per C-OD-04 §4.2)") — i.e., the spec is **internally consistent at cardinality 7**, which strengthens the authority-chain reading that the *plan* (cardinality 6) is the divergent artifact.

---

## Class 3 findings (severe — phase re-opening)

### F3-01 — U-CP-22 `TopologyPattern` enum, `CascadePolicy` enum, and admissibility matrix diverge wholesale from spec C-CP-10 and ADR-D4 §1.1 — a third independent fork on U-CP-22

- **Location:**
  - Plan: `design-substrate/Implementation_Plan_Control_Plane_v2_1.md` §2 U-CP-22, lines 1184–1210 (signatures block + acceptance #1–#3). Preserved verbatim into `Implementation_Plan_Control_Plane_v2_2.md` (§2.4 "U-CP-22 → U-CP-27 preserved verbatim from v2.1") and `Implementation_Plan_Control_Plane_v2_3.md` (line 364 "U-CP-22 through U-CP-55 preserved verbatim from v2.2") — i.e., the divergence is canonical-current at the latest plan version.
  - Spec: `design-substrate/Spec_Control_Plane_v1_2.md` §10 C-CP-10 §10.1 (lines 834–845), §10.2 (lines 847–863), §10.3 (lines 865–882).
  - ADR: `design-substrate/ADR-D4.md` §1.1 (lines 67–101, six-pattern taxonomy table) + §58 ("single-threaded linear / orchestrator-workers / decentralized-handoff / hierarchical-delegation / evaluator-optimizer / parallelization").

- **Defect:** U-CP-22 `Implements: [C-CP-10 §10.1, §10.2, §10.3]` and its acceptance criteria #1–#3 claim the signatures are "per C-CP-10 §10.x verbatim." The plan signature is not. The divergence is wholesale and semantic, across three distinct surfaces:

  | # | Surface | Plan U-CP-22 signature | Spec C-CP-10 + ADR-D4 §1.1 | Plan acceptance claim |
  |---|---|---|---|---|
  | C-1 | §10.1 topology pattern enum | `TopologyPattern` = `SINGLE_AGENT, SEQUENTIAL_HANDOFF, PARENT_FANOUT_AGGREGATE, RECONCILER_MESH, ROUTER_DELEGATE, PIPELINE_STAGES` | `single-threaded-linear, orchestrator-workers, decentralized-handoff, hierarchical-delegation, evaluator-optimizer, parallelization` (spec §10.1 table; ADR-D4 §1.1; identical in `CLAUDE.md` §1.1 CP row's 6-class enum reference) | acceptance #1: "declares exactly six values per C-CP-10 §10.1 **verbatim**" — **false**. Cardinality is 6 in both, but **not a single value name matches.** |
  | C-2 | §10.2 cascade policy | `CascadePolicy` enum = `COMPLETE_ALL, CANCEL_ON_FIRST_FAIL, PAUSE_ON_FIRST_FAIL` (3 values) | Spec §10.2 declares no enum named `CascadePolicy`; cascade policy appears only as the `TopologyDeclaration.cascade_policy` field with string-literal domain `"pause" \| "proceed" \| "cascade-cancel"` (spec §10.2 line 857, cross-ref C-CP-17 §17.1.1) | acceptance #2: "declares exactly three values per C-CP-10 §10.3 **verbatim**" — **false** twice over: (a) §10.3 enumerates no cascade-policy values at all (cascade-policy is a §10.2 surface, not §10.3); (b) the three plan value names do not match the spec's three string literals. |
  | C-3 | §10.2/§10.3 admissibility predicate | `is_admissible(pattern: TopologyPattern, workload: WorkloadClass) -> bool` with acceptance #3's admissibility matrix keyed on the plan's invented pattern names | Spec §10.2/§10.3 declare no function named `is_admissible`. Spec §10.3 ("Cross-pattern admissibility per workload class") expresses admissibility as prose annotations keyed on the spec's pattern names (`hierarchical-delegation` admissible at software-engineering + research; `decentralized-handoff` at pipeline-automation; `parallelization` at research + content-creation). The plan's acceptance #3 matrix (`RECONCILER_MESH` for content-creation + pipeline-automation; `ROUTER_DELEGATE` for software-engineering + research; `PIPELINE_STAGES` pipeline-only) cannot be reconciled with the spec §10.3 prose because the pattern vocabularies are disjoint. | acceptance #3 claims the matrix is "per §10.2 admissibility matrix" — but §10.2 contains no admissibility matrix, and §10.3's admissibility annotations use a disjoint pattern vocabulary. |

  This is structurally **identical to Tension 002 (the prior U-CP-22-vs-C-CP-10 §10.1 enum divergence) and to Tension 004** (plan claims "verbatim" against a signature that is not). The SKILL.md §"Evals" section itself names "the U-CP-22 TopologyPattern enum divergence" as a calibration fixture — confirming this divergence is a known, expected-findable defect, and confirming it is a distinct concern from the `WorkloadClass` gap.

- **Why this is NOT covered by Tension 003.** Tension 003's §2 defect statement is solely "no atomic unit declares `WorkloadClass`"; its proposed resolution (§5) is solely to assign a carrier unit for `WorkloadClass`. Resolving Tension 003 lands the `WorkloadClass` type — it does **not** rename `TopologyPattern`'s six values, does not reconcile `CascadePolicy` against the spec's `cascade_policy` string-literal domain, and does not align the admissibility matrix. After Tension 003 is fully resolved, U-CP-22 would still fail its own acceptance #1–#3 against C-CP-10. F3-01 is therefore an **independent blocking fork.**

- **Internal-consistency note (so the fork is correctly scoped).** The plan's *invented* vocabulary is internally self-consistent: U-CP-22 acceptance #3's admissibility matrix composes cleanly with U-CP-23 acceptance #2's per-workload defaults (`software-engineering → SEQUENTIAL_HANDOFF`, `content-creation → PARENT_FANOUT_AGGREGATE`, `pipeline-automation → PIPELINE_STAGES`, `research → ROUTER_DELEGATE` — each default is admissible for its workload class under acceptance #3). The defect is **not** an intra-plan inconsistency; it is a plan-vs-spec/ADR divergence. This matters for the resolution: conforming U-CP-22 to the spec vocabulary will require a corresponding revision of U-CP-23 (and any other unit consuming `TopologyPattern` values) so the cross-unit composition survives the rename.

- **Discriminator that classifies as Class 3 (§4.1):** discriminator **(b)** — requires upstream-phase artifact revision. The U-CP-22 unit is a Phase-6 plan artifact; resolving the divergence requires a Phase-6 implementation-plan revision-pass (rename the enum values; reconcile/relocate `CascadePolicy`; re-key the admissibility matrix; re-cite §10.2 vs §10.3 correctly; propagate to U-CP-23). Same authority-chain shape as Tension 002 and Tension 004. The spec C-CP-10 + ADR-D4 §1.1 are the canonical authority per `CLAUDE.md` §1.3; the plan is the artifact in error.
- **Evidence:** Plan signature block lines 1185–1201 vs spec §10.1 table lines 838–845 (zero value-name overlap) and ADR-D4 §1.1 line 58. Plan `CascadePolicy` lines 1194–1198 vs spec §10.2 line 857 `cascade_policy : "pause" | "proceed" | "cascade-cancel"`. Plan acceptance #2 line 1206 mis-cites §10.3 for a §10.2 surface.
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing — the plan unit silently substituted a different topology vocabulary for the contract it claims to implement) and the calibration-discipline check behind Tension 002 (does the plan unit faithfully implement the cited contract — SKILL.md §3).
- **Axis-domain attack engaged:** CP — "enum divergence from spec" + "admissibility-matrix mismatch" (SKILL.md §"Axis-domain attack vocabulary", CP row). The domain defect's outcome is concretely present in the artifact's content.
- **Resolution path (shape only — per FM-C, no replacement text supplied):** File a new Phase-7 Class 1 (§2.7.6 halt-execution) tension record — recommended `Phase_7_Class_1_Tension_005_U-CP-22_Topology_Schema_Divergence.md` — covering the §10.1 enum-name divergence, the §10.2 `CascadePolicy`-vs-`cascade_policy` divergence, and the §10.3 admissibility-matrix divergence as one fork cluster. The operator selects the canonical topology vocabulary (authority-chain reading per `CLAUDE.md` §1.3 favours the spec/ADR, as in Tension 002); then an `implementation-planner` revision-pass conforms U-CP-22 signatures + acceptance #1–#3 and propagates the rename to U-CP-23 and any other `TopologyPattern`-consuming unit. The reviewer does not pick the conformance direction. **Decision-vocabulary label: *decided*** — the artifact's text supports a single reading (the plan claims "verbatim" and is demonstrably not verbatim; the divergence is a defect, not a careful-scoping ambiguity).

---

## Class 2 findings (moderate — current-phase revision)

### F2-01 — U-OD-04 `Inputs` field mis-describes the spec §4.3 tier set it cites

- **Location:** `design-substrate/Implementation_Plan_Operational_Discipline_v2_1.md` §3.2.1 U-OD-04, line 449 (`Inputs:` field).
- **Defect:** U-OD-04's `Inputs` field states "§4.3 attribute tiers (Required / Conditional / Recommended / Opt-In)" — naming a four-tier set with a `Conditional` tier. Spec C-OD-04 §4.3 declares three tiers (Required (Stable) / Recommended (Development) / Opt-In content); there is no `Conditional` tier. This is a fourth surface inside U-OD-04 carrying the same divergence as Tension 004 row D-3 — but Tension 004's table cites the *signature* `AttributeTier` enum (line 469) and acceptance #3 (line 490); it does not separately enumerate the `Inputs`-field occurrence at line 449. The `Inputs` field is a distinct location and would survive a fix that only touched the signature block and acceptance criteria.
- **Discriminator that classifies as Class 2 (§4.1):** discriminator **(a)** — affects the substantive content of the current-phase artifact (the `Inputs` declaration is a substantive plan-unit field, not a typo), and resolution is self-contained to the U-OD-04 plan unit *given that Tension 004's resolution has fixed the canonical tier set*. It does not independently trigger (b) or (c) beyond what Tension 004 already carries. **It is not a separate blocking fork** — it is a completeness gap *within* the Tension 004 resolution scope: whoever applies the Tension 004 plan revision-pass must also fix line 449, or U-OD-04's `Inputs` field will still name a non-existent tier.
- **Evidence:** Line 449 `§4.3 attribute tiers (Required / Conditional / Recommended / Opt-In)` vs spec §4.3 table lines 293–297 (three rows, no Conditional).
- **Anti-fabrication attack engaged:** none specifically; surfaced by the §3 calibration-discipline cross-check (plan field vs cited contract).
- **Axis-domain attack engaged:** OD — "span-attribute schema gaps" (the tier taxonomy is the attribute-emission-posture schema).
- **Resolution path (shape only):** Fold the line-449 `Inputs`-field correction into the Tension 004 plan revision-pass scope so the four divergent surfaces (signature `AttributeTier`, acceptance #3, acceptance #4 assignment, and the `Inputs` field) are all conformed in one pass. No separate tension record required. **Decision-vocabulary label: *decided*.**

---

## Class 1 findings (minor — documentation drift)

### F1-01 — U-OD-04 `Inputs` field cites the spec base metric by the divergent value

- **Location:** `design-substrate/Implementation_Plan_Operational_Discipline_v2_1.md` §3.2.1 U-OD-04, line 449 — "§4.5 base metric (`gen_ai.client.token.usage` per spec)".
- **Defect:** The `Inputs` field asserts the spec §4.5 base metric **is** `gen_ai.client.token.usage` "per spec." Spec §4.5 says `gen_ai.client.operation.duration`. This is the same D-4 divergence as Tension 004, here mis-attributed to the spec ("per spec") rather than flagged as a plan deviation. It is drift in a descriptive field rather than a separate substantive defect — Tension 004 row D-4 already owns the substantive divergence; this is the descriptive-field echo.
- **Resolution:** Inline fix in the U-OD-04 `Inputs` field as part of the Tension 004 revision-pass — once the operator selects the canonical base metric, the `Inputs` field's parenthetical "per spec" attribution is corrected to match. No separate record.

### F1-02 — `CLAUDE.md` §2.2 mislabels ADR-D5 as "Topology pattern" / ADR-D6 vs the design-substrate ADR roles

- **Location:** workspace-root `CLAUDE.md` §2.2 table — "ADR-D5 | v1.3 | Topology pattern" and "ADR-D6 | v1.2 | OTel schema (12 namespaces)".
- **Defect:** In `design-substrate/`, **ADR-D4** is the multi-agent topology six-pattern taxonomy (`ADR-D4.md` title line 1) and **ADR-D5** is the HITL primitive (`ADR-D5.md` §1.1 four-response palette, §1.3 three-placement HITL topology primitive). Spec C-CP-10 traces its ADR commitment to ADR-D4 (`Spec_Control_Plane_v1_2.md` line 828: "ADR-D4 v1.1 §Decision ... §1.1 six-pattern topology taxonomy table"). `CLAUDE.md` §2.2 labels ADR-D5 as "Topology pattern" and ADR-D1 as "HITL primitive" — the D-ADR role labels in the `CLAUDE.md` table do not match the design-substrate ADR files. This did not cause a finding against U-CP-22 or U-OD-04 (the units cite spec contracts, not the `CLAUDE.md` table), so it is drift, not a blocking fork.
- **Discriminator:** (a/b/c) all miss — a cross-reference label mismatch in a workspace-pointer table that does not change unit-level semantics. Class 1 drift.
- **Resolution:** Inline correction of the `CLAUDE.md` §2.2 D-ADR role labels to match the design-substrate ADR file roles. Note: per `CLAUDE.md` §9.1 the root `CLAUDE.md` revision policy routes through back-flow — surface to operator; non-blocking for U-CP-22 / U-OD-04.

---

## Findings considered and rejected (transparency)

Substantive attack vectors applied to the U-CP-22 + U-OD-04 corpus that did **not** surface an additional blocking fork:

1. **U-CP-22 admissibility matrix internal consistency (CP axis-domain — admissibility-matrix mismatch).** Checked acceptance #3's admissibility matrix against U-CP-23 acceptance #2's per-workload defaults. Every U-CP-23 default pattern is admissible for its workload class under U-CP-22 acceptance #3. Internally consistent — the divergence is plan-vs-spec only (folded into F3-01), not a cross-unit contradiction. No separate finding.

2. **U-CP-22 cardinality of `TopologyPattern`.** Both plan and spec/ADR commit cardinality **6**. The taxonomy-closed acceptance #4 ("extension requires Workflow §4.1.2 Class-2 D4 revision") matches spec §10.1 line 836 ("closed at D4 §1.1; extension is a Workflow §4.1.2 Class-2 D4 revision"). Cardinality and closure discipline are clean — only the value *names* diverge. Recorded so the operator does not conflate F3-01 with a cardinality defect.

3. **U-OD-04 §4.4 hierarchy-correlation span schema (OD axis-domain — span-attribute schema gap).** Spec §4.4 commits `gen_ai.conversation.id` as the correlation key and the C-OD-11 cardinality-safe restriction (span attribute only, never metric dimension). Plan acceptance #5 covers `trace_id` / `span_id` / `parent_span_id` propagation per OTel. The plan does not contradict §4.4 — it under-specifies the `gen_ai.conversation.id` correlation key, but acceptance #5 is a generic OTel trace-context check that does not *claim* §4.4-verbatim in a way that contradicts the spec. Not a fifth Tension-004 divergence point; Tension 004's four-point table is complete.

4. **U-OD-04 operations enum — `retrieval` question.** `Spec_Operational_Discipline_v1_2.md` C-OD-05 (lines 564–572) references a `retrieval` operation "where `gen_ai.operation.name=retrieval`." Checked whether this implies C-OD-04 §4.2's operations enum is itself incomplete (a spec-internal defect). It does not: §4.2 is the OTel GenAI semconv 1.41.0 base set (7 values); the C-OD-05 specialization layer adds namespace rows on top of the base — `retrieval` appears in the specialization context, not as a claimed base-enum member. The spec is internally consistent; no spec-contract defect surfaced. Tension 004's recommended tiebreaker (operator confirms semconv 1.41.0 matches §4.x) remains the correct place to resolve any residual external-standard question.

5. **U-OD-04 cross-unit dependency gap.** U-OD-04 `Depends on: []`; downstream U-OD-05 `Depends on: [U-OD-04]` and consumes "base-layer attributes ... over which OD specialization-layer namespaces compose" (acceptance #7). The dependency edge is declared in both directions; no hidden coupling. The U-OD-04 rollback boundary correctly enumerates 8 direct dependents. Dependency graph clean for this unit.

6. **U-CP-22 dependency gap (predecessor-missing check).** U-CP-22 `Depends on: (none)` / `Inputs: None`. Tension 003 already correctly observes that even if a `WorkloadClass` carrier unit existed, U-CP-22's empty dependency set would leave the `is_admissible` signature unsatisfiable — this is captured by Tension 003, not a new finding. No additional predecessor-missing edge surfaced beyond `WorkloadClass`.

7. **CXA cross-axis edge cardinality (CXA axis-domain).** Checked whether U-CP-22 (TopologyPattern) or U-OD-04 (span base layer) sit on a cross-axis edge whose seam wiring would be blocked. Both units are axis-internal foundational enum/schema units consumed within their own axis first; CXA seam instantiation (sub-phase 7c) is downstream of unit landing and not in the pre-implementation review scope for these two 7b units. No CXA edge-cardinality finding.

8. **Anti-fabrication A8 (framing contamination) — both units.** Checked whether U-CP-22 or U-OD-04 embeds a persona/stack/deployment overcommitment contrary to `CLAUDE.md` framing. They do not — both are stack-neutral schema/enum declarations; U-OD-04 explicitly defers OTel SDK binding "to implementation discretion" (spec §4.5 line 307). No discriminator (c) framing-contamination finding.

9. **Anti-fabrication A4 (fabricated citations).** Spot-checked U-CP-22's `Implements: [C-CP-10 §10.1, §10.2, §10.3]` and U-OD-04's `Implements: [C-OD-04 §4.1–§4.5]` — all cited spec sections resolve to real sections in `Spec_Control_Plane_v1_2.md` §10 and `Spec_Operational_Discipline_v1_2.md` §4. Citations resolve; the defect is divergence-from-cited-content (F3-01 / Tension 004), not citation fabrication. One mis-citation noted within F3-01 (acceptance #2 cites §10.3 for a §10.2 surface) — folded into F3-01, not a separate A4 finding.

10. **A5 (missing uncertainty signals).** Implementation-plan units are not confidence-tagged artifacts (tagging discipline applies to ADR/spec deliberation surfaces); absence of `[SPECULATIVE]` tags in U-CP-22 / U-OD-04 is expected for the artifact type. Not a finding.

11. **FM-D self-check (axis-domain mechanical application).** Each CP/OD axis-domain concern was checked for whether its *outcome* appears in the artifact, not asserted generically: the CP enum-divergence outcome IS present (F3-01); the OD span-schema-gap outcome at §4.4 is NOT present (rejected, item 3). Mechanical application avoided.

12. **U-OD-04 acceptance #7 / #8 (specialization-layer composition + semconv validator).** Acceptance #7 (specialization namespaces add, do not replace) and #8 (runtime semconv validator conformance) are observable, well-formed acceptance criteria with no spec contradiction. Clean — recorded so the rejected-findings list is not all-negative-on-U-CP-22.

---

## Disposition

**Tensions 003 + 004 are NOT the complete blocking set for U-CP-22 + U-OD-04.** There is a fork N+1.

- **U-OD-04** is blocked by **Tension 004 only.** Tension 004's four-point divergence table is verified complete; F2-01 and F1-01 are completeness gaps *within* the Tension 004 resolution scope (the `Inputs`-field occurrences of the tier-set and base-metric divergences), to be folded into the Tension 004 plan revision-pass — they are not separate forks. After Tension 004 is resolved with its `Inputs`-field echoes corrected, U-OD-04 has no further blocking fork.

- **U-CP-22** is blocked by **Tension 003 AND a third, independent fork (F3-01).** Tension 003 (missing `WorkloadClass` carrier unit) is correctly classified and holds, but is scoped only to the type-declaration gap. F3-01 — the wholesale divergence of U-CP-22's `TopologyPattern` enum value names, `CascadePolicy` enum, and admissibility matrix from spec C-CP-10 §10.1/§10.2/§10.3 and ADR-D4 §1.1 — is a §4.1 **Class 3** review finding (discriminator (b): Phase-6 plan revision required) whose disposition is a **§2.7.6 Class 1 (halt-execution) fork**, structurally identical to Tension 002. Resolving Tension 003 alone does not unblock U-CP-22; F3-01 would still fail acceptance #1–#3 against the cited contract.

**Recommended operator action before either unit lands:**

1. **File a new fork record** — recommended `Phase_7_Class_1_Tension_005_U-CP-22_Topology_Schema_Divergence.md` — capturing F3-01 (the §10.1 enum-name + §10.2 `CascadePolicy` + §10.3 admissibility-matrix divergence cluster) as a single §2.7.6 Class 1 halt-execution fork. The `systems-architect` §4A tension-resolution mode can produce the authority-chain recommendation, as it did for Tension 002.
2. Resolve Tension 003, Tension 004, and the new Tension 005 — three forks, two of them (004, 005) being plan-vs-spec "verbatim"-claim divergences resolvable via `implementation-planner` revision-pass against the spec-canonical reading; one (003) being a missing-carrier-unit plan gap requiring an operator decision on the declaring unit + residence.
3. Note the cross-unit propagation: the Tension 005 resolution renames `TopologyPattern` values and will require a corresponding revision of U-CP-23 (and any other `TopologyPattern`-consuming unit) to keep the cross-unit composition intact.

**Systemic pattern note.** Tension 002, Tension 004, and F3-01 are the same finding shape — a Phase-6 plan unit asserting "per §X verbatim" against a signature that diverges from the cited Phase-5 spec contract. Three occurrences across the CP and OD plans cross the SKILL.md §6 "≥3 → systemic pattern" threshold. Recommendation: in addition to the per-unit revision-passes, the operator should consider a plan-wide audit pass cross-checking every unit's "verbatim" acceptance-criterion claims against its cited spec sections, rather than discovering each divergence one fork at a time at execution-time. This is a higher-leverage resolution than three independent fork records — it addresses the source defect (un-audited "verbatim" claims in the Phase-6 plans) rather than the symptoms.

---

*Phase-7 pre-implementation review. Read-only with respect to all design-substrate and plan artifacts — no repository file modified. Authored 2026-05-15 per `harness-adversarial-reviewer` SKILL.md Phase-7 pre-implementation review mode.*

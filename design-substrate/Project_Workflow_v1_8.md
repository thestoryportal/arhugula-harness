# Project Workflow v1.8

*Multi-LLM Agent Harness Engineering Project · Canonical Workflow Document*
*Status: v1.8 · Authored: 2026-05-08 · Revised: 2026-05-15 (Phase 6.5 Session 5 (γ) — Workflow v1.7 → v1.8 promotion: absorbed §4.1.4.6 cascade-closure-substrate review discipline per `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md`; codified Phase 6.5 pre-transition arc at new §2.6.5 + Phase 7 execution phase at new §2.7; added §5.5 DP-5 in-project Phase 6.5 fork management; applied global-consistency amendments at §0 + §2.6 + §3.1 + §3.2 + §8.6; filename bump from `Project_Workflow_v1_7.md` to `Project_Workflow_v1_8.md`) · Loaded selectively into design-phase sessions*

*Prior revisions: v1.7 (2026-05-14 — Path δ fidelity-grammar revision — encoded Pattern P2 mandatory carry-forward + Pattern P1 strengthening discipline as new §7.4 per `Path_Delta_Workflow_v1_6_to_v1_7_Revision_Kickoff.md`); v1.6 (2026-05-14 — P6-CK Iter 2 PRE-CLEARANCE REVISION at terminal-iteration ceiling — encoded adversarial-review iteration discipline as new §4.1.4 + one-time P6-CK Path B Iter-3 authorization per `P6-CK_Iteration_2_Ceiling_Disposition.md` §4); v1.5 (2026-05-13 — P5-CK iter-2 final-revision-pass — consolidated Pattern P1-PHASE-5 + Pattern P2-PHASE-5 session-prompt-template discipline clauses at §2.5.2)*

---

## §0. Visual Summary

*Front-matter reference. Designed for inclusion as standing context in every design-phase session prompt.*

### Sequencing diagram

```
                              ┌─────────────────┐
PHASE 1 ──► PHASE 2 ──► 3a ──►│ 3a-CHECKPOINT   │──► 3b ──► 3c ──► 3c-CK ────────────► 3d
[research]  [persona]   [F1-  │ [adversarial    │   [D1-  [cross-    CHECKPOINT       [ADD
[COMPLETE]  surfacing]  F5]   │  review of      │    D6]   axis      adversarial      consol-
                              │  found. ADRs]   │          integ.]   review of ADRs]  idation]
                              └─────────────────┘
                                                                                        │
                                                                                        ▼
                     ┌──────────────────┐                                  ┌─────────────────┐
                     │ 6-CHECKPOINT     │◄── 6 ◄── 5-CK ◄── 5 ◄── 4-CK ◄── 4 ◄──            │    3d-CHECKPOINT │
                     │ [adv. review of  │   [impl. [adv.     [spec][PRD] [adv. review       │
                     │  impl. plan]     │    plan]  review PRD]            of ADD]          │
                     └──────────────────┘                                  └─────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ PHASE 6.5        │     7-session pre-transition arc:
                     │ [pre-transition  │     δ stack / α executability /
                     │  arc; in this    │     ζ F3-02 IS / η+θ meta-arch +
                     │  workspace]      │     Phase 7 internal / γ Workflow v1.8 /
                     └──────────────────┘     ε bootstrap / β Phase 7 entry directive
                              │
                              ▼
                     ┌──────────────────┐     H_T (target harness per v2.3 plans)
                     │ PHASE 7          │     built in H_E (Claude Code CLI) per
                     │ [execution;      │     Phase_7_Meta_Architecture_v1 substitution
                     │  new workspace   │     discipline + anti-leakage rules;
                     │  per DP-4]       │     back-flow routes to design-phase workspace
                     └──────────────────┘
```

### Phase × execution-agent matrix

| Phase | Activity | Execution agent |
|---|---|---|
| 1 | Substrate research | (complete; for traceability only) |
| 2 | Persona surfacing | Systems architect skill |
| 3a | Foundational ADRs (F1–F5) | Slate council (11 voices) |
| 3a-CK | Adversarial review of foundational ADRs | Harness adversarial reviewer skill |
| 3b | Derivative ADRs (D1–D6) | Slate council OR per-axis voice (see §5.1) |
| 3c | Cross-axis integration verification | Slate council |
| 3c-CK | Adversarial review of ADRs (D1-D6) | Harness adversarial reviewer skill |
| 3d | ADD consolidation | Systems architect skill |
| 3d-CK | Adversarial review of ADD | Harness adversarial reviewer skill |
| 4 | PRD authoring | PRD author skill |
| 4-CK | Adversarial review of PRD | Harness adversarial reviewer skill |
| 5 | Specification authoring | spec-writer (existing) + council voices as consultants |
| 5-CK | Adversarial review of specification | Harness adversarial reviewer skill |
| 6 | Atomic implementation plan | Implementation planner skill |
| 6-CK | Adversarial review of implementation plan | Harness adversarial reviewer skill |
| 6.5 | Pre-transition arc bridging Phase 6 close → Phase 7 entry; 7-session sequence per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 | Skill-varying per session: stack-commitment + audit-mode (δ + α); implementation-planner §8 (ζ); council-orchestrator selective + spec-writer (η+θ); spec-writer + implementation-planner §8 (γ); systems-architect + skill-creator (ε); spec-writer (β) |
| 7 | H_T build in H_E (Claude Code CLI) under v2.3 plans + Phase_7_Meta_Architecture_v1 substitution discipline; 4 sub-phases per §2.7.3 | Operator + LLM-assisted execution at Claude Code CLI workspace; per-sub-phase agent assignment per `Phase_7_Meta_Architecture_v1.md` §10 |

### Phase entry-gate dependencies (compact)

```
P2     ⇐ P1 complete + pre-design housekeeping complete
P3a    ⇐ P2 produces persona document
P3a-CK ⇐ P3a ADRs exist + adversarial reviewer skill exists
P3b    ⇐ P3a-CK clearance
P3c    ⇐ All P3b ADRs exist
P3d    ⇐ P3c integration verification passes
P3-CK  ⇐ P3d ADD complete
P4     ⇐ P3-CK clearance + PRD author skill exists
P5     ⇐ P4 PRD complete
P5-CK  ⇐ P5 specification complete
P6     ⇐ P5-CK clearance + implementation planner skill exists
P6-CK  ⇐ P6 implementation plan complete
P6.5   ⇐ P6-CK clearance + Phase_6_5_Pre_Transition_Arc_Manifest filed +
         operator directive authorizing pre-transition arc
P7     ⇐ P6.5 9-criterion arc completion + new Claude Code CLI workspace
         bootstrapped + Phase_7_Session_1_Entry_Directive filed
```

### Fork trigger summary

| Class | Trigger | Effect |
|---|---|---|
| Adv-1 (Minor) | Documentation drift in checkpoint | In-place fix; no upstream impact |
| Adv-2 (Moderate) | ADR revision required in current phase | Phase ADR revised; no upstream re-open |
| Adv-3 (Severe) | Foundational/architectural defect | Phase re-opened + affected upstream phases re-opened |
| Integ-1 | Same-axis ADR contradiction (3c) | Council session, single axis |
| Integ-2 | Cross-axis ADR contradiction (3c) | Council session, all relevant voices |
| Integ-3 | Decision dependency on missing ADR (3c) | Backflow to dependent axis |
| Integ-4 | Cross-axis emergent property (3c) | New ADR + consistency check |
| Pers-1 | Persona narrower than expected (P2) | Persona-conditioned foundational decisions |
| Pers-2 | Persona broader / multiple personas (P2) | Decisions duplicated or generalized |
| Pers-3 | Persona surfaces constraint not in substrate (P2) | Pause P3a; new substrate research |

### Skill build sequence summary

| # | Skill | Built when | Where |
|---|---|---|---|
| 1 | Systems architect skill | Before P2 | Separate workspace |
| 2 | Harness adversarial reviewer skill | After P3a completes | Separate workspace |
| 3 | PRD author skill | After P3 completes (JIT for P4) | Separate workspace |
| 4 | Implementation planner skill | After P5 completes (JIT for P6) | Separate workspace |

### Decision points where workflow may legitimately diverge

| ID | Decision | Default | Where |
|---|---|---|---|
| DP-1 | Council vs single skill for derivative ADRs | Council | Entry to P3b |
| DP-2 | Adversarial review depth per checkpoint | Full at P3-CK / P5-CK / P6-CK; sample at P3a-CK | Each checkpoint |
| DP-3 | Re-validate council after major workflow revisions | Yes if ≥1 voice skill modified | After Adv-3 fork |
| DP-4 | Fork project into separate workspace for implementation execution | Yes | After P6-CK clearance |
| DP-5 | In-project Phase 6.5 fork management | All forks routed to design-phase channels per §2.6.5.3 | Per Phase 6.5 session |

### Project commitment reminder

**Committed:** Multi-LLM by design · production-grade engineering discipline · local development environment as design-time deployment target (deployment-stage characteristic, not local-first principles).

**Not committed (design outputs):** persona · stack · deployment surface · framework adoption · model providers · tool protocols · orchestration substrate · durability substrate.

---

## §1. Purpose and Scope

### 1.1 What this document is

The canonical sequencing plan for moving the harness engineering project from completed substrate research through to atomic implementation plan. Encodes phase ordering, execution-agent assignment per phase, skill build sequencing, fork handling for adversarial findings and integration failures, and revision discipline.

### 1.2 What this document is not

This document is not the V3 system prompt, does not duplicate or override it, and does not restate the project's framing commitments. The V3 system prompt governs every session's framing, citation discipline, confidence tagging, scope discipline, and failure-mode awareness. This workflow document complements that framing with phase-specific operational discipline — *what runs when, what gates what, what triggers a rework*.

This document does not specify ADR content, PRD content, specification content, or implementation plan content. Those are phase outputs, not workflow inputs.

### 1.3 Relationship to KB substrate

The workflow is loaded selectively per session, not bulk-loaded. §0 (visual summary) is the standing-context block intended for inclusion in every design-phase session prompt; §§2–8 are reference sections loaded when specific workflow questions surface during execution.

### 1.4 Relationship to ADRs and revisions

The workflow itself is versioned. Revisions are recorded in `Project_Workflow_Revision_Log.md` per the discipline in §7. The workflow does not record ADRs; ADRs are phase outputs filed in their own KB locations as defined by Phase 3 sub-phase outputs (see §2.3).

---

## §2. Phase Definitions

### 2.1 Phase 1 — Substrate research

| Field | Value |
|---|---|
| **Status** | COMPLETE |
| **Inputs** | Initial project framing |
| **Activity** | Sessions 1–3 landscape mapping; Cluster 1–5 deep-dives; Triaged Source Inventory; Pattern Reference Catalog v1.0; council voice skills C1–C11; council validation test |
| **Outputs** | Substrate deliverables in KB; council ready for design-phase deployment |
| **Execution agent** | (historical; documented for traceability) |
| **Entry criteria** | n/a (project genesis) |
| **Exit criteria** | (a) Pattern Reference Catalog v1.0 filed; (b) Cluster 5 V2 §3 decision DAG produced; (c) council validation test outcome READY |
| **Sessions** | 3 substrate sessions + 5 cluster deep-dives + catalog construction sessions A–G + council validation |

Council validation outcome: **READY** (0 FAIL, 1 PARTIAL on confidence tagging granularity). [HIGH — verified against `council-validation-hitl-irreversible-actions-test.md` §7]. The PARTIAL is addressed via session-prompt directives (atomic confidence tagging on substantive claims), not council revision.

### 2.2 Phase 2 — Persona surfacing

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | V3 system prompt (project commitments); substrate deliverables (Cluster 5 V2 §3 D5/D6 persona-dependent classifications); pre-design housekeeping outputs |
| **Activity** | Surface the persona(s) the harness will serve. Persona surfacing is a deliberate design decision, not a research input. The systems architect skill walks the operator through persona-dependent decision implications surfaced by Cluster 5 V2 §3 (HITL synchrony D5; observability backend D6 partial; interactive UX vs API-first surface) and produces a persona document |
| **Outputs** | `Persona_Document_v1.md` with: persona definition; workload shape implications; deployment-surface implications; persona-dependent decision pre-classifications |
| **Execution agent** | Systems architect skill |
| **Entry criteria** | Phase 1 complete; pre-design housekeeping complete; systems architect skill built and validated |
| **Exit criteria** | Persona document filed; persona-dependent decisions in Cluster 5 V2 §3 are classified as (a) directly answerable from persona; (b) requiring further design-phase resolution; (c) deferrable |
| **Sessions** | 1–2 sessions |

### 2.3 Phase 3 — Architectural design

#### 2.3.1 Phase 3a — Foundational decisions (F1–F5)

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | Persona document; Pattern Reference Catalog v1.0 §11.3.1 (per-foundational-decision source loading recommendations); Cluster 5 V2 §3 foundational classification |
| **Activity** | Council deliberation producing one ADR per F-decision: F1 multi-LLM provider abstraction shape; F2 filesystem-as-shared-substrate adoption depth; F3 durable-execution coordination spine commitment (substrate TBD); F4 sandbox-isolation-strength-by-trust-level policy; F5 OS-keychain-at-dev / vault-at-prod secret abstraction |
| **Outputs** | `ADR-F1.md` through `ADR-F5.md` |
| **Execution agent** | Slate council (11 voices) |
| **Entry criteria** | Persona document filed |
| **Exit criteria** | All five F-ADRs filed; each ADR's References section satisfies §2.3.1.1 References-section discipline (standalone Cluster 5 V2 §3 F-decision dependency declaration AND Pattern Reference Catalog source citations are BOTH required; the catalog's §11.3 mapping is a derivative artifact and does NOT substitute for the standalone §3 declaration) |
| **Sessions** | 5 sessions (one per F-decision) |

[HIGH — F1–F5 enumeration verified against Pattern Reference Catalog v1.0 §11.3.1.]

##### 2.3.1.1 References-section discipline (Phase 3a F-ADRs)

Every Phase 3a F-ADR's References section MUST include all four of the following declaration shapes. The shapes are independent: presence of one does not satisfy another.

| # | Declaration shape | Format | Rationale |
|---|---|---|---|
| 1 | Substrate dependency | `Cluster 5 V2 §3 F<N> (text identifying the F-decision foundational classification — persona-dependent / persona-confirmed / workload-dependent / persona-open / etc.)` | Names the substrate-research-derived foundational classification this ADR closes |
| 2 | Pattern Reference Catalog source citation | `Pattern Reference Catalog v1.0 §<axis>.<n> P-<axis>-<n> (one-line pattern descriptor)` | Names the production-pattern source the ADR's decision composes against |
| 3 | Per-axis recommendation citation | `Pattern Reference Catalog v1.0 §11.3.1 F<N> (candidate set: <enumeration> · per-foundational-decision recommendation)` | Names the per-decision substrate enumeration |
| 4 | Persona document trace | `Persona_Document_v1 §<n>.<m> (text identifying the persona-document section the ADR's decision references)` | Names the persona-document section the ADR's decision is sourced to |

Declaration shape 1 (standalone Cluster 5 V2 §3 substrate declaration) is the discipline added in workflow v1.1 to close the systemic citation-omission found in P3a-CK adversarial review. Pattern Reference Catalog §11.3 is a derivative mapping of the §3 DAG and does NOT substitute for declaration shape 1; both shapes 1 and 3 are required.

Worked example (declaration shape 1 for F1):

```
Cluster 5 V2 §3 F1 (multi-LLM provider abstraction shape — persona-confirmed
foundational decision; abstraction-shape and routing-strategy persona-open
sub-aspects deliberated at F-layer per Persona §10.3).
```

The exit-criteria check at §2.3.2 (P3a-CK adversarial review) verifies presence of all four declaration shapes per F-ADR. Absence of any shape is a Class 2 finding by default per §4.1 discriminator (a).

#### 2.3.2 Phase 3a-checkpoint — Adversarial review of foundational ADRs

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | F1–F5 ADRs |
| **Activity** | Discrete adversarial review of foundational ADRs. Reviewer red-teams council voice outputs, surfaces unexamined assumptions, and produces a findings report classified per the §4.1 severity framework |
| **Outputs** | `Adversarial_Review_3a.md` with finding-class breakdown |
| **Execution agent** | Harness adversarial reviewer skill |
| **Entry criteria** | All F-ADRs filed; harness adversarial reviewer skill exists |
| **Exit criteria** | Findings report filed; all Class-3 findings (severe) resolved per §4.1; Class-2 findings either resolved or formally deferred with rationale |
| **Sessions** | 1 session |

#### 2.3.3 Phase 3b — Derivative decisions (D1–D6)

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | F1–F5 ADRs (post-checkpoint clearance); persona document; Pattern Reference Catalog v1.0 §11.3.2 |
| **Activity** | One ADR per D-decision: D1 durable-execution substrate; D2 sandbox provider; D3 Anthropic-primitive adoption depth; D4 multi-agent topology; D5 HITL synchrony; D6 observability backend. Independent decisions I1–I3 may be addressed here or formally deferred |
| **Outputs** | `ADR-D1.md` through `ADR-D6.md` (and optionally `ADR-I1.md` through `ADR-I3.md`) |
| **Execution agent** | Slate council OR per-axis voice (see §5.1 DP-1) |
| **Entry criteria** | Phase 3a-checkpoint clearance |
| **Exit criteria** | All six D-ADRs filed; each D-ADR's References section satisfies §2.3.3.1 References-section discipline (standalone Cluster 5 V2 §3 D-decision dependency declaration AND parent F-ADR citation AND persona document citation when persona-dependent are ALL required) |
| **Sessions** | 6 sessions (one per D-decision) if council; 3–4 sessions if per-axis voice |

[HIGH — D1–D6 and I1–I3 enumeration verified against Pattern Reference Catalog v1.0 §11.3.2 and `Agent_Harness_Architecture__Deployment_Surfaces__Anthropic_Primitives__and_Foundational_Tradeoffs.md`.]

##### 2.3.3.1 References-section discipline (Phase 3b D-ADRs)

Every Phase 3b D-ADR's References section MUST include all five of the following declaration shapes. Shapes 1, 2, 3 mirror Phase 3a's §2.3.1.1 declaration shapes 1, 2, 3 with D-decision substitution; shapes 4 and 5 are D-ADR-specific.

| # | Declaration shape | Format | Rationale |
|---|---|---|---|
| 1 | Substrate dependency | `Cluster 5 V2 §3 D<N> (text identifying the D-decision foundational classification — persona-dependent / persona-confirmed / workload-dependent / persona-open / etc.)` | Names the substrate-research-derived foundational classification this D-ADR closes |
| 2 | Pattern Reference Catalog source citation | `Pattern Reference Catalog v1.0 §<axis>.<n> P-<axis>-<n> (one-line pattern descriptor)` | Names the production-pattern source the D-ADR's decision composes against |
| 3 | Per-axis recommendation citation | `Pattern Reference Catalog v1.0 §11.3.2 D<N> (candidate set: <enumeration> · per-derivative-decision recommendation)` | Names the per-decision substrate enumeration |
| 4 | Parent F-ADR citation | `ADR-F<N> §<section> (text identifying the F-decision the D-ADR composes against)` | Names the F-ADR(s) this D-ADR specializes or extends; required for every D-ADR |
| 5 | Persona document trace | `Persona_Document_v1 §<n>.<m> (text identifying the persona-document section)` | Required when the D-decision is persona-dependent per Persona §10.2 / §10.3; absent declarations require explicit "persona-independent" rationale in the D-ADR §Rationale |

The exit-criteria check at §2.3.6 (P3-CK adversarial review of ADD) verifies presence of all required declaration shapes per D-ADR. Absence of shape 1, 2, 3, or 4 is a Class 2 finding by default per §4.1 discriminator (a). Absence of shape 5 without persona-independent rationale is a Class 2 finding.

#### 2.3.4 Phase 3c — Cross-axis integration verification

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | All F-ADRs and D-ADRs |
| **Activity** | Council convenes with all 11 voices to verify that ADRs are mutually consistent, that no axis has unresolved dependencies on missing ADRs, and that emergent cross-axis properties (e.g., interaction between F3 durable execution + D5 HITL synchrony at trust boundaries per T-perm-1, T-perm-2, T-perm-3) are explicitly addressed |
| **Outputs** | `Integration_Verification_Report.md` with consistency matrix and any new ADRs surfaced (per §4.2) |
| **Execution agent** | Slate council (full convening) |
| **Entry criteria** | All P3b ADRs exist |
| **Exit criteria** | Consistency matrix shows zero unresolved contradictions; any newly-surfaced ADRs filed; integration verification report acknowledges all three permanent tensions and how the chosen ADRs resolve or accept them |
| **Sessions** | 1–2 sessions |

#### 2.3.5 Phase 3d — Architectural Design Document (ADD) consolidation

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | All F/D/I ADRs; integration verification report |
| **Activity** | Consolidate ADRs into a single coherent Architectural Design Document. Preserve ADR traceability; produce the ADD as the canonical pre-PRD architectural artifact |
| **Outputs** | `Architectural_Design_Document_v1.md` |
| **Execution agent** | Systems architect skill |
| **Entry criteria** | Phase 3c integration verification clearance |
| **Exit criteria** | ADD filed; every ADR is referenced by at least one ADD section; every ADD section traces to at least one ADR |
| **Sessions** | 1–2 sessions |

#### 2.3.6 Phase 3-checkpoint — Adversarial review of ADD

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | ADD |
| **Activity** | Discrete adversarial review of the consolidated ADD. Reviewer tests architectural coherence end-to-end, attacks the design at its weakest junctions, and surfaces gaps not visible at individual ADR level |
| **Outputs** | `Adversarial_Review_3.md` |
| **Execution agent** | Harness adversarial reviewer skill |
| **Entry criteria** | ADD filed |
| **Exit criteria** | Findings report filed; all Class-3 findings resolved; Class-2 findings resolved or formally deferred |
| **Sessions** | 1 session |

### 2.4 Phase 4 — PRD authoring

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | ADD (post-checkpoint clearance); persona document |
| **Activity** | Author the PRD. The PRD documents the harness's observable behavior — what it does as visible to its users — derived from the architectural decisions in the ADD. The project's deliberate inversion (substrate → design → PRD → spec → impl plan) means the PRD does *not* drive design; design drives the PRD |
| **Outputs** | `PRD_v1.md` |
| **Execution agent** | PRD author skill |
| **Entry criteria** | Phase 3-checkpoint clearance; PRD author skill built and validated |
| **Exit criteria** | PRD filed; every PRD requirement traces to at least one ADR; no PRD requirement contradicts the ADD |
| **Sessions** | 2–3 sessions |

### 2.5 Phase 5 — Specification authoring

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | PRD; ADD; ADRs |
| **Activity** | Author the specification. The specification translates PRD requirements and ADD architectural commitments into precise, implementable contracts: interface signatures, data schemas, control-flow contracts, validation gate criteria, observability schemas, durability semantics, security boundaries, HITL protocols. Spec-writer skill (existing) is the primary author; council voices act as consultants for axis-specific contract precision |
| **Outputs** | `Specification_v1.md` (likely multi-document; structure determined by ADD) |
| **Execution agent** | spec-writer (existing skill) + council voices as consultants |
| **Entry criteria** | PRD filed |
| **Exit criteria** | Specification filed; every PRD requirement is satisfied by at least one specification element; every ADR commitment is honored by the specification |
| **Sessions** | 4–6 sessions (depending on harness surface area) |

#### 2.5.1 Phase 5-checkpoint — Adversarial review of specification

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | Specification |
| **Activity** | Discrete adversarial review of the specification. Reviewer tests contract completeness, identifies underspecified interfaces, surfaces ambiguities that would cause implementation drift |
| **Outputs** | `Adversarial_Review_5.md` |
| **Execution agent** | Harness adversarial reviewer skill |
| **Entry criteria** | Specification filed |
| **Exit criteria** | Findings report filed; all Class-3 findings resolved; ambiguities either resolved or explicitly deferred to implementation discretion |
| **Sessions** | 1 session |

#### 2.5.2 Session-prompt-template discipline (Phase 5 spec authoring revision passes)

Every Phase 5 spec-authoring revision-pass session prompt MUST include the following two discipline clauses at its session-prompt §"Per-stage execution" or equivalent execution-discipline section. The clauses operationalize two systemic patterns surfaced at P5-CK iterations:

**Clause (i) — Pattern P1-PHASE-5 mechanical-alignment-discipline.** At each Phase 5 spec authoring session-N entry, the authoring skill MUST verify:

1. Namespace names at session-N spec align with prior-session specs' source declarations. Source-axis spec declarations are canonical; downstream specs ingest verbatim.
2. Event-name verb forms (e.g., `breaker.tripped` not `breaker.trip`; `fallback.triggered` not `fallback.trigger`) are aligned across all five-spec authoring sessions.
3. Attribute-set enumerations align across source-axis declarations and downstream-axis ingest tables; per-namespace attribute counts match canonical schema.

Discipline applies to all Phase 5 spec-authoring sessions including initial-draft authoring (sessions 1–5) and revision-pass execution (P5-CK clearance paths). The check is non-skippable per Pattern P1-PHASE-5 closure: mechanical alignment at source-declaration ↔ downstream-ingest seam is the discipline that prevents the namespace-name drift surfaced as systemic pattern at `Adversarial_Review_5.md` iter-1 §"Cross-artifact pattern surfacing".

**Clause (ii) — Pattern P2-PHASE-5 use-latest-version body-citation-alignment.** At each revision-pass stage-N entry, the authoring skill MUST verify body citations to upstream artifacts revised at earlier stages of the same revision pass:

1. Citations to upstream artifacts revised earlier in the same pass MUST be bumped to the latest revised version.
2. Discipline applies across multi-stage revision passes regardless of substantive content change at the revised artifact — token-level alignment required even when cited content is materially unchanged.
3. Pre-emission grep audit for residual citations at prior versions is part of the stage-close discipline; residual citations log as Pattern P2-PHASE-5 violations.

The check is non-skippable per Pattern P2-PHASE-5 closure: failure to bump body citations across multi-stage revision passes is the discipline gap surfaced as F-iter2-03 at `Adversarial_Review_5_iter2.md` (ten body-citation sites across IS + CP + OD specs requiring `ADR-D3 v1.1` → `v1.2` mechanical bump).

**Audit at P5-CK adversarial review.** The harness adversarial reviewer skill verifies (i) + (ii) compliance at every P5-CK iteration. Absence of mechanical-alignment verification or use-latest-version bumps at revision-pass stages is a Class 2 finding by default per §4.1 discriminator (a). Class 2 escalation to Class 3 fires if cross-spec ingest tables diverge from source-axis declarations beyond mechanical-alignment scope.

### 2.6 Phase 6 — Atomic implementation plan

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | Specification (post-checkpoint clearance); ADD; PRD |
| **Activity** | Author the atomic implementation plan: ordered, dependency-explicit, individually-shippable units of work. Each unit names its inputs, its acceptance criteria, its tests, and its dependency on prior units |
| **Outputs** | `Implementation_Plan_v1.md` |
| **Execution agent** | Implementation planner skill |
| **Entry criteria** | Phase 5-checkpoint clearance; implementation planner skill built and validated |
| **Exit criteria** | Implementation plan filed; topological sort of units is acyclic; every specification element is covered by at least one unit; every unit has explicit acceptance criteria |
| **Sessions** | 2–4 sessions |

> **Close state at v1.8.** Phase 6 CLOSED 2026-05-14 with cascade-substrate-clearance ISSUED per `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §8.3 and Phase 7 entry authorization GRANTED. Canonical Phase 6 deliverables at close: IS plan v2.1 / AS plan v1 / CP plan v2.3 / OD plan v2.3 / CXA v2.1. Phase 6.5 pre-transition arc entered 2026-05-14 per operator directive (full pre-transition rigor); see §2.6.5. IS plan v2.1 and OD plan v2.3 subsequently superseded at Phase 6.5 Session 3 (ζ) by v2.2 / v2.4 absorbing F3-02 acknowledged-deferred finding; the v2.2 + v2.4 revisions are Phase 6 plan-substrate consumed by Phase 6.5 + Phase 7, not Phase 6 deliverable additions.

#### 2.6.1 Phase 6-checkpoint — Adversarial review of implementation plan

| Field | Value |
|---|---|
| **Status** | PENDING |
| **Inputs** | Implementation plan |
| **Activity** | Discrete adversarial review of the plan. Reviewer tests dependency ordering, identifies hidden coupling between units, surfaces missing test coverage |
| **Outputs** | `Adversarial_Review_6.md` |
| **Execution agent** | Harness adversarial reviewer skill |
| **Entry criteria** | Implementation plan filed |
| **Exit criteria** | Findings report filed; all Class-3 findings resolved; plan is implementation-ready |
| **Sessions** | 1 session |

### 2.6.5 Phase 6.5 — Pre-transition arc

| Field | Value |
|---|---|
| **Status** | PENDING at v1.8 filing (in-progress); arc-execution authorized 2026-05-14 |
| **Inputs** | P6-CK cascade-substrate-clearance disposition; v2.1/v2.3/v1 implementation plans at Phase 6 close; CXA v2.1; ADD v1.3; PRD v1.1; all canonical ADRs; `Phase_6_5_Pre_Transition_Arc_Manifest.md`; `Canonical_Substrate_Inventory.md` |
| **Activity** | Bridge Phase 6 close → Phase 7 execution entry. Commit target stack; validate plan executability against committed stack; resolve F3-02 acknowledged-deferred finding (eliminates execution-time IS↔OD back-flow risk); author chicken-and-egg meta-architecture distinguishing target harness (H_T) from execution harness (H_E); promote Workflow v1.7 → v1.8 with §2.6.5 + §2.7 phase specifications; author Claude Code CLI bootstrap substrate; author Phase 7 Session 1 Entry Directive |
| **Outputs** | `Target_Stack_Commitment_v1.md` (δ); `Plan_Executability_Audit_v1.md` (α); `Implementation_Plan_Information_Substrate_v2_2.md` + `Implementation_Plan_Operational_Discipline_v2_4.md` (ζ); `Phase_7_Meta_Architecture_v1.md` (η+θ); `Project_Workflow_v1_8.md` (γ); Claude Code CLI bootstrap substrate at ε; `Phase_7_Session_1_Entry_Directive.md` (β) |
| **Execution agent** | Skill-varying per session (see §2.6.5.2) |
| **Entry criteria** | P6-CK clearance per `Adversarial_Review_6_iter4.md` + `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §8.3 cascade-substrate-clearance ISSUED + operator directive 2026-05-14 authorizing full pre-transition rigor |
| **Exit criteria** | 9 arc completion criteria per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §5 (see §2.6.5.4) ALL met |
| **Sessions** | 7 sessions (one per arc-element) per Manifest §3.2 |

#### 2.6.5.1 Arc framing

Phase 6.5 is a pre-transition arc bridging Phase 6 close to Phase 7 execution entry. Phase 6 produced cleared implementation plans approved-for-execution at v2.3 / v2.1 / v1 revisions. Phase 7 hosts the build of the **target harness (H_T)** — the multi-LLM agent harness specified by ADRs + ADD + specs + plans — inside **Claude Code CLI** as the **execution harness (H_E)**.

The chicken-and-egg paradox is load-bearing. Two agent harnesses coexist during Phase 7 build: H_T (the harness the v2.3 plans specify) and H_E (the Claude Code CLI harness hosting the build). H_T's design is authoritative; H_E patterns MUST NOT leak into H_T implementation. Phase 6.5 closes the gap between "cleared plans" and "confident execution start" by committing target stack (eliminates stack-uncertainty execution-time fork risk), validating plan executability (verifies v2.3 plans materialize cleanly against committed stack), resolving F3-02 (eliminates execution-time IS↔OD back-flow risk), authoring meta-architecture (canonicalizes substitution discipline preventing H_E leakage), promoting Workflow v1.7 → v1.8 (formalizes Phase 6.5 + Phase 7 specifications retroactively), authoring Claude Code CLI bootstrap substrate (substrate the new workspace receives at Phase 7 entry), and authoring Phase 7 Session 1 Entry Directive (closes structural gap between portable kickoff and session-1 directive).

#### 2.6.5.2 Session enumeration

Phase 6.5 executes 7 sessions in this design-phase workspace per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2:

| Session | Designator | Name | Primary deliverable | Execution agent |
|---|---|---|---|---|
| 1 | δ | Target Stack Commitment | `Target_Stack_Commitment_v1.md` | Constraint-enumeration + candidate-matrix authoring with ad-hoc C-voice consultation |
| 2 | α | Pre-flight Executability Audit | `Plan_Executability_Audit_v1.md` | Audit-mode deliberation against v2.3 plans; ad-hoc C-voice consultation at signature-level tradeoffs |
| 3 | ζ | F3-02 IS-axis Revision Pass | `Implementation_Plan_Information_Substrate_v2_2.md` + `Implementation_Plan_Operational_Discipline_v2_4.md` | `implementation-planner` SKILL.md §8 revision-pass sub-mode |
| 4 | η + θ | Meta-architecture + Phase 7 internal workflow | `Phase_7_Meta_Architecture_v1.md` (combined per OD-S4-1.A) | `council-orchestrator` selective-convening (C1 + C7 + C11) + `spec-writer` canonicalization |
| 5 | γ | Workflow v1.7 → v1.8 promotion | `Project_Workflow_v1_8.md` + `Project_Workflow_Revision_log.md` update | `spec-writer` workflow-promotion variant + `implementation-planner` §8 revision-pass discipline |
| 6 | ε | Claude Code CLI bootstrap substrate | Root + per-axis `CLAUDE.md`; custom skills; sub-agent boundaries | `systems-architect` + `skill-creator` |
| 7 | β | Phase 7 Session 1 Entry Directive | `Phase_7_Session_1_Entry_Directive.md` | `spec-writer` directive-authoring variant |

Sessions execute in strict sequence. Each session's kickoff prompt is authored at the prior session's close per §2.6.5.6 each-session close handoff pattern. The Phase 6.5 sequence runs in this design-phase project workspace; the new Claude Code CLI workspace is bootstrapped at Session 6 (ε); workspace transfer occurs at Session 7 (β) close per DP-4 default.

#### 2.6.5.3 In-project fork management

Per operator directive 2026-05-14, all forks discovered during Phase 6.5 sessions are managed in this design-phase project workspace. Workspace transfer to the Claude Code CLI workspace does not occur until Session 7 (β) close.

Class disposition routing per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4:

| Class | Trigger | Routing |
|---|---|---|
| Class 1 (halt-arc) | Architectural defect discovered that invalidates prior Phase 6.5 session outputs OR requires Phase 6 / Phase 5 / Phase 3 revision | Halt session; surface to operator; route to applicable design-phase channel (Phase 6 plan revision-pass; Phase 5 spec revision-pass; Phase 3a/3b ADR revision via council convening; Phase 3d ADD revision; Phase 4 PRD revision) per `harness-adversarial-reviewer` SKILL.md §4.1 disposition framework |
| Class 2 (operator-decision-blocking) | In-session decision-point requiring operator selection between substantive alternatives | Surface to operator with options menu via `ask_user_input_v0`; resume after disposition recorded |
| Class 3 (informational) | Observation requiring documentation but not blocking session progress | Log at session close handoff §7.x; route to applicable future session or carry forward |

Class 1 routing back to design phases preserves the design-phase artifact authority chain. Class 2 in-session disposition preserves session forward velocity. Class 3 carry-forward preserves observation continuity across the arc. Phase 7 execution-time fork routing inherits the design-phase back-flow discipline; see §2.7.6.

#### 2.6.5.4 Arc completion criteria

9-criterion completion gate per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §5. Phase 6.5 exits to Phase 7 entry when ALL criteria are met:

| # | Criterion | Owning session |
|---|---|---|
| 1 | Target stack committed at `Target_Stack_Commitment_v1.md` | δ (Session 1) |
| 2 | Plan executability validated against committed stack at `Plan_Executability_Audit_v1.md` | α (Session 2) |
| 3 | F3-02 acknowledged-deferred finding CLOSED via IS plan v2.2 + OD plan v2.4 revision | ζ (Session 3) |
| 4 | Chicken-and-egg meta-architecture canonicalized at `Phase_7_Meta_Architecture_v1.md` (η components catalog + capability overlap map + substitution mapping table + substitution-risk discipline + self-hosting milestone gradient + Phase 7 sub-phase structure) | η + θ (Session 4) |
| 5 | Workflow v1.7 → v1.8 promotion with §2.6.5 + §2.7 + §4.1.4.6 specifications at `Project_Workflow_v1_8.md` | γ (Session 5) |
| 6 | Claude Code CLI bootstrap substrate authored (root + per-axis `CLAUDE.md`; custom skills; sub-agent boundaries) | ε (Session 6) |
| 7 | Phase 7 Session 1 Entry Directive authored at `Phase_7_Session_1_Entry_Directive.md` | β (Session 7) |
| 8 | All Class 1 / Class 2 forks dispositioned with operator decision recorded | All sessions |
| 9 | `Canonical_Substrate_Inventory.md` updated to reflect Phase 6.5 arc deliverables | All sessions (cumulative) |

#### 2.6.5.5 Each-session opening read pattern

Every Phase 6.5 session opens by loading 7 artifacts per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §6:

1. `Phase_6_5_Pre_Transition_Arc_Manifest.md` — sequence context + fork-handling discipline + arc completion criteria
2. `Canonical_Substrate_Inventory.md` — KB navigation anchor; disambiguates retrieval-time canonical-vs-superseded artifact ambiguity
3. The session's kickoff prompt (`Phase_6_5_Session_N_Kickoff.md`) — session-specific scope + segmented delivery contract + entry-gate verification
4. Predecessor session's close handoff (for N ≥ 2) — inheritance of outputs + open forks
5. `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` — Phase 6 close record + Phase 7 entry authorization
6. `Phase_7_Kickoff_Prompt.md` — portable kickoff (substrate inventory + execution discipline + back-flow routing reference)
7. Session-specific substrate per kickoff §3 substrate retrieval

The 7-artifact load pattern is non-skippable at session open. Any missing artifact triggers session-open halt per kickoff §4 entry-gate verification.

#### 2.6.5.6 Each-session close handoff pattern

Every Phase 6.5 session closes by producing 2 artifacts per Manifest §7:

| Artifact | Content |
|---|---|
| `Phase_6_5_Session_N_Close_Handoff.md` | Session deliverable inventory + open forks + Class 1/2/3 disposition + arc completion criteria status + Session N+1 entry-gate prerequisites |
| `Phase_6_5_Session_N+1_Kickoff.md` | Next session's kickoff prompt per project precedent: each session authors next session's prompt at close |

The next-session-kickoff-at-current-session-close discipline preserves session-entry substrate continuity. Operator pushes both close-handoff and next-kickoff from `/mnt/user-data/outputs/` to `/mnt/project/` between sessions.

#### 2.6.5.7 Anti-leakage discipline preservation

Phase 6.5 + Phase 7 inherit two anti-leakage discipline surfaces from `Phase_7_Meta_Architecture_v1.md`:

| Surface | Source | Discipline |
|---|---|---|
| 18 anti-leakage rules across 5 axes + 3 cross-cutting | `Phase_7_Meta_Architecture_v1.md` §7 | H_E patterns MUST NOT contaminate H_T implementation; per-axis enumerated rules govern build-time substitution scope; canonical examples enumerated (illustrative: Claude Code sub-agent topology ≠ H_T CP-axis topology; do not copy) |
| H_T-CP-1 Class 2 substitution-risk surface visibility | `Phase_7_Meta_Architecture_v1.md` §9 | Multi-LLM commitment per ADR-F1 v1.2 is unmet at Phase 7 sub-phase 7a runtime (single-LLM during bootstrap); risk-management discipline anchored at U-CP-01 retirement criterion + anti-leakage rule CP-AL-4; operator visibility preserved across Workflow §2.6.5.7 + §2.7.7 + Session 7 (β) Phase 7 Session 1 Entry Directive substrate |

Both surfaces propagate to Phase 7 execution discipline at §2.7.4 (substitution discipline reference) and §2.7.7 (Class 2 substitution-risk visibility reference). Preservation at Workflow v1.8 ensures these disciplines remain visible after the Phase 7 workspace transfer at Session 7 (β) close — Workflow v1.8 remains in the design-phase workspace as authoritative reference for Phase 7 execution.

### 2.7 Phase 7 — Execution

| Field | Value |
|---|---|
| **Status** | PENDING (entry authorized at Phase 6.5 Session 7 (β) close per §2.6.5.4 criterion 7; execution begins at new Claude Code CLI workspace) |
| **Inputs** | All canonical Phase 6.5 + Phase 6 deliverables: v2.2 / v1 / v2.3 / v2.4 implementation plans; CXA v2.1; IS/AS/CP/OD specs at canonical revisions; F1–F5 + D1–D6 ADRs; ADD v1.3; PRD v1.1; `Target_Stack_Commitment_v1.md`; `Phase_7_Meta_Architecture_v1.md`; `Project_Workflow_v1_8.md`; Claude Code CLI bootstrap substrate; `Phase_7_Session_1_Entry_Directive.md` |
| **Activity** | Build the target harness (H_T) — the multi-LLM agent harness specified by ADRs + ADD + specs + plans — inside Claude Code CLI as the execution harness (H_E). Execute per `Phase_7_Meta_Architecture_v1.md` §10 sub-phase structure (7a Bootstrap / 7b Per-axis interior execution / 7c Cross-axis integration / 7d Self-hosting milestones) under §5 substitution mapping discipline + §7 anti-leakage rules + §6 self-hosting milestone gradient |
| **Outputs** | Target harness (H_T) implementation per v2.3 plans; per-axis production codebase; self-hosting milestones achieved per §6 gradient; cross-axis integration per CXA v2.1; back-flow artifacts routed to design-phase workspace per §2.7.6 |
| **Execution agent** | Operator + LLM-assisted execution in Claude Code CLI workspace; per-sub-phase agent assignment per `Phase_7_Meta_Architecture_v1.md` §10 |
| **Entry criteria** | All 9 Phase 6.5 arc completion criteria met per §2.6.5.4; new Claude Code CLI workspace bootstrapped per Session 6 (ε) substrate; `Phase_7_Session_1_Entry_Directive.md` filed per Session 7 (β) |
| **Exit criteria** | All 7a + 7b + 7c + 7d exit criteria per `Phase_7_Meta_Architecture_v1.md` §10 met; all H_E substitutions retired per §6 self-hosting milestone gradient (or explicitly carried as bounded-residual with documented rationale) |
| **Sessions** | Operator-burden estimate 39–64 sessions per `Phase_6_5_Session_4_Close_Handoff.md` §2.1 Segment 5 disposition |
| **Workspace** | Separate Claude Code CLI workspace per DP-4 default; this design-phase workspace remains canonical archive + back-flow target |

#### 2.7.1 Phase 7 framing

Phase 7 is the execution phase. Two harnesses coexist during build: the target harness (H_T) being built per v2.3 plans, and the execution harness (H_E) — Claude Code CLI — hosting the build. The chicken-and-egg paradox is resolved by `Phase_7_Meta_Architecture_v1.md` §1: H_T's design is authoritative (canonical at ADRs + ADD + specs + plans + CXA v2.1); H_E provides bounded substitutions for not-yet-built H_T primitives; substitutions retire at named self-hosting milestones; H_E patterns MUST NOT leak into H_T implementation.

#### 2.7.2 Workspace discipline

Phase 7 runs in a separate Claude Code CLI workspace from this design-phase project workspace per DP-4 default (`Fork project into separate workspace for implementation execution · Default: Yes · After P6-CK clearance`; see §5.4). This design-phase workspace remains canonical archive of ADRs / ADD / PRD / specs / plans / CXA / Workflow / Phase 6.5 arc artifacts AND remains the back-flow target for Phase 7 execution-time forks per §2.7.6. Bidirectional discipline: Phase 7 execution does not modify design-phase artifacts in-workspace; design-phase artifacts modified in response to Phase 7 back-flow are re-issued from design-phase workspace and re-loaded at Phase 7 workspace.

#### 2.7.3 Sub-phase structure

Phase 7 internal workflow structures into 4 sub-phases per `Phase_7_Meta_Architecture_v1.md` §10 (canonical reference; this clause cites; does not duplicate):

| Sub-phase | Scope | Reference |
|---|---|---|
| 7a Bootstrap | Foundational Level 0 units across all axes + operational minimum (L1–L2 inclusive) per OD-S4-4.A pragmatic boundary derivation; minimum viable IS + OD + CP primitives operational | `Phase_7_Meta_Architecture_v1.md` §10.1 |
| 7b Per-axis interior execution | Axis-level cluster completion; intra-axis dependency-graph traversal per v2.2 / v1 / v2.3 / v2.4 plan dependency graphs | `Phase_7_Meta_Architecture_v1.md` §10.2 |
| 7c Cross-axis integration | CXA v2.1 composition seam instantiation; per-bucket edge activation per CXA v2.1 §3–§7 | `Phase_7_Meta_Architecture_v1.md` §10.3 |
| 7d Self-hosting milestones | Per `Phase_7_Meta_Architecture_v1.md` §6 substitution-retirement schedule; H_T primitives replace H_E substitutions | `Phase_7_Meta_Architecture_v1.md` §10.4 |

Per-sub-phase entry-gate criteria, exit criteria, back-flow routing, and reduced-HITL viability assessment are canonical at `Phase_7_Meta_Architecture_v1.md` §10. Workflow v1.8 §2.7.3 does not redeclare; consumers consult the meta-architecture artifact.

#### 2.7.4 Substitution discipline

H_T ↔ H_E substitution governance is canonical at `Phase_7_Meta_Architecture_v1.md`:

| Surface | Reference | Content |
|---|---|---|
| Substitution mapping table | `Phase_7_Meta_Architecture_v1.md` §5 | 49 substitution entries (IS=9 / AS=6 / CP=21 / OD=8 / CXA=5) across 6 substitution-mechanism categories (H_E-direct=11 / MCP-server=12 / convention=9 / shell-out=8 / manual=5 / authoring-only=4); per-entry: mechanism + scope + retirement criterion |
| Anti-leakage rules | `Phase_7_Meta_Architecture_v1.md` §7 | 18 rules across 5 axes + 3 cross-cutting; preserved at Workflow §2.6.5.7 + §2.7.7 as governance discipline |

Substitution mechanism category boundaries are non-overlapping. Per-primitive retirement triggers at named self-hosting milestones per §2.7.5. Build-time disposition of any new H_T primitive lacking H_E native support routes through the substitution mapping table; new substitutions added to H_T design at Phase 7 execution-time route to design-phase back-flow per §2.7.6 prior to substitution-table extension.

#### 2.7.5 Self-hosting milestone gradient

The Phase 7 progression metric is the self-hosting milestone gradient at `Phase_7_Meta_Architecture_v1.md` §6: per-primitive 49-row retirement gradient (live-criterion + substitution-retirement-criterion) + cluster aggregation as secondary view + 2 documented cross-axis retirement dependencies. Phase 7 progress is measured by substitution-retirement count and cluster-completion ordering rather than by sub-phase elapsed time. Sub-phase 7d closure requires all H_E substitutions retired per the gradient OR each non-retired substitution explicitly carried as bounded-residual with documented rationale (no silent carry-forward).

#### 2.7.6 Back-flow routing

Phase 7 execution-time forks route to design-phase channels per `Phase_7_Kickoff_Prompt.md` §6 back-flow discipline + `Phase_7_Meta_Architecture_v1.md` §10.5.3 back-flow routing aggregate:

| Fork class | Routing target | Mechanism |
|---|---|---|
| Class 1 (halt-execution) | Applicable design-phase channel (Phase 6 plan revision / Phase 5 spec revision / Phase 3a/3b ADR revision / Phase 3d ADD revision / Phase 4 PRD revision / Workflow revision) | Halt Phase 7 sub-phase execution; re-issue design-phase artifact from design-phase workspace; re-load at Phase 7 workspace |
| Class 2 (in-execution operator decision) | Phase 7 execution-time operator decision recorded at sub-phase artifact | Surface to operator in Phase 7 workspace; record decision at sub-phase log |
| Class 3 (informational) | Phase 7 execution log + `Canonical_Substrate_Inventory.md` update | Log; route to Phase 7 final closure documentation |

The design-phase workspace remains canonical archive AND back-flow target throughout Phase 7. Workspace bidirectional discipline per §2.7.2 binds.

#### 2.7.7 Class 2 substitution-risk visibility

`Phase_7_Meta_Architecture_v1.md` §9 records the H_T-CP-1 Class 2 substitution-risk surface: the multi-LLM-by-design commitment per ADR-F1 v1.2 is unmet at Phase 7 sub-phase 7a runtime (single-LLM during bootstrap; H_T's CP-axis multi-LLM topology lands at U-CP-01 retirement criterion in 7b–7c). Risk-management discipline anchored at:

| Anchor | Mechanism |
|---|---|
| U-CP-01 retirement criterion | Substitution-table entry at `Phase_7_Meta_Architecture_v1.md` §5 specifies retirement at U-CP-01 landing |
| Anti-leakage rule CP-AL-4 | `Phase_7_Meta_Architecture_v1.md` §7 governs against H_E single-LLM topology leakage into H_T multi-LLM design |
| Operator visibility at Session 4 (η+θ) close handoff | `Phase_6_5_Session_4_Close_Handoff.md` §5.2 records Class 2 disposition CLOSED with operator visibility |
| Workflow §2.6.5.7 + §2.7.7 (this clause) | Preservation of substitution-risk surface visibility across workflow revision boundary |
| Phase 7 Session 1 Entry Directive substrate (Session 7 β) | Session 7 (β) deliverable inherits H_T-CP-1 surface for operator visibility at Phase 7 entry |

Non-blocking at Phase 6.5 + Phase 7 entry — no design artifact revision required. CLOSED with operator visibility preserved across the workflow-revision boundary.

---

## §3. Phase Dependencies and Ordering

### 3.1 Strict ordering constraints

```
P1 (complete)
   │
   ▼
P2 ─── [persona document]
   │
   ▼
P3a ── [ADR-F1..F5]
   │
   ▼
P3a-CK ─ [Adv_Review_3a]  ◄──── requires harness adversarial reviewer skill
   │
   ▼
P3b ── [ADR-D1..D6, optionally ADR-I1..I3]
   │
   ▼
P3c ── [Integration_Verification_Report]  ◄── full council convening
   │
   ▼
P3d ── [ADD_v1]
   │
   ▼
P3-CK ─ [Adv_Review_3]
   │
   ▼
P4 ─── [PRD_v1]  ◄──── requires PRD author skill
   │
   ▼
P5 ─── [Specification_v1]
   │
   ▼
P5-CK ─ [Adv_Review_5]
   │
   ▼
P6 ─── [Implementation_Plan_v1]  ◄──── requires implementation planner skill
   │
   ▼
P6-CK ─ [Adv_Review_6_iter4 → cascade-substrate-clearance ISSUED]
   │
   ▼
P6.5 ── [pre-transition arc artifacts: Target_Stack_Commitment / Plan_Executability_Audit /
         IS plan v2.2 + OD plan v2.4 (F3-02) / Phase_7_Meta_Architecture /
         Project_Workflow_v1_8 / Claude Code CLI bootstrap substrate /
         Phase_7_Session_1_Entry_Directive]   ◄── 7 sessions in design-phase workspace
   │
   ▼
P7 ──── [H_T build in H_E execution harness]  ◄── new workspace per DP-4;
                                                  back-flow per §2.7.6 routes to
                                                  design-phase workspace
```

### 3.2 Parallelism opportunities

Within Phase 3a, the five F-ADR sessions may run in any order; F1, F2, F4, F5 do not depend on each other. F3 is best run after F2 because durable execution coordinates *over* the filesystem (see Cluster 5 V2 §3 commentary on F3). [MODERATE — F3-after-F2 is a recommendation derived from substrate; not a hard dependency.]

Within Phase 3b, derivative ADRs partition by parent F-ADR:
- D1 derives from F3
- D2 derives from F4
- D3 derives from F2
- D4 is workload-dependent (no single F-parent)
- D5 derives from F1+F3 (HITL contract spans both)
- D6 derives from F3 + persona

D-ADRs may run in any order within Phase 3b. Cross-axis interactions are caught at Phase 3c, not within 3b.

Skill builds (§6) run in parallel with their preceding phase's tail and the next phase's head, in a separate workspace. Build-path is independent of the execution path until the skill is needed for entry into the next phase.

**Phase 6.5 sequencing.** Phase 6.5 sessions execute **sequentially** per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2. Each session's kickoff prompt is authored at the prior session's close per §2.6.5.6; substrate continuity requires sequential execution. No intra-arc parallelism is available.

**Phase 7 sub-phase intra-axis parallelism.** Phase 7 sub-phases 7b (per-axis interior execution) and 7d (self-hosting milestones) admit intra-axis parallelism per `Phase_7_Meta_Architecture_v1.md` §10.2 + §10.4. Per-axis cluster completion within 7b can proceed independently across the four axes (IS / AS / CP / OD) within the dependency-graph constraints of v2.2 / v1 / v2.3 / v2.4 plan dependency graphs. 7a (Bootstrap) and 7c (Cross-axis integration) are inherently cross-axis and do not admit intra-axis parallelism. Self-hosting milestones at 7d retire H_E substitutions in the order specified by `Phase_7_Meta_Architecture_v1.md` §6 self-hosting milestone gradient with 2 documented cross-axis retirement dependencies; ordering within a single retirement cluster is operator-discretion under the gradient's per-primitive criteria.

---

## §4. Workflow Forks and Revision Triggers

### 4.1 Adversarial review findings — severity classes

#### 4.1.1 Class 1 (Minor)

**Criteria:** Documentation drift; typos; format inconsistencies; missing cross-references; unclear prose. Does not affect ADR semantics or downstream phases.

**Revision artifact:** Inline fix in the affected document.

**Re-running discipline:** No re-running of phase activities required.

**Documentation discipline:** Logged in adversarial review findings report; not logged in workflow revision log.

#### 4.1.2 Class 2 (Moderate)

**Criteria:** ADR or document revision required within the current phase. The ADR's substantive content changes, but downstream phases are not invalidated. Examples: refining a decision criterion that was underspecified; adding an explicit dependency declaration that was implicit; correcting a citation; closing an ambiguity that the council noted but did not resolve.

**Revision artifact:** Revised ADR (or document) with version bump in the artifact, change-note inline.

**Re-running discipline:** Re-run only the affected ADR session, not the full phase.

**Documentation discipline:** Logged in adversarial review findings report and in workflow revision log if it changes phase-level structure.

#### 4.1.3 Class 3 (Severe)

**Criteria:** Foundational defect that invalidates downstream work. Examples: an F-ADR that conflicts with an established project commitment surfaces only at the checkpoint; a D-ADR that depends on an F-ADR commitment that does not actually exist; an integration property that breaks an architectural premise.

**Revision artifact:** Phase re-opened. All ADRs and outputs of affected upstream phases are re-evaluated. Affected downstream phases (if any have begun) are halted.

**Re-running discipline:** Affected upstream phases re-run from the point of defect; phase exit criteria re-evaluated.

**Documentation discipline:** Workflow revision log entry. If revision changes which ADRs exist, ADR index updated. If revision invalidates an adversarial review, that review is also re-run.

#### 4.1.4 Adversarial-review iteration discipline

*Added in workflow v1.6 (2026-05-14) per `P6-CK_Iteration_2_Ceiling_Disposition.md` §4. Encodes adversarial-review iteration ceiling discipline previously implicit in P3a-CK / P3-CK / P5-CK / P6-CK practice; resolves ceiling-citation ambiguity surfaced at `Adversarial_Review_6_iter2.md` §6.3.*

##### 4.1.4.1 Per-checkpoint iteration ceiling

Each adversarial-review checkpoint (P3a-CK, P3c-CK, P3-CK, P4-CK, P5-CK, P6-CK) operates under a **2-iteration ceiling** by default:

| Iteration | Scope |
|---|---|
| Iteration 1 | Entry review against the artifact as filed at the checkpoint's entry-gate |
| Iteration 2 | Re-review against revision-pass absorption of Iteration 1 findings |

A PRE-CLEARANCE REVISION disposition at Iteration 2 triggers out-of-band remediation routing per §4.1.4.3 — **not** an automatic Iteration 3.

**Rationale.** A 2-iteration ceiling balances the cost of repeated adversarial review against the cost of carrying defects forward into downstream phases. Allowing unbounded iterations would convert checkpoint review into iterative authoring, defeating the red-team posture central to the harness adversarial reviewer skill (per `harness-adversarial-reviewer` SKILL.md §10 read-only-with-respect-to-artifacts discipline).

**Scope.** The 2-iteration ceiling applies to the adversarial-review checkpoints listed above. Other workflow forks (Integ-1/2/3/4 cross-axis integration failures at Phase 3c; Pers-1/2/3 persona-surfacing surprises at Phase 2) follow their own resolution paths per §4.2 and §4.3 and are not subject to the iteration ceiling.

##### 4.1.4.2 Iteration N entry conditions

For N ≥ 2, Iteration N entry at a checkpoint requires all of:

1. **Predecessor disposition.** Iteration N-1 disposition is PRE-CLEARANCE REVISION. CLEARED dispositions route forward to the next phase; CONDITIONAL CLEARANCE dispositions route forward with deferred absorption logged at the next-phase entry handoff.
2. **Revision-pass absorption filed.** All findings classified at Iteration N-1 are absorbed at v(N+1) revision-pass artifacts filed before session entry.
3. **Operator OD selections.** Per the iteration N kickoff prompt's OD inventory.

##### 4.1.4.3 Out-of-band remediation paths at ceiling

A PRE-CLEARANCE REVISION disposition at the ceiling iteration (default: Iteration 2) routes to **one** of three remediation paths, selected by the operator at the ceiling-disposition handoff:

**Path A — operator-authorized revision-pass absorption.** Operator-authored or LLM-assisted revision pass absorbs the unresolved findings; absorption fidelity verified by operator review rather than further adversarial-review iteration. Final artifacts filed at v(N+1) version bump per affected artifact.

| Trade-off axis | Posture |
|---|---|
| Adversarial gate preserved | No — operator review replaces independent red-team verification |
| Forward velocity | High — no additional iteration cost |
| Residual-defect risk | Moderate — operator may absorb the literal finding without surfacing adjacent defects |

**Path B — ceiling extension by amendment.** Operator amends §4.1.4 to clarify or extend the ceiling for the specific checkpoint, authorizing Iteration N+1 to run an adversarial review against the v(N+1) absorption. The amendment may be:

- **One-time (per-checkpoint exception).** Authorizes a specific Iteration N+1 at a specific checkpoint; does not change the §4.1.4.1 default for future checkpoints.
- **Systemic (default revision).** Revises §4.1.4.1 to increase the default ceiling across all future checkpoints.

| Trade-off axis | Posture |
|---|---|
| Adversarial gate preserved | Yes — independent red-team verification at Iter N+1 |
| Forward velocity | Lower — adds full adversarial-review iteration |
| Procedural overhead | Moderate — explicit Workflow §4.1.4 revision authoring |

**Path C — forward absorption.** Operator authorizes next-phase entry on the substrate as filed; unresolved findings absorbed downstream during next-phase execution; amendment trace logged at next-phase entry handoff.

| Trade-off axis | Posture |
|---|---|
| Adversarial gate preserved | No — defects persist through next-phase entry-gate verification |
| Forward velocity | Highest — no v(N+1) authoring or additional iteration |
| Residual-defect risk | Highest — defects compound through downstream phases until absorbed |

##### 4.1.4.4 Revision log entry on ceiling-extension amendment

Any §4.1.4 amendment authorizing Path B for a specific checkpoint MUST log a revision-log entry per §4.4 documentation discipline capturing:

| Field | Content |
|---|---|
| Trigger checkpoint + iteration | e.g., "P6-CK Iter 2 PRE-CLEARANCE REVISION at terminal-iteration ceiling" |
| Class 2 / Class 3 findings remaining | Per-finding inventory from the Iter N adversarial-review report |
| Operator authorization rationale | Why Path B was selected over Path A or Path C |
| Iteration ceiling delta | One-time vs systemic; affected checkpoint scope |
| Iter N+1 entry gate dependencies | Predecessor v(N+1) artifacts required at Iter N+1 entry |

##### 4.1.4.5 One-time amendments authorized at this workflow version

The following one-time Path B amendments are authorized at workflow v1.6:

**P6-CK Iter 3 (one-time).** Authorized per `P6-CK_Iteration_2_Ceiling_Disposition.md` §3.1 + §4. Iteration 3 of P6-CK runs an adversarial review against the v2.1 absorption ensemble (IS plan v2.1 + CP plan v2.1 + OD plan v2.1 + CXA doc v2.1; AS plan v1 unchanged). One-time scope: does not affect §4.1.4.1 default 2-iteration ceiling for future P6-CK iterations or for other checkpoints. Iter 3 entry conditional on filing of:

- `Project_Workflow_v1_6.md` (this artifact)
- `Implementation_Plan_Information_Substrate_v2_1.md` absorbing F1-IS-02
- `Implementation_Plan_Control_Plane_v2_1.md` absorbing F2-CP-03
- `Implementation_Plan_Operational_Discipline_v2_1.md` absorbing F1-OD-02
- `Cross_Axis_Composition_Document_v2_1.md` absorbing F1-CXA-03
- `P6-CK_Iteration_3_Kickoff.md` entry-gate prompt

##### 4.1.4.6 Cascade-closure-substrate review discipline

*Added in workflow v1.8 (2026-05-15) per OD-F212-5.B at `F2-12_Closure_Declaration.md` §6 + companion revision-log entry `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md`. Encodes cascade-closure-substrate adversarial-review discipline for plan revisions consuming carry-forward closure cascade substrate.*

###### 4.1.4.6.1 Cascade-closure-substrate definition

A **cascade-closure-substrate** is the substrate-set produced by carry-forward closure cascade execution spanning ADR + ADD + PRD + spec + plan revision passes. The canonical cascade pattern is declared at `F2-12_Closure_Path_Execution_Kickoff.md` §3.2: a 6-step closure chain (Step 1 council deliberation → Step 2 ADR revisions → Step 3 ADD consolidation → Step 4 PRD revision → Step 5 spec revisions → Step 6 plan revisions). Cascade-discovered sub-step decomposition (e.g., Step 2 → Step 2a + Step 2b) extends the canonical chain without altering its semantic content.

**Minimum threshold for §4.1.4.6 applicability:** cascade substrate spans ≥6 artifacts authored under §7 fidelity-grammar discipline. Cascades below the threshold do not warrant a §4.1.4.6 review iteration; carry-forward closure under standard §4.1 + §4.1.2 routing applies.

###### 4.1.4.6.2 Authorization conditions

A §4.1.4.6 review iteration is authorized when all of the following hold:

1. **Cascade-substrate span.** ≥6 artifacts produced under §7 fidelity-grammar discipline.
2. **Pre-cascade carry-forward closure.** The pre-cascade carry-forward item (e.g., F2-12 acknowledged-deferred surface) is explicitly declared CLOSED at the cascade-close declaration artifact (e.g., `F2-12_Closure_Declaration.md`).
3. **Operator OD selection at cascade close.** OD selection of the form OD-{cascade-ID}-5 form (option B authorizing §4.1.4.6 review iteration over option A exemption or option C deferred-to-Phase-7-carry-forward).

When all three conditions hold, the cascade-close declaration's §6 disposition table records the §4.1.4.6 authorization scope.

###### 4.1.4.6.3 Iteration-ceiling extension

The §4.1.4.1 default P6-CK iteration ceiling of 3 (= 2 base iterations + 1 one-time Path B extension per §4.1.4.5) **EXTENDS to 4** for cascade-closure-substrate consumers under §4.1.4.6 authorization. The 4th iteration is the cascade-substrate-verification iteration; it does NOT count against the per-plan-revision base-iteration ceiling for non-cascade-driven revisions.

Future cascade closures may invoke §4.1.4.6.3 **once per cascade**; the extension is per-cascade, not per-checkpoint. A cascade that closes and re-opens later requires a new §4.1.4.6 authorization at the re-opened cascade close.

###### 4.1.4.6.4 Review scope discipline

A §4.1.4.6 review iteration scope is the **cascade-driven plan revision absorbing the cascade substrate**. The review:

| Inclusion | Treatment |
|---|---|
| Plan revision absorbing cascade substrate | **Primary review subject**; full adversarial review per `harness-adversarial-reviewer` SKILL.md §4.1 framework |
| Cascade upstream artifacts (ADR / ADD / PRD / spec revisions in the cascade) | **Referential substrate**; inspectable for fidelity verification of plan absorption; NOT adversarially reviewed at this iteration |
| Non-cascade artifacts (other ADRs / specs / plans not in the cascade) | **Out of scope**; preserved at pre-cascade canonical revisions |

Cascade-discovered sub-step decomposition is inspectable as referential substrate; verifying sub-step semantic preservation of the canonical chain is a §4.1.4.6 review concern.

###### 4.1.4.6.5 Disposition routing

§4.1.4.6 review iteration dispositions follow `harness-adversarial-reviewer` SKILL.md §4.1 framework:

| Disposition | Effect |
|---|---|
| CLEARED | Authorizes Phase 7 entry for the cascade-driven plan revision; cascade-substrate-clearance ISSUED at iteration close handoff |
| CONDITIONAL CLEARANCE | Per-finding routing per existing §4.1.2 discipline (Path A operator-authored revision-pass; Path B further iteration extension by new amendment; Path C forward-absorption with Phase 7 carry-forward trace) |
| PRE-CLEARANCE REVISION | Out-of-band remediation routing per §4.1.4.3 (Path A / Path B / Path C selection at cascade-close handoff) |
| FAIL | Phase re-open per §4.1.3 Class 3 disposition |

**Cross-references at v1.8:**

- `F2-12_Closure_Declaration.md` §6.1 — first-application P6-CK Iter 4 authorization scope (Workflow v1.8 §4.1.4.6 first application)
- `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §8.3 — first-application cascade-substrate-clearance ISSUED disposition record
- `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 — canonical 6-step closure cascade pattern reference

Future cascade closures cite this revision-log entry (`Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md`) plus their own cascade-close declaration's §6 disposition table.

### 4.2 Cross-axis integration failures (Phase 3c)

#### 4.2.1 Same-axis ADR contradiction

**Trigger:** Two ADRs within the same architectural axis (e.g., two state-related ADRs) are mutually inconsistent.

**Resolution:** Council session with the axis-owning voice as primary; consultant voices as needed. Resolution may modify one ADR, modify both, or introduce a third ADR.

#### 4.2.2 Cross-axis ADR contradiction

**Trigger:** ADRs across different axes are mutually inconsistent (typically engaging one of the three permanent tensions: T-perm-1 C4↔C10, T-perm-2 C2↔C3, T-perm-3 C1↔C9).

**Resolution:** Full council session with all relevant voices. Resolution explicitly names which permanent tension is engaged and how the chosen ADR pair resolves or formally accepts the tension.

#### 4.2.3 Decision dependency on missing ADR

**Trigger:** During Phase 3c, an ADR is found to depend on another ADR that was not produced.

**Resolution:** Backflow to the dependent axis. The missing ADR is authored (Phase 3a or Phase 3b session, depending on whether the missing decision is foundational or derivative). Phase 3c is paused until the missing ADR is filed.

#### 4.2.4 Cross-axis emergent property

**Trigger:** Phase 3c surfaces an architectural property that emerges from the interaction of multiple ADRs and is not addressed by any single ADR. Example: replay-determinism semantics across the durable boundary engages C1+C3+C7+C11 simultaneously.

**Resolution:** New ADR authored to cover the emergent property. Consistency check re-run.

### 4.3 Persona-surfacing surprises (Phase 2 propagating to Phase 3)

#### 4.3.1 Persona narrower than expected

**Trigger:** Phase 2 surfaces a persona narrower than the substrate-research scope assumed (e.g., a single specific role, a single specific deployment target).

**Effect:** More decisions become persona-specific. The Cluster 5 V2 §3 D5/D6 persona-dependent classifications may extend to additional decisions; some F-decisions may need persona-conditioning.

**Resolution path:** Workflow revision log entry. Phase 3a session prompts updated to reflect persona-conditioning. No phase re-run unless persona-conditioning changes a foundational ADR's content.

#### 4.3.2 Persona broader than expected (multiple personas)

**Trigger:** Phase 2 surfaces multiple personas the harness must serve, not a single persona.

**Effect:** More decisions become persona-dependent. Some ADRs may need to be made twice (per persona) or generalized with persona-as-parameter.

**Resolution path:** Persona document explicitly enumerates personas. Phase 3a/3b session prompts indicate per-persona-or-generalized resolution per ADR. No phase re-run unless ADR scope expands beyond single-session capacity.

#### 4.3.3 Persona surfaces constraint not in substrate

**Trigger:** Phase 2 surfaces a persona-driven constraint the substrate research did not address (e.g., specific compliance requirement, specific deployment-environment constraint, specific scale property).

**Effect:** Substrate research gap. Phase 3a may be unable to proceed without further substrate.

**Resolution path:** Phase 3a paused. Targeted substrate research session(s) authored to close the gap. Phase 3a resumes after substrate is filed.

### 4.4 Documentation discipline (all forks)

Every fork triggers a workflow revision log entry capturing:

- **Trigger** — what surfaced the fork (checkpoint finding, integration failure, persona surprise)
- **Severity / class** — Class 1/2/3 for adversarial; Integ-1/2/3/4 for integration; Pers-1/2/3 for persona
- **Affected phases** — which phases re-open
- **Affected ADRs** — which ADRs require revision
- **Resolution path** — how the fork was resolved
- **Resolution outcome** — the final state after resolution

§4.1.4 amendments authorizing Path B for a specific checkpoint additionally capture the §4.1.4.4 fields.

---

## §5. Decision Points Where Workflow May Diverge

These are points where the project may legitimately choose between multiple valid paths. Decisions here are *workflow* decisions, not architectural ADRs.

### 5.1 DP-1 — Council vs single skill for derivative decisions (Phase 3b)

| Field | Value |
|---|---|
| **Decision** | Should D1–D6 be authored by full council convening, or by per-axis voice operating alone? |
| **Criteria** | (a) Substrate richness for the decision; (b) cross-axis tension presence; (c) session budget |
| **Options** | Full council convening per D-ADR; per-axis voice with handled-by-reference for adjacent voices; hybrid |
| **Default** | Full council convening |
| **When to revisit** | After P3a-checkpoint findings; if Phase 3a council deliberations consistently resolve into single-voice positions, downgrade default to per-axis with consultants |

### 5.2 DP-2 — Adversarial review depth at each checkpoint

| Field | Value |
|---|---|
| **Decision** | At each checkpoint, what depth of adversarial review applies — full review of every artifact, or sample-based review? |
| **Criteria** | Phase output stakes; ADR count; session budget |
| **Options** | Full (every ADR, every section); sample (representative ADRs, key integration points); targeted (only ADRs flagged by author as uncertain) |
| **Default** | Full at P3-CK, P5-CK, P6-CK; sample at P3a-CK |
| **When to revisit** | If P3a-CK sample review surfaces Class-3 findings, upgrade P3a-CK to full going forward |

### 5.3 DP-3 — Re-validate council after major workflow revisions

| Field | Value |
|---|---|
| **Decision** | If a workflow revision (Class-3 fork) modifies a council voice skill, should the council validation test be re-run? |
| **Criteria** | Voice skill modification scope; whether modification touches framing or just substrate references |
| **Options** | Re-run full validation test; run abbreviated re-validation on modified voice only; skip re-validation |
| **Default** | Re-run validation if any voice skill's framing-relevant content (V3 framing compliance, citation discipline, tension surfacing) is modified; otherwise skip |
| **When to revisit** | After any Class-3 fork that touches voice skill files |

### 5.4 DP-4 — Fork project into separate workspace for implementation execution

| Field | Value |
|---|---|
| **Decision** | After Phase 6-checkpoint clearance, should implementation execution happen in a separate workspace or in the current project? |
| **Criteria** | Cross-project isolation discipline (V3 system prompt §continuity); KB sprawl risk; execution-vs-design context separation |
| **Options** | Separate workspace; same workspace; hybrid (separate workspace for execution, this workspace as read-only reference) |
| **Default** | Separate workspace; this workspace becomes read-only reference |
| **When to revisit** | At P6-CK clearance |

### 5.5 DP-5 — In-project Phase 6.5 fork management

*Added in workflow v1.8 (2026-05-15) per operator directive 2026-05-14 + `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4 in-project fork management; canonical content at §2.6.5.3.*

| Field | Value |
|---|---|
| **Decision** | During Phase 6.5 pre-transition arc execution, are forks discovered at any session managed in this design-phase project workspace or transferred immediately to the Phase 7 Claude Code CLI workspace? |
| **Criteria** | Pre-transition arc artifact coherence (design-phase artifacts at canonical authority); workspace transfer threshold (Phase 7 Session 1 Entry Directive filing); cross-workspace fork-routing complexity |
| **Options** | (A) All Phase 6.5 forks managed in design-phase workspace; new-workspace transfer only at Session 7 (β) close · (B) Forks per-session transferred to Claude Code CLI workspace as Phase 6.5 progresses · (C) Hybrid (Class 1 forks in design-phase; Class 2/3 in either workspace per operator discretion) |
| **Default** | **(A) All Phase 6.5 forks managed in design-phase workspace.** Per operator directive 2026-05-14. Canonical routing per §2.6.5.3 and `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4. The new Claude Code CLI workspace is not bootstrapped until Session 6 (ε); transfer threshold is Session 7 (β) close. Design-phase workspace remains canonical authority for ADR / ADD / PRD / spec / plan / CXA / Workflow artifacts throughout Phase 6.5 + Phase 7. |
| **When to revisit** | Per arc; if future cascade-closure events produce a pre-transition arc analogous to Phase 6.5, evaluate whether DP-5 default applies or whether the analogous arc warrants distinct routing. The Phase 6.5 → Phase 7 cross-workspace back-flow discipline at §2.7.6 inherits DP-5 default during Phase 7 execution. |

---

## §6. Skill Build Sequencing

Skills are built in a separate workspace per the project's cross-project isolation discipline (V3 system prompt §continuity). The build workspace is isolated from this project's KB; only the validated skill artifact is brought into this project.

### 6.1 Skill 1 — Systems architect skill

| Field | Value |
|---|---|
| **Used in** | Phase 2 (persona surfacing); Phase 3d (ADD consolidation) |
| **Built when** | Immediately, before Phase 2 begins |
| **Where** | Separate workspace |
| **Informed by** | V3 system prompt; substrate deliverables (especially Cluster 5 V2 §3 persona-dependent and workload-dependent classifications); Pattern Reference Catalog v1.0 |
| **Build effort** | 1–2 sessions |
| **Validation discipline** | Validation test against representative persona-surfacing scenario and ADD-consolidation scenario before deployment to harness project |

### 6.2 Skill 2 — Harness adversarial reviewer skill

| Field | Value |
|---|---|
| **Used in** | Phases 3a-CK, 3-CK, 5-CK, 6-CK |
| **Built when** | After Phase 3a completes |
| **Rationale** | Building after Phase 3a means the adversarial reviewer's design is informed by what foundational ADRs actually look like in this project, rather than by speculation about their shape |
| **Where** | Separate workspace |
| **Informed by** | F1–F5 ADRs as authored; council voice skill files (target of red-team); §4.1 severity classification framework |
| **Build effort** | 2–3 sessions |
| **Validation discipline** | Validation test against the F1–F5 ADRs (does it find Class-2 and Class-3 findings the council missed?) before deployment |

### 6.3 Skill 3 — PRD author skill

| Field | Value |
|---|---|
| **Used in** | Phase 4 |
| **Built when** | After Phase 3 completes (just-in-time) |
| **Rationale** | JIT build means the PRD author skill is informed by the actual ADD content; the project's deliberate inversion (design → PRD) means the PRD author must work *from* architectural decisions, not toward them |
| **Where** | Separate workspace |
| **Informed by** | ADD; PRD author conventions appropriate to the project's deployment-stage characteristics |
| **Build effort** | 1–2 sessions |
| **Validation discipline** | Validation test on a representative ADD section (does the skill produce PRD requirements that trace back to the ADR and forward to observable behavior?) |

### 6.4 Skill 4 — Implementation planner skill

| Field | Value |
|---|---|
| **Used in** | Phase 6 |
| **Built when** | After Phase 5 completes (just-in-time) |
| **Rationale** | JIT build means the implementation planner is informed by the actual specification's contracts, not by speculation about specification shape |
| **Where** | Separate workspace |
| **Informed by** | Specification; the specification's interface signatures, schemas, and contracts |
| **Build effort** | 1–2 sessions |
| **Validation discipline** | Validation test on a representative specification section (does the skill produce ordered, dependency-explicit, individually-shippable units with concrete acceptance criteria?) |

---

## §7. Workflow Versioning Discipline

### 7.1 Versioning scheme

- **v1.x** — clarifications, minor structural updates (e.g., §0 visual summary refinements; new fork-class addition without changing the three-class structure; new decision-point addition; iteration-ceiling discipline encoding per §4.1.4)
- **v2.x** — major structural changes (adding/removing phases; fundamental fork-handling structure changes; reordering phase dependencies)

### 7.2 Revision recording

Revision log lives in KB as `Project_Workflow_Revision_Log.md`. Every workflow revision creates a log entry with:

- Version bump (v1.0 → v1.1)
- Date
- Change summary
- Rationale
- Affected sections
- Trigger (workflow fork that motivated the revision; or planned refinement)

### 7.3 Revert discipline

If a workflow revision proves wrong (creates more friction than the prior version; misclassifies a fork; misorders a dependency), the prior version is restored. The revision log records the revert with rationale. Reverts are recorded as forward-version-numbered entries (v1.2 reverts to v1.0 content as v1.3, not "go back to v1.0"), so the revision history remains linear.

### 7.4 Fidelity-grammar discipline

*Added in workflow v1.7 (2026-05-14) per Path δ revision authorization (`Path_Delta_Workflow_v1_6_to_v1_7_Revision_Kickoff.md`). Encodes cumulative Pattern P2 systemic-recommendation mandatory carry-forward (7 finding-instances across IS / OD / CXA / CP at P6-CK Iter 1–3) and Pattern P1 strengthening case (9 cross-iteration finding-instances at P6-CK Iter 1–3). Discipline applies to artifacts authored under v1.7 onward; v1.6-and-prior substrate is grandfathered.*

#### 7.4.1 Fidelity-claim taxonomy

Every claim of alignment between authored content and a cited substrate site classifies into exactly one of the following four categories. The enumeration is closed and disjoint: every fidelity claim MUST resolve to one category; categories MUST NOT overlap at a single claim site.

| Category | Semantic precision | Verification basis |
|---|---|---|
| **byte-exact** | Asserts byte-for-byte identity between authored content and a cited substrate sub-section. Vocabulary: `verbatim`, `byte-exact`, `exact copy`, `unchanged`. | Deterministic diff against the cited substrate site MUST return zero changes (per §7.4.2). |
| **structural-fidelity** | Asserts element-by-element semantic alignment without byte-exactness. Vocabulary: `aligned`, `matches`, `mirrors`, `preserves N entries`, `same cardinality`. | Per-element traceability mapping against a named invariant kind (per §7.4.3). |
| **paraphrastic** | Asserts semantic alignment with rephrased form. Vocabulary: `derived from`, `summarized from`, `restated from`. | Author judgment; not automatable. Carries derivation signal only; does NOT guarantee literal content. |
| **citation-only** | No fidelity claim about authored content's relation to substrate beyond derivation or inheritance. Vocabulary: `per §N.M`, `see §N.M`, `as defined in §N.M`. | Citation MUST resolve to a content-bearing anchor (per §7.4.5); no fidelity assertion required. |

**Default category for ambiguous claim sites: citation-only.** A claim authored without explicit byte-exact, structural-fidelity, or paraphrastic vocabulary is interpreted as citation-only and carries no fidelity assertion beyond substrate identification.

#### 7.4.2 Byte-exact verification grammar

A fidelity claim in the byte-exact category MUST satisfy all of:

1. **Diff-zero precondition.** The authored content site, when diffed against the cited substrate sub-section, returns zero textual changes. The author MUST execute the diff before emission. Whitespace-only differences disqualify byte-exact classification (downgrade to structural-fidelity).
2. **Sub-section-anchor resolution.** The citation MUST resolve to the most-specific sub-section anchor that bears the cited content per §7.4.5. Byte-exact claims against parent-section anchors where the content lives in a sub-section are P2 firings.
3. **Single-substrate scope.** A byte-exact claim cites exactly one substrate site. Composite "byte-exact per §A + §B + §C" claims are forbidden; each substrate site's contribution requires its own classified fidelity claim.
4. **Downgrade path.** If diff-zero cannot be verified at emission time, the author MUST reclassify to structural-fidelity (with named invariant per §7.4.3), paraphrastic, or citation-only. Falsifying a byte-exact claim against substrate is a Pattern P2 firing and a Class 2 finding by default per §4.1 discriminator (a).

#### 7.4.3 Structural-fidelity verification grammar

A fidelity claim in the structural-fidelity category MUST name one of the following invariant kinds. The enumeration is closed:

| Invariant kind | Semantic | Verification check |
|---|---|---|
| **cardinality match** | N substrate elements map to N authored elements 1:1 | Element count at substrate equals element count at authored site |
| **name match** | Element identifiers preserved verbatim in distinct authoring context | Per-name lookup against substrate identifier set |
| **ordering match** | Sequence preserved across authoring transformation | Position-by-position mapping |
| **enumeration match** | Closed-set membership preserved (no additions, no omissions) | Set-equality check against substrate enumeration |
| **structural-fidelity composite** | Two or more of the above co-applied at a single claim site | Each invariant kind verified independently; composite claim names all applied kinds |

Claim format: `{invariant-kind} per {substrate-site}` with explicit invariant kind named from the enumeration above. Examples:

- `cardinality match per CP spec §5.3 (5 of 5 entries)` — five substrate entries map to five authored entries.
- `name match per ADR-D1 §1.1.1 (engine.* attribute names)` — the attribute names appear verbatim in distinct authoring context.
- `enumeration match per CP spec §9.2 (Tier-3 / Tier-5 mapping)` — the closed set is preserved without addition or omission.

Verification: row-by-row or element-by-element traceability mapping pass before emission. The mapping does NOT need to appear in the artifact; the artifact records the claim, the audit pass at §7.4.6 verifies it.

Falsifying a structural-fidelity claim is a Class 2 finding by default per §4.1 discriminator (a).

#### 7.4.4 Citation-only grammar

A fidelity claim in the citation-only category MUST satisfy all of:

1. **No fidelity-claim vocabulary.** Citation-only claims MUST NOT use `verbatim`, `byte-exact`, `matches`, `mirrors`, `preserves` or other §7.4.1 byte-exact / structural-fidelity vocabulary. Use of fidelity vocabulary at a citation-only site reclassifies the claim and invokes the corresponding §7.4.2 or §7.4.3 verification grammar.
2. **Sub-section-anchor resolution.** The citation MUST resolve per §7.4.5; citation-only does not relax sub-section-resolution discipline.
3. **Named transformation when derivation is non-trivial.** If the authored content derives from substrate via a transformation (e.g., specialization, extension, ingest with verb-form normalization, composition across multiple substrates), the transformation MUST be named at the claim site. Acceptable transformation vocabulary: `specialized from §N.M`, `extended at §N.M`, `ingested from §N.M with verb-form normalization`, `composed from §A + §B`.

Citation-only is the acceptable shape for derivation, inheritance composition, and dependency declaration where the authored content intentionally diverges from substrate content (refinement, extension, specialization).

#### 7.4.5 Sub-section-resolution discipline (P1 addressing)

*Addresses Pattern P1 (mechanical-alignment: sub-section anchor drift; citation cardinality drift; spec-anchor mis-attribution). Per OD-Pδ-1 (A) revision-scope inclusion.*

Every citation in an authored artifact MUST resolve to the most-specific sub-section anchor that bears the cited content. The discipline applies across all four §7.4.1 fidelity-claim categories.

| Defect shape | Discipline rule |
|---|---|
| Citation to `§N` where canonical content-bearing sub-section is `§N.M` | P1 firing. Citation MUST be deepened to `§N.M`. |
| Citation to `§N.M` where canonical content lives at `§N.M.K` | P1 firing. Citation MUST be deepened to `§N.M.K`. |
| Citation to `§N.M` where substrate sub-section has been renumbered since the cited revision | P1 firing. Citation MUST be updated to the current revision's anchor. |
| Coverage-matrix cardinality claim (e.g., "5 of 5 entries") that does not match the substrate sub-section's actual cardinality | P1 firing. Cardinality MUST be re-counted against substrate; matrix row count adjusted. |
| Multi-substrate citation (`per §A + §B`) where one substrate does not bear the cited content | P1 firing. Citation MUST drop the non-bearing substrate or reclassify the claim. |

Verification: sub-section-anchor resolution check pass before emission. The check resolves every citation in the authored artifact against the cited substrate's current revision; unresolved anchors and cardinality mismatches are logged as P1 violations.

Falsifying sub-section-resolution discipline is a Class 2 finding by default per §4.1 discriminator (a).

#### 7.4.6 Pre-emission audit gate

*Per OD-Pδ-3 (B) — Plan + spec + ADD + PRD substantive-substrate coverage. ADRs, CXA, integration-verification reports, adversarial-review reports, kickoffs, handoffs, revision logs, and the workflow document itself are out-of-scope. The out-of-scope artifact classes remain under their existing filing-time discipline (§§2.3.1.1 / 2.3.3.1 References discipline; §2.5.2 spec-authoring discipline).*

##### 7.4.6.1 Audit scope

The pre-emission fidelity-grammar audit applies to authoring sessions producing artifacts in the following closed enumeration:

| Artifact class | Examples | Authoring skill |
|---|---|---|
| **Implementation plan** | `Implementation_Plan_<axis>_v<n>.md` | `implementation-planner` |
| **Axis specification** | `Spec_<axis>_v<n>.md`; `Spec_Action_Surface_v<n>.md`; `Spec_Control_Plane_v<n>.md`; `Spec_Information_Substrate_v<n>.md`; `Spec_Operational_Discipline_v<n>.md` | `spec-writer` |
| **Architectural Design Document** | `Architectural_Design_Document_v<n>.md` | `systems-architect` (Phase 3d) |
| **Product Requirements Document** | `PRD_v<n>.md` | `prd-author` |

Audit scope applies to BOTH initial-draft authoring sessions AND revision-pass sessions (per `implementation-planner` SKILL.md §8 and `spec-writer` SKILL.md §12 revision-pass disciplines).

##### 7.4.6.2 Audit pass shape

For every authoring session in §7.4.6.1 scope, the authoring skill MUST execute a pre-emission fidelity-grammar audit pass before artifact filing:

1. **Claim enumeration.** Enumerate every fidelity claim in the authored artifact. Classify each per §7.4.1 taxonomy.
2. **Per-claim verification.** Verify each classified claim against the corresponding §7.4.2 / §7.4.3 / §7.4.4 grammar.
3. **Sub-section-anchor resolution check.** Apply §7.4.5 discipline across all citations (regardless of fidelity-claim category).
4. **Disposition assignment.** Return one of three dispositions:

| Disposition | Criteria | Emission action |
|---|---|---|
| **PASS** | All fidelity claims grammar-conformant; all citations resolve at sub-section anchor; no P1 / P2 firings | Artifact MAY be emitted |
| **PARTIAL** | Some claims need reclassification (e.g., byte-exact downgraded to structural-fidelity); no falsified fidelity claims; no unresolved anchors | Reclassify in-place; re-run audit; if PASS, emit |
| **FAIL** | One or more byte-exact / structural-fidelity claims falsified by substrate; OR one or more unresolved sub-section anchors | Artifact MUST NOT be emitted; revise per audit findings; re-run audit |

##### 7.4.6.3 Audit-pass documentation

The audit pass disposition (PASS / PARTIAL / FAIL) and the per-claim classification table SHOULD be retained at the authoring session's working scope. The audit-pass record is NOT a filed artifact; it is authoring-session-internal discipline.

Adversarial review at the corresponding checkpoint (P6-CK for plans; P5-CK for specs; P3-CK for ADD; P4-CK for PRD) MAY request the audit record for verification. Absence of an executed audit pass at a covered artifact class is a Class 2 finding by default per §4.1 discriminator (a).

##### 7.4.6.4 Out-of-scope artifact classes

Per OD-Pδ-3 (B), the following artifact classes are explicitly NOT subject to §7.4.6 pre-emission audit:

| Out-of-scope artifact class | Existing discipline (preserved) |
|---|---|
| ADRs (F-class, D-class, I-class) | §§2.3.1.1 / 2.3.3.1 References-section discipline |
| Cross-Axis Composition Document (CXA) | §2.5 spec-authoring discipline at session boundary |
| Integration Verification Report | §2.3.4 Phase 3c exit-criteria discipline |
| Adversarial-review reports | `harness-adversarial-reviewer` SKILL.md authoring discipline |
| Kickoff artifacts | No formal pre-emission discipline; session-internal review only |
| Handoff artifacts | No formal pre-emission discipline; session-internal review only |
| Revision logs | §4.4 documentation discipline (already specifies trigger / severity / affected phases / resolution path) |
| Workflow document (this artifact) | §7.1–§7.3 versioning discipline |

The OD-Pδ-3 (B) scope is intentionally narrow. Operator may revisit at a future Workflow revision if out-of-scope artifact classes exhibit P1 / P2 pattern accumulation.

---

## §8. Open Questions and Known Unknowns

The following items the workflow does not yet specify, with explicit deferral rationale.

### 8.1 Fork severity classification thresholds

**Status:** First-pass criteria defined in §4.1 (Class 1: documentation drift; Class 2: ADR revision in current phase; Class 3: phase re-opening). Iteration-ceiling discipline added at §4.1.4 in workflow v1.6. Refined through actual cases.

**Deferral rationale:** Severity classification benefits from calibration against real findings. Predefining quantitative thresholds (e.g., "n findings = Class 2") would either be arbitrary or constrain the reviewer's judgment.

**Resolution trigger:** After P3a-CK produces actual findings, evaluate whether the qualitative criteria need quantitative anchors.

### 8.2 Phase abandonment handling

**Status:** Not specified. The workflow does not specify what happens if a phase cannot complete (e.g., council deadlocks, persona surfacing produces irreconcilable persona conflict, adversarial review produces unresolvable findings).

**Deferral rationale:** Phase abandonment is a low-frequency contingency; the resolution path likely depends on the specific abandonment cause. Premature specification would either over-constrain or under-specify.

**Resolution trigger:** First phase that approaches abandonment surfaces the gap.

### 8.3 Council deliberation token budget per design session

**Status:** Not specified. Each council session has an output budget but no explicit token budget allocation across the 11 voices.

**Deferral rationale:** Council deliberation patterns vary by topic; some topics engage 4 voices deeply, others touch all 11 lightly. Fixed per-voice budgets would distort deliberation shape.

**Resolution trigger:** Session-prompt-level discipline; revisit if deliberations consistently exceed session output budgets.

### 8.4 Systems architect skill at Phase 3d

**Status:** §6.1 names the systems architect skill as the Phase 3d execution agent. Alternative: technical writer skill (lower architectural authority, lower coupling to council outputs).

**Deferral rationale:** ADD consolidation is partly synthesis (which technical writer covers) and partly architectural reasoning (which systems architect covers). The right answer depends on whether Phase 3c integration verification is exhaustive enough that 3d is purely synthesis, or whether 3d needs ongoing architectural judgment.

**Resolution trigger:** P3c integration verification completion. If integration verification produces a complete consistency matrix with zero residual reasoning, technical writer suffices for 3d.

### 8.5 Criteria for workflow v2.0 (major revision)

**Status:** §7.1 distinguishes v1.x (minor) from v2.x (major) qualitatively. Specific thresholds not defined.

**Deferral rationale:** Workflow v2.0 is a contingency for substantial structural rework; it is unlikely to be needed within the project's expected lifecycle. Specifying thresholds for an unlikely event is premature.

**Resolution trigger:** Any workflow revision that the operator judges to be near the v1.x / v2.x boundary.

### 8.6 Iteration ceiling default beyond 2 iterations

**Status:** §4.1.4.1 establishes a 2-iteration ceiling default across all adversarial-review checkpoints. The default may prove too tight for high-finding-density checkpoints or too loose for low-finding-density checkpoints.

**Deferral rationale:** Per-checkpoint calibration requires data across multiple checkpoint runs. The first one-time ceiling-extension authorization at workflow v1.6 §4.1.4.5 (P6-CK Iter 3) provides one data point; pattern across checkpoints needed before adjusting the default.

**Resolution trigger:** After three or more Path B authorizations at the same checkpoint, evaluate whether §4.1.4.1 default should be revised systemically.

**Data-point accumulation at v1.8.** The §4.1.4.5 one-time P6-CK Iter 3 authorization (v1.6) and the §4.1.4.6 cascade-closure-substrate-driven P6-CK Iter 4 extension (v1.8) constitute **two ceiling-extension data points** at the P6-CK checkpoint. The §8.6 resolution trigger ("After three or more Path B authorizations at the same checkpoint, evaluate whether §4.1.4.1 default should be revised systemically") is not yet met; one additional ceiling-extension event at P6-CK would trigger systemic re-evaluation. Other checkpoints (P3a-CK, P3-CK, P5-CK) have not yet invoked ceiling extension; per-checkpoint pattern remains insufficient for systemic revision.

---

*End of Project Workflow v1.8.*

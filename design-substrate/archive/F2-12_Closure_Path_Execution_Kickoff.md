# F2-12 Closure-Path Execution Kickoff

## §1 Status block

| Field | Value |
|---|---|
| Artifact | `F2-12_Closure_Path_Execution_Kickoff.md` |
| Status | **Authorized** — Phase 7 entry-gate conditional routing per `Adversarial_Review_6_iter3.md` §11.4 + `P6-CK_Iteration_3_Close_Handoff.md` §5; mandatory closure path declared at `Spec_Control_Plane_v1.md` §8.4 + `Architectural_Design_Document_v1.md` §6.3.1 active path |
| Phase | Out-of-band cascade authoring; not gated to Phase 6 close cycle; required for Phase 7 entry-gate `F2-12 closure_pending false` precondition |
| Date | 2026-05-14 |
| Predecessor artifacts | `Spec_Control_Plane_v1.md` §8.4 (F2-12 carry-forward affected-contract notation, sub-scope enumeration); `Architectural_Design_Document_v1.md` §6.3.1 (active path declaration); `PRD_v1_0.md` §[carry-forwards] [CF-1]; `Implementation_Plan_Control_Plane_v2_1.md` U-CP-20 acceptance #5 (active engagement surface); `Implementation_Plan_Operational_Discipline_v2_1.md` U-OD-20 closure_path (canonical chain); `Implementation_Plan_Control_Plane_v2_1.md` U-CP-55 §24.4 export manifest |
| Successor artifacts | 6-step canonical chain — see §3.2 |
| Session-authoring skill | `council-orchestrator` SKILL.md (primary); `spec-writer` SKILL.md (cascade authoring sub-mode); `systems-architect` SKILL.md (ADD consolidation sub-mode); `prd-author` SKILL.md (PRD revision sub-mode); `implementation-planner` SKILL.md (plan revision sub-mode) |
| Out-of-scope | Iter-3 finding absorption (operator-decided Path C-i or Path C-ii per `P6-CK_Iteration_3_Close_Handoff.md` §3.3); Path δ Workflow §7 revision (parallel session per `Path_Delta_Workflow_v1_6_to_v1_7_Revision_Kickoff.md`); Phase 7 substantive entry |

---

## §2 Entry-gate verification

### §2.1 Prerequisites filed at session entry

| Prerequisite | Source | Status |
|---|---|---|
| F2-12 sub-scope enumeration on record | `Spec_Control_Plane_v1.md` §8.4 lines 764–770 | ✅ Filed |
| F2-12 active path declared | `Architectural_Design_Document_v1.md` §6.3.1 | ✅ Filed |
| F2-12 carry-forward referenced in PRD | `PRD_v1_0.md` §[carry-forwards] [CF-1] | ✅ Filed (PRD v1.0.1) |
| F2-12 active engagement surface declared at CP plan | `Implementation_Plan_Control_Plane_v2_1.md` U-CP-20 acceptance #5 + `Implementation_Plan_Control_Plane_v2_1.md` line 219 (`carry-forward affected-contract` notation) | ✅ Filed |
| F2-12 closure_path declared at OD plan | `Implementation_Plan_Operational_Discipline_v2_1.md` U-OD-20 (canonical 6-step chain) | ✅ Filed |
| F2-12 closure routing acknowledged at Iter-1 + Iter-2 + Iter-3 close handoffs | `P6-CK_Iter1_Revision_Cycle_Close_Handoff.md` §7 + `P6-CK_Iteration_2_Ceiling_Disposition.md` §8 + `P6-CK_Iteration_3_Close_Handoff.md` §5 | ✅ Filed |

### §2.2 Strongly-recommended preconditions (not hard prerequisites)

| Precondition | Rationale | Status |
|---|---|---|
| Path δ Workflow §7 fidelity-grammar revision filed (v1.6 → v1.7) | Cascade produces 6+ newly-authored artifacts (D1 v1.2, D6 v1.2, ADD v1.3, PRD v1.1, CP spec v1.3, OD spec v1.3, plan v2.2 + plan v2.2). Authoring under Workflow v1.6 risks Pattern P2 / Pattern P1 propagation per `Adversarial_Review_6_iter3.md` §6.1 + §6.2 cumulative-evidence accumulation | Conditional — operator may proceed without Path δ but accepts P2/P1 propagation risk |

**Recommendation.** Path δ filed before F2-12 cascade authoring entry. Path δ session is `ask_user_input_v0`-driven and substantively shorter than the F2-12 cascade; sequencing Path δ first imposes minimal forward-velocity cost and absorbs strengthened authoring discipline into F2-12 cascade artifacts.

### §2.3 Entry-gate disposition

**AUTHORIZED.** All §2.1 prerequisites satisfied. F2-12 closure-path execution session entry permitted. Operator decides Path δ sequencing per §2.2 + OD-F212-1 (Section §6.1).

---

## §3 F2-12 scope summary

### §3.1 Three sub-scopes per CP spec §8.4

F2-12 is the **12th carry-forward item from the F2 ADR cluster** (per `Spec_Control_Plane_v1.md` §24.4 carry-forward inventory). F2-12 covers three replay-time observability semantics that remained out-of-scope at the v1.x spec revision boundary:

| Sub-scope | Defect surface | Affected substrate |
|---|---|---|
| **(i) Span re-emission semantics under engine replay** | Event-sourced-replay engines: do spans re-emit at replay time, or is replay a deterministic re-read without new span emission? Affects D1 §1.1 lifecycle envelope at engine-replay boundary. | ADR-D1 v1.1 §1.1 lifecycle envelope + ADR-D6 v1.1 §1.2 cost-attribution-per-span at replay boundary |
| **(ii) `retry.attempt` sibling-span discipline** | Does the retry emit `retry.attempt` event AND a new sibling span per D6 §1.2? Affects retry observability composition with engine-replay boundary. | ADR-D6 v1.1 §1.2 sibling-span discipline + CP spec §5.4 retry.attempt sampling discipline |
| **(iii) Trace-ingestion dedup composition with F2 `idempotency_key`** | Cost-attribution-per-span at D6 §1.5 must avoid double-counting on replay. F2 idempotency_key join key (per IS spec §10.2) must compose with D6 ingestion dedup at replay boundary. | ADR-D6 v1.1 §1.5 cost-attribution + IS spec §10.2 idempotency_key join + OD spec cost-attribution-per-span contract |

### §3.2 Canonical 6-step closure cascade

```
F2-12 CLOSURE CASCADE (canonical chain)
│
├── STEP 1 ─ Council deliberation (C7 + C9 primary; C3 + C5 + C1 + C11 consultants)
│            ├── Resolve sub-scope (i) span re-emission semantics
│            ├── Resolve sub-scope (ii) retry.attempt sibling-span discipline
│            └── Resolve sub-scope (iii) trace-ingestion dedup composition
│
├── STEP 2 ─ ADR revisions absorb council resolutions
│            ├── ADR-D1 v1.1 → v1.2 (span re-emission semantics — sub-scope (i))
│            └── ADR-D6 v1.1 → v1.2 (retry.attempt sibling-span + dedup composition — (ii) + (iii))
│
├── STEP 3 ─ ADD consolidation
│            └── Architectural_Design_Document v1.2 → v1.3 (consolidates D1 v1.2 + D6 v1.2)
│
├── STEP 4 ─ PRD revision pass
│            └── PRD v1.0.1 → v1.1 (closes carry-forward [CF-1]; R-CP-* + R-OD-* requirements
│                                   amended to reflect resolved replay-observability semantics)
│
├── STEP 5 ─ Spec revisions
│            ├── Spec_Control_Plane v1.2 → v1.3 (C-CP-08 + C-CP-09 + §5.4 retry sampling)
│            └── Spec_Operational_Discipline v1.2 → v1.3 (cost-attribution-per-span contract)
│
└── STEP 6 ─ Plan revisions
             ├── Implementation_Plan_Control_Plane v2.1 → v2.2 (downstream of CP spec v1.3)
             └── Implementation_Plan_Operational_Discipline v2.1 → v2.2 (downstream of OD spec v1.3)
```

### §3.3 Cascade-step authoring agents

| Step | Authoring agent | Skill activated |
|---|---|---|
| Step 1 | Council deliberation | `council-orchestrator` SKILL.md with C7 + C9 convening; consultants invoked per §4 council convening shape |
| Step 2 | ADR revision authoring | Council-produced; `spec-writer` SKILL.md formalizes per ADR amendment-protocol discipline |
| Step 3 | ADD consolidation | `systems-architect` SKILL.md (ADD consolidation sub-mode; analogous to Phase 3d original ADD authoring) |
| Step 4 | PRD revision pass | `prd-author` SKILL.md (revision-pass sub-mode per `prd-author` SKILL §[revision-pass]) |
| Step 5 | Spec revision pass | `spec-writer` SKILL.md §12 (spec-revision-pass sub-mode) |
| Step 6 | Plan revision pass | `implementation-planner` SKILL.md §8 (revision-pass sub-mode) |

---

## §4 Council convening shape

### §4.1 Voice assignments

Per `council-orchestrator` SKILL.md convening-block discipline + voice-domain ownership per individual voice SKILL.md files:

| Voice | Role | Domain rationale |
|---|---|---|
| **C7 Observability Architect** | Primary | Owns OTel GenAI semconv + span schema + per-attribute discipline + sampling. F2-12 sub-scopes (i) + (iii) are span-emission-discipline territory. |
| **C9 Reliability & Recovery Engineer** | Primary | Owns retry mechanics + retry.attempt event semantics + per-attempt timeout + breaker-trip event composition. F2-12 sub-scope (ii) is retry.attempt sibling-span discipline territory. |
| **C3 State, Memory & Persistence Architect** | Consultant | Owns durable state + F2 state-ledger entry shape + idempotency_key as canonical join key. F2-12 sub-scope (iii) trace-ingestion dedup composes against F2 state-ledger join surface (C3 territory). |
| **C5 Validation Contract Architect** | Consultant | Owns fail-classification at runtime gates. F2-12 sub-scope (i) span re-emission disposition under engine-replay boundary affects fail-class attribution at replay-time. |
| **C1 Orchestration & Control Architect** | Consultant | Owns control-flow + topology. F2-12 sub-scope (ii) retry.attempt sibling-span discipline affects parent-child topology under retry composition. |
| **C11 Operator Loop & Local Deployment Specialist** | Consultant | Owns TUI trace browser + operator-experience at replay-time event visibility. F2-12 sub-scope (i) span re-emission at replay-time affects TUI trace inspection surface. |

### §4.2 Convening shape options (OD-F212-2)

| Option | Convening shape | Trade-off |
|---|---|---|
| **(A) Full 6-voice convening at session open** | All 6 voices (C7 + C9 + C3 + C5 + C1 + C11) convened at session open; consultants contribute prefix-block readings before primary deliberation | Maximum domain coverage; longest delivery; consultant voices may contribute beyond scope on adjacent territory |
| **(B) Primary-only (C7 + C9) with ad-hoc consultants** | C7 + C9 convened at session open; C3 / C5 / C1 / C11 invoked ad-hoc when their domain surfaces in deliberation | Tighter primary deliberation; consultants invoked only when their domain is engaged; minimum convening overhead |
| **(C) Sub-scope-paired primaries** | Sub-scope (i) primary = C7 + C3; sub-scope (ii) primary = C9 + C1; sub-scope (iii) primary = C7 + C3; other voices ad-hoc | Per-sub-scope domain-anchored deliberation; voice-pair primary aligns with sub-scope content territory |

**Default recommendation: (B) Primary-only with ad-hoc consultants.** Per established `council-orchestrator` SKILL.md convening discipline. Primary voices (C7 + C9) cover the majority of F2-12 substantive territory; consultants invoked when their domain surfaces (per voice-skill activation triggers).

### §4.3 Tension surfacing

Per `council-orchestrator` SKILL.md TENSION block discipline + permanent tension ledger:

| Permanent tension | F2-12 engagement |
|---|---|
| **T-perm-3 (C1↔C9 — topology-vs-retry composition)** | Engaged at sub-scope (ii) — retry.attempt sibling-span discipline composes against topology (parent-child span hierarchy under retry). Resolution shape: per-sibling F2 ledger composition with retry.attempt event vs parent-fanout topology. |
| **T-perm-2 (C2↔C3 — within-turn-vs-durable composition)** | Engaged at sub-scope (iii) — trace-ingestion dedup composition spans within-turn span emission (C7 territory; OTel SDK) and across-turn durable trace storage (C3 territory; F2 ledger). |
| **T-perm-1 (C4↔C10 — tool-trust-vs-blast-radius)** | Not directly engaged at F2-12 scope; absent unless sub-scope (i) replay touches tool-call replay disposition (operator decides per OD-F212-3 sub-scope scoping). |

T-perm-3 and T-perm-2 surface at F2-12 deliberation. Resolutions documented in council output per `council-orchestrator` SKILL.md TENSION-block discipline.

---

## §5 Substrate references

### §5.1 F2-12 scope substrate

| Substrate | Role at this kickoff |
|---|---|
| `Spec_Control_Plane_v1.md` §8.4 | F2-12 sub-scope enumeration (lines 764–770) — canonical 3-sub-scope source |
| `Architectural_Design_Document_v1.md` §6.3.1 | F2-12 active path declaration |
| `PRD_v1_0.md` §[carry-forwards] [CF-1] | PRD-side carry-forward record |
| `Implementation_Plan_Control_Plane_v2_1.md` U-CP-20 acceptance #5 | CP plan-side active engagement surface |
| `Implementation_Plan_Operational_Discipline_v2_1.md` U-OD-20 closure_path | OD plan-side canonical 6-step chain reference |
| `Implementation_Plan_Control_Plane_v2_1.md` U-CP-55 §24.4 + line 219 | CP plan-side export manifest declaration |

### §5.2 ADR substrate (revision targets at Step 2)

| Substrate | Revision target | Sub-scope addressed |
|---|---|---|
| `ADR-F2.md` v1.2 (referenced upstream) | Not directly revised; F2 cluster ADR ancestor | — |
| `ADR-D1.md` v1.1 | **→ v1.2** | Sub-scope (i) span re-emission semantics |
| `ADR-D6.md` v1.1 | **→ v1.2** | Sub-scopes (ii) retry.attempt sibling-span + (iii) trace-ingestion dedup composition |

### §5.3 Downstream cascade substrate

| Substrate | Revision target |
|---|---|
| `Architectural_Design_Document_v1.md` v1.2 | **→ v1.3** (Step 3 consolidation) |
| `PRD_v1_0.md` v1.0.1 | **→ v1.1** (Step 4 revision pass) |
| `Spec_Control_Plane_v1.md` v1.2 | **→ v1.3** (Step 5; C-CP-08 + C-CP-09 + §5.4) |
| `Spec_Operational_Discipline_v1.md` v1.2 | **→ v1.3** (Step 5; cost-attribution-per-span contract) |
| `Implementation_Plan_Control_Plane_v2_1.md` v2.1 | **→ v2.2** (Step 6) |
| `Implementation_Plan_Operational_Discipline_v2_1.md` v2.1 | **→ v2.2** (Step 6) |

### §5.4 Skills

| Skill | Role |
|---|---|
| `council-orchestrator` SKILL.md | Step 1 council convening + deliberation |
| Individual voice SKILL.md files (`c7-observability`, `c9-reliability-recovery`, `c3-state-persistence`, `c5-validation-contract`, `c1-orchestration-control`, `c11-operator-local`) | Step 1 per-voice domain contributions |
| `spec-writer` SKILL.md (council-formalization sub-mode) | Step 2 ADR revision formalization |
| `systems-architect` SKILL.md (ADD consolidation sub-mode) | Step 3 ADD v1.3 consolidation |
| `prd-author` SKILL.md (revision-pass sub-mode) | Step 4 PRD revision pass |
| `spec-writer` SKILL.md §12 (spec-revision-pass sub-mode) | Step 5 spec revisions |
| `implementation-planner` SKILL.md §8 (revision-pass sub-mode) | Step 6 plan revisions |

### §5.5 Adversarial-review gating substrate

| Substrate | Gating role at downstream phase entry |
|---|---|
| `Project_Workflow_v1_6.md` (or v1.7 under Path δ priority) §4.1 | Adversarial-review checkpoint framework — P3-CK (ADD), P5-CK (specs), P6-CK (plans) re-entry conditions |
| `Project_Workflow_v1_6.md` §4.1.4.5 | One-time P6-CK extension expended at Iter 3; further P6-CK iteration requires separate amendment (see §10.2) |

---

## §6 Operator Decision (OD) inventory

OD selections required at session open. Delivered via `ask_user_input_v0` single-select menus.

### §6.1 OD-F212-1 — Path δ sequencing

Determines whether F2-12 cascade entry waits on Path δ Workflow v1.7 filing.

| Option | Sequencing shape | Rationale |
|---|---|---|
| (A) **Path δ before F2-12** | F2-12 entry deferred until `Project_Workflow_v1_7.md` filed; cascade authored under v1.7 fidelity-grammar discipline | Minimum P2/P1 propagation risk; cascade artifacts inherit strengthened discipline; Path δ session is `ask_user_input_v0`-driven and short |
| (B) **F2-12 before Path δ** | F2-12 entry proceeds under Workflow v1.6; Path δ deferred to post-cascade or parallel | Forward-velocity priority; accepts P2/P1 propagation risk at cascade artifacts; cascade artifacts subject to v1.6 discipline at filing |
| (C) **Parallel** | F2-12 and Path δ proceed in parallel; cascade artifact filing dates determine which Workflow version applies (v1.6 or v1.7) | Mixed discipline application; complicates verification at adversarial-review checkpoints |

**Default recommendation: (A) Path δ before F2-12.** Per `Path_Delta_Workflow_v1_6_to_v1_7_Revision_Kickoff.md` §8.3 strong recommendation + §2.2 of this kickoff.

### §6.2 OD-F212-2 — Council convening shape

Determines convening shape for Step 1 council deliberation per §4.2.

| Option | Convening shape | Reference |
|---|---|---|
| (A) Full 6-voice convening at session open | C7 + C9 + C3 + C5 + C1 + C11 all convened | §4.2 option A |
| (B) Primary-only with ad-hoc consultants | C7 + C9 convened; C3 / C5 / C1 / C11 ad-hoc | §4.2 option B |
| (C) Sub-scope-paired primaries | Per-sub-scope voice-pair primaries | §4.2 option C |

**Default recommendation: (B) Primary-only with ad-hoc consultants.** Per `council-orchestrator` SKILL.md established convening discipline.

### §6.3 OD-F212-3 — Sub-scope deliberation ordering

Determines whether Step 1 council deliberation addresses sub-scopes (i) / (ii) / (iii) sequentially, in parallel, or in operator-defined order.

| Option | Ordering shape | Trade-off |
|---|---|---|
| (A) Sequential (i) → (ii) → (iii) | Each sub-scope deliberated to resolution before next sub-scope opens | Cleanest per-sub-scope deliberation traceability; longest cumulative session time |
| (B) Parallel | All 3 sub-scopes deliberated within single convening; council resolves cross-sub-scope dependencies in-band | Shortest session time; cross-sub-scope dependencies (e.g., sub-scope (iii) consumes sub-scope (i) span-emission disposition) surfaced in council deliberation |
| (C) Sequential (i) → (iii) → (ii) | Reordered sequential; sub-scope (iii) precedes (ii) because retry.attempt sibling-span discipline (ii) depends on trace-ingestion dedup behavior (iii) | Sequential traceability + dependency-aware ordering |

**Default recommendation: (A) Sequential (i) → (ii) → (iii).** Matches spec §8.4 enumeration order; per-sub-scope deliberation traceability is preserved for downstream ADR-D1 v1.2 + ADR-D6 v1.2 amendment authorship.

### §6.4 OD-F212-4 — Cascade-step delivery cadence

Determines whether the 6-step cascade is authored in a single session, multiple sessions, or per-step sessions.

| Option | Cadence shape | Trade-off |
|---|---|---|
| (A) **Single combined session** | Steps 1–6 authored in single multi-turn session with operator-confirmed segment boundaries between steps | Continuous context; single closure-handoff; longest session |
| (B) **Per-step sessions (6 sessions)** | One session per step; per-step handoff documents step boundary | Per-step pacing; cleanest per-step traceability; longest cumulative wall-clock time |
| (C) **Phase-paired sessions (3 sessions)** | Session 1 = Step 1 council deliberation + Step 2 ADR revisions; Session 2 = Steps 3 + 4 (ADD + PRD); Session 3 = Steps 5 + 6 (specs + plans) | Aligns sessions with substrate-class groupings (council outputs / architectural docs / implementation substrate); 3 handoff boundaries |

**Default recommendation: (C) Phase-paired sessions (3 sessions).** Aligns session boundaries with substrate-class groupings; preserves intermediate handoff artifacts at meaningful substrate-class transitions; consistent with project's established three-segment-delivery pacing pattern.

### §6.5 OD-F212-5 — Phase 7 entry-gate disposition for plan v2.2 production

Determines the workflow-routing shape for the v2.2 plans (Step 6 outputs) given that Workflow v1.6 §4.1.4.5 one-time P6-CK extension is expended.

| Option | Routing shape | Trade-off |
|---|---|---|
| (A) **F2-12-closure-substrate exemption** | Plan v2.2 authored as F2-12-closure-derived absorption; treated as Phase 7 entry-gate-cleared without P6-CK re-review; closure_pending flag toggles to false at v2.2 filing | Forward-velocity priority; treats F2-12 cascade as substantive remediation sufficient to satisfy Phase 7 entry-gate; accepts no fresh adversarial-review gate on v2.2 |
| (B) **Workflow §4.1.4.6 amendment** | Workflow v1.6 (or v1.7 under Path δ) §4.1.4 amended to authorize a one-time P6-CK Iter 4 specifically for F2-12-cascade-derived v2.2 plans; plan v2.2 reviewed under P6-CK Iter 4 against revised specs | Preserves adversarial-review gate; engages explicit workflow-revision action; longest forward-routing path |
| (C) **Plan v2.2 deferred to Phase 7 carry-forward** | Step 6 produces draft plan v2.2 with carry-forward annotation; substantive plan revision occurs during Phase 7 implementation; F2-12 closure_pending toggles to false at draft-v2.2 filing | Hybrid; ADR + ADD + PRD + spec cascade complete; plan revision absorbed at implementation time |

**Default recommendation: (B) Workflow §4.1.4.6 amendment.** Preserves adversarial-review gate; consistent with `P6-CK_Iteration_2_Ceiling_Disposition.md` §4 amendment precedent. Operator decides at the Step 6 boundary (after Steps 1–5 deliver substantive substrate); no decision required at this kickoff session open.

---

## §7 Per-cascade-step session discipline

### §7.1 Step 1 — Council deliberation

Per `council-orchestrator` SKILL.md:

| Element | Discipline |
|---|---|
| Convening block | Per OD-F212-2 selection |
| CCR (cross-cutting-resolution) | Required for tensions surfaced per §4.3 |
| Per-voice contributions | Per OD-F212-3 sub-scope ordering |
| TENSION block | Required for T-perm-2 + T-perm-3 surfacings |
| Output target | Council deliberation transcript filed as `F2-12_Council_Deliberation_Output.md` |

### §7.2 Step 2 — ADR revisions

Per `spec-writer` SKILL.md (council-formalization sub-mode) + `harness-adversarial-reviewer` SKILL.md ADR-review framing:

| Element | Discipline |
|---|---|
| ADR-D1 v1.2 amendment scope | Sub-scope (i) span re-emission semantics; preserve all D1 v1.1 substantive content not affected by F2-12 |
| ADR-D6 v1.2 amendment scope | Sub-scopes (ii) retry.attempt sibling-span + (iii) trace-ingestion dedup composition; preserve all D6 v1.1 substantive content not affected by F2-12 |
| `Status:` field | `Status: Proposed` until ADD v1.3 consolidation (Step 3) absorbs |
| §0 amendment trace | Required per ADR-revision protocol |

### §7.3 Step 3 — ADD consolidation

Per `systems-architect` SKILL.md (ADD consolidation sub-mode):

| Element | Discipline |
|---|---|
| ADD v1.3 consolidation scope | Integrate ADR-D1 v1.2 + ADR-D6 v1.2 substantive amendments; update §6.3.1 active path to record F2-12 closure |
| Traceability | Every ADD claim traces to ADR (D1 v1.2 or D6 v1.2); F2-12 sub-scope (i)/(ii)/(iii) trace-anchored to council deliberation output |
| §0 amendment trace | Required per ADD-revision pattern |

### §7.4 Step 4 — PRD revision pass

Per `prd-author` SKILL.md (revision-pass sub-mode):

| Element | Discipline |
|---|---|
| PRD v1.1 amendment scope | Close [CF-1] carry-forward; amend R-CP-* + R-OD-* requirements affected by F2-12 closure |
| §[carry-forwards] section | [CF-1] removed; status updated to "closed at F2-12 cascade Step 4" |

### §7.5 Step 5 — Spec revisions

Per `spec-writer` SKILL.md §12 (spec-revision-pass sub-mode):

| Element | Discipline |
|---|---|
| CP spec v1.3 amendment scope | C-CP-08 §8.4 F2-12 affected-contract notation amended; replay-disposition content added per ADR-D1 v1.2 + council resolution; C-CP-09 §9.x amended per sub-scope (i) span-emission disposition; §5.4 retry.attempt sampling discipline amended per sub-scope (ii) |
| OD spec v1.3 amendment scope | Cost-attribution-per-span contract amended per sub-scope (iii); trace-ingestion dedup composition added per ADR-D6 v1.2 |
| Adversarial-review re-entry | P5-CK re-entry against revised specs |

### §7.6 Step 6 — Plan revisions

Per `implementation-planner` SKILL.md §8 (revision-pass sub-mode):

| Element | Discipline |
|---|---|
| CP plan v2.2 amendment scope | Downstream of CP spec v1.3 + OD spec v1.3 substrate updates; U-CP-20 acceptance #5 carry-forward declaration revised to record closure; U-CP-55 §24.4 export manifest amended |
| OD plan v2.2 amendment scope | Downstream of OD spec v1.3; U-OD-20 closure_path closure status revised |
| Adversarial-review re-entry | Conditional on OD-F212-5 (Section §6.5) selection |

---

## §8 Out-of-scope reminders

### §8.1 Not in F2-12 closure cascade scope

| Concern | Reason out-of-scope | Routing |
|---|---|---|
| Iter-3 finding absorption (C1 / C2 / C3 / C4) | Operator-decided Path C-i (Phase 7 carry-forward) or Path C-ii (spec revision) per `P6-CK_Iteration_3_Close_Handoff.md` §3.3 | Phase 7 entry session (under Path C-i) OR `spec-writer` SKILL §12 session (under Path C-ii) — orthogonal to F2-12 cascade |
| Path δ Workflow §7 revision | Parallel session; mandatory but separate scope | `Path_Delta_Workflow_v1_6_to_v1_7_Revision_Kickoff.md` |
| Phase 7 substantive entry | Conditioned on F2-12 closure_pending false + Path C disposition + (under OD-F212-5.B) P6-CK Iter 4 clearance | Phase 7 entry session — gated downstream of this cascade |
| F2-12 sub-scope expansion beyond CP spec §8.4 enumeration | Strict-narrow — only the 3 enumerated sub-scopes (i)/(ii)/(iii) addressed; no additional carry-forward items folded in | Separate carry-forward cascade if additional items emerge |
| ADR-F2 v1.2 revision | F2-12 is a F2-cluster carry-forward but cascade-step 2 targets D1 + D6 (per spec §8.4 closure expected as D1 v1.2 + D6 v1.2); F2 itself not directly revised | No F2 revision at this cascade |

### §8.2 Anti-pattern reminders

| Anti-pattern | Discipline source |
|---|---|
| Council author-mode drift | `council-orchestrator` SKILL.md — council deliberates and outputs decisions; does not author downstream cascade artifacts directly (Steps 2+ are skill-formalized) |
| Sub-scope scope creep | Strict-narrow per §8.1 — only sub-scopes (i)/(ii)/(iii) addressed |
| Cascade-step parallelization (Steps 2+ in parallel with Step 1 council deliberation) | Forbidden — cascade is dependency-ordered; Step N requires Step N−1 output as substrate |
| Pattern P2 (verbatim-claim-contradicted) propagation | Avoided by Path δ priority (under OD-F212-1.A); without Path δ, cascade authors apply fidelity-grammar discipline manually |
| Workflow v1.6 §4.1.4.5 silent extension | Forbidden — P6-CK Iter 4 (if needed under OD-F212-5.B) requires explicit Workflow §4.1.4 amendment; cascade does not implicitly extend the ceiling |

---

## §9 Session outputs

### §9.1 Primary outputs (in cascade dependency order)

| # | Artifact | Step | Authoring | Filing path |
|---|---|---|---|---|
| 1 | `F2-12_Council_Deliberation_Output.md` | Step 1 | `council-orchestrator` | `/mnt/user-data/outputs/` |
| 2 | `ADR-D1_v1_2.md` | Step 2 | `spec-writer` (council-formalization) | `/mnt/user-data/outputs/` |
| 3 | `ADR-D6_v1_2.md` | Step 2 | `spec-writer` (council-formalization) | `/mnt/user-data/outputs/` |
| 4 | `Architectural_Design_Document_v1_3.md` | Step 3 | `systems-architect` (ADD consolidation) | `/mnt/user-data/outputs/` |
| 5 | `PRD_v1_1.md` | Step 4 | `prd-author` (revision pass) | `/mnt/user-data/outputs/` |
| 6 | `Spec_Control_Plane_v1_3.md` | Step 5 | `spec-writer` §12 (spec-revision pass) | `/mnt/user-data/outputs/` |
| 7 | `Spec_Operational_Discipline_v1_3.md` | Step 5 | `spec-writer` §12 (spec-revision pass) | `/mnt/user-data/outputs/` |
| 8 | `Implementation_Plan_Control_Plane_v2_2.md` | Step 6 | `implementation-planner` §8 (revision pass) | `/mnt/user-data/outputs/` |
| 9 | `Implementation_Plan_Operational_Discipline_v2_2.md` | Step 6 | `implementation-planner` §8 (revision pass) | `/mnt/user-data/outputs/` |

### §9.2 Per-session handoff artifacts (under OD-F212-4.C 3-session cadence)

| Session boundary | Handoff artifact |
|---|---|
| End of Session 1 (Steps 1 + 2) | `F2-12_Cascade_Session_1_Close_Handoff.md` |
| End of Session 2 (Steps 3 + 4) | `F2-12_Cascade_Session_2_Close_Handoff.md` |
| End of Session 3 (Steps 5 + 6) | `F2-12_Cascade_Closure_Handoff.md` (terminal — declares F2-12 closure_pending false) |

### §9.3 Final closure-declaration artifact

`F2-12_Closure_Declaration.md` — filed at cascade close. Required content:

| Section | Content |
|---|---|
| §1 | F2-12 closure_pending false declaration (with substrate update to U-CP-20 acceptance #5 + U-OD-20 closure_path + ADD §6.3.1 + PRD [CF-1]) |
| §2 | Per-sub-scope resolution summary (sub-scopes (i)/(ii)/(iii) outcomes) |
| §3 | Cascade-artifact inventory (9 artifacts per §9.1) |
| §4 | Adversarial-review re-entry disposition (P5-CK + P6-CK routing per OD-F212-5 selection) |
| §5 | Phase 7 entry-gate disposition |

---

## §10 Forward routing

### §10.1 Adversarial-review re-entry conditions

| Phase checkpoint | Re-entry trigger | Workflow basis |
|---|---|---|
| P5-CK (specifications) | Spec_Control_Plane_v1_3 + Spec_Operational_Discipline_v1_3 filed | Workflow v1.6 (or v1.7) §4.1 P5-CK admissibility; standard 2-iteration ceiling per §4.1.4.1 |
| P6-CK (implementation plans) | Plan_v2_2 artifacts filed | Workflow v1.6 §4.1.4.5 one-time extension expended at Iter 3; **further P6-CK iteration requires Workflow §4.1.4.6 amendment** per OD-F212-5.B routing |

### §10.2 P6-CK ceiling reminder

`Project_Workflow_v1_6.md` §4.1.4.5 explicitly authorizes P6-CK Iteration 3 as a one-time extension. F2-12 cascade-derived plan v2.2 production engages the P6-CK boundary again; admissibility requires:

- OD-F212-5.A: exemption (no fresh P6-CK gate), OR
- OD-F212-5.B: Workflow §4.1.4 amendment authorizing P6-CK Iter 4 specifically for F2-12-derived plan v2.2, OR
- OD-F212-5.C: plan v2.2 deferred to Phase 7 implementation carry-forward (no fresh P6-CK gate at v2.2 filing)

Decision deferred to Step 6 boundary (post-Steps 1–5 substantive substrate cascade).

### §10.3 Phase 7 entry-gate trigger

Per `Adversarial_Review_6_iter3.md` §11.4:

```
PHASE 7 ENTRY GATE (post-F2-12 cascade close)
│
├── P6-CK route ────── Iter-3 disposition pending (PRE-CLEARANCE REVISION)
│                      │
│                      ├── Path C-i: Phase 7 carry-forward of 4 Iter-3 findings (C1, C2, C3, C4)
│                      └── Path C-ii: spec revision per `spec-writer` SKILL §12
│
└── F2-12 route ────── closure_pending false at this cascade close
                       │
                       └── Cascade-derived substrate filed per §9.1
```

Both routes converge at Phase 7 entry session. Phase 7 admissibility requires:
- Iter-3 Path C disposition selected + per-path absorption disposition recorded
- F2-12 cascade complete + closure_pending false declared
- (Under OD-F212-5.A or .C) plan v2.2 absorption disposition recorded
- (Under OD-F212-5.B) P6-CK Iter 4 CLEARED disposition recorded

---

## §11 Filing footer

| Field | Value |
|---|---|
| Artifact | `F2-12_Closure_Path_Execution_Kickoff.md` |
| Status | Authorized for session entry per `Spec_Control_Plane_v1.md` §8.4 + `Architectural_Design_Document_v1.md` §6.3.1 active path declaration; Phase 7 entry-gate conditional routing per `Adversarial_Review_6_iter3.md` §11.4 |
| Filing destination | `/mnt/user-data/outputs/F2-12_Closure_Path_Execution_Kickoff.md` |
| Operator action at session open | Present OD-F212-1 + OD-F212-2 + OD-F212-3 + OD-F212-4 via `ask_user_input_v0` single-select menus per established session discipline; OD-F212-5 deferred to Step 6 boundary |
| Strongly-recommended precondition | `Project_Workflow_v1_7.md` filed (via `Path_Delta_Workflow_v1_6_to_v1_7_Revision_Kickoff.md` session) before cascade entry |
| Date | 2026-05-14 |

*Filed at Iter-3 close + 1. F2-12 closure-path execution authorized. 6-step canonical cascade entry permitted. Cascade closure → Phase 7 entry-gate F2-12 precondition satisfied.*

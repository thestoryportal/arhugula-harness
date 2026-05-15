# Phase 6 Entry Handoff

## Status block

| Field | Value |
|---|---|
| Artifact | `Phase_6_Entry_Handoff.md` |
| Status | **Filed** — routing substrate for Phase 6 atomic implementation plan authoring arc |
| Date | 2026-05-14 |
| Phase | 5 close → Phase 6 entry boundary |
| Substrate | `Spec_Information_Substrate_v1.md` v1.2 + `Spec_Action_Surface_v1.md` v1.1 + `Spec_Control_Plane_v1.md` v1.2 + `Spec_Operational_Discipline_v1.md` v1.2 + `Specification_v1.md` v1.1 (primary Phase 6 substrate — P5-CK-cleared specification artifact set); `Architectural_Design_Document_v1.md` v1.2 (deeper substrate); `PRD_v1_0.md` v1.0.1 (deeper substrate); `Persona_Document_v1.md` (persona-linkage trace); F1–F5 + D1–D6 ADRs (canonical commitment substrate via ADD); `Project_Workflow_v1_5.md` §2.6 + §2.6.1 + §6.4 (Phase 6 + P6-CK + implementation-planner skill framing) |
| Skill activation | `implementation-planner` SKILL.md (per Workflow §6.4 + verified present at `/mnt/skills/user/implementation-planner/SKILL.md` resolving OD-6-1.C); council voices as consultants per Workflow §2.6 only on cross-axis composition seams; spec-writer SKILL.md NOT activated at plan-authoring (skill bounds at §2 Activation discipline excludes Phase 6 implementation work) |
| Entry authorization | Phase 5 final-revision-pass close at `P5-CK_Iteration_2_Revision_Pass_Close_Handoff.md` §10 (CONDITIONAL CLEARANCE → final operator-authored revision pass COMPLETE; iteration ceiling 2 of 2 consumed; §4.1.2 escalation available but not triggered); Phase 6 entry-gate AUTHORIZED per close handoff §5 row 1–7 transition to ✅ MET via operator push at session entry |
| Arc shape | 5 sessions per OD-6-5.A (4 per-axis plan-authoring sessions + 1 cross-axis composition session) per Workflow §2.6 Sessions field "2–4 sessions" — exceeds nominal estimate; rationale per §7.1 below |
| Exit gate | All implementation plan documents filed; topological sort of units acyclic; every specification contract covered by ≥1 unit; every unit has explicit acceptance criteria; P6-CK CLEARED per Workflow §2.6.1 |

---

## §1 Operator pre-decisions (ODs) — captured at Phase 6 entry

### 1.1 OD selection summary

Five operator pre-decisions captured at Phase 6 entry session. Selections recorded at session entry via tappable `ask_user_input_v0` menus per established protocol.

| OD | Question | Selection | Rationale |
|---|---|---|---|
| OD-6-1 | Implementation-planner skill build strategy | **C** — adopt existing skill | Verification at session entry confirmed `/mnt/skills/user/implementation-planner/SKILL.md` present; encodes atomic-decomposition + spec-traceability + dependency-graph discipline per session prompt Stage 2 specification; JIT build (A) unnecessary; multi-session build (B) unwarranted |
| OD-6-2 | Implementation plan document structure | **A** — per-axis multi-document | Inherits Phase 5 OD-5-1.A per-axis multi-document precedent; preserves per-axis traceability to source spec contracts; aligns plan-layer decomposition with spec-layer decomposition |
| OD-6-3 | Implementation plan unit ordering | **A** — dependency-graph topological sort | Canonical per Workflow §2.6 exit criterion ("topological sort of units is acyclic"); aligns with implementation-planner SKILL.md §7 dependency-graph discipline (DAG invariant; foundational-first; direct-not-transitive declarations) |
| OD-6-4 | P6-CK aggregation strategy | **A** — aggregate at full Phase 6 close | Inherits OD-5-4.A aggregate-checkpoint precedent; one P6-CK invocation per Workflow §2.6.1 Sessions field "1 session"; aggregate review surfaces cross-axis defects that per-axis interim checkpoints would miss |
| OD-6-5 | Session sequencing within Phase 6 | **A** — entry + skill build at entry session; 4 per-axis + 1 cross-axis = 5 plan-authoring sessions | Per-axis serial authoring matches Phase 5 5-session precedent; under OD-6-1.C the Stage 2 skill-build collapses at entry session but per-axis session count is independent of skill-build path |

### 1.2 OD-6-1 path-C effect on session structure

OD-6-1.C resolution collapses the session-prompt Stage 2 (skill JIT build) out of the entry session. Entry session deliverables reduce from three to two:

| Stage | Skill | Deliverable | Status at this handoff |
|---|---|---|---|
| 1 | spec-writer | `Phase_6_Entry_Handoff.md` | **This artifact** (in flight) |
| 2 (collapsed) | — | — | OD-6-1.C: existing skill adopted |
| 3 | spec-writer | `Phase_6_Session_1_Session_Prompt.md` | Authored next at Segment 2 of this turn |

### 1.3 ODs explicitly NOT at the menu (non-decisions per skill discipline)

| Rejected OD | Reason for rejection |
|---|---|
| Per-unit risk annotations or effort estimates | Per implementation-planner SKILL.md §10 anti-pattern (risk/estimate annotations); the plan is for the executor; resourcing artifacts are separate and out of scope |
| PR / commit / file-granularity pre-commitment | Per SKILL.md §3.4 + §10 anti-pattern; stack-dependent; deferred to execution; plan commits to coherent-rollback at logical level only |
| Specification contract re-statement in plan | Per SKILL.md §2 (plan implements, does not extend spec); analog to PRD §[carry-forwards] translate-not-restate discipline; plan units cite spec contracts by ID + section, do not paraphrase contract content |
| Architecture extension or library introduction at plan layer | Per SKILL.md §4 sub-discipline 4 + §10 anti-pattern (spec extension); unit cannot introduce library/framework/protocol not named in spec; if extension feels necessary, back-flow to Phase 5 per §2 consequence 1 |
| Unit composition across multiple axes without spec-grade cross-axis contract | Per SKILL.md §7 cross-axis dependency-flag discipline; cross-axis units permissible but flagged; composition-only units require cross-axis composition contracts from `Specification_v1.md` §3–§7 |

---

## §2 Routing matrix

### 2.1 Arc routing shape

```
Phase 5 close (P5-CK Iteration 2 Final Revision Pass complete; 5 specs filed; iter-ceiling 2 of 2)
  │
  ▼
Phase 6 entry-gate AUTHORIZED (this handoff)
  │
  ├─ OD menu at session entry → C + A + A + A + A confirmed
  │
  ▼
Phase 6 entry session (current session — segmented delivery)
  │  ├─ Stage 1: Phase_6_Entry_Handoff.md (this artifact)
  │  ├─ Stage 2 collapsed under OD-6-1.C
  │  └─ Stage 3: Phase_6_Session_1_Session_Prompt.md (next segment)
  │
  ▼
Phase 6 Session 1: First-axis plan authoring (axis per §5.1 sequencing recommendation)
  │  ├─ implementation-planner SKILL.md activated (initial-authoring sub-mode)
  │  ├─ Specification (in-scope axis spec + composition document substrate seam exports) read at session entry
  │  ├─ Atomic-unit decomposition + dependency graph authored; coverage matrix populated for in-scope axis
  │  └─ Next-session session prompt authored at session close
  │
  ▼
Phase 6 Sessions 2–4: Per-axis plan authoring (remaining 3 axes per §5.1 sequencing)
  │  ├─ Each session inherits prior-session-filed plans as substrate
  │  ├─ Cross-axis dependencies flagged per SKILL.md §7 with `cross-axis: <Y>` annotation
  │  └─ Each session authors next session's session prompt at close
  │
  ▼
Phase 6 Session 5: Cross-axis composition plan (Implementation_Plan_v1.md top-level)
  │  ├─ Plan units derived from Specification_v1.md §3–§7 cross-axis composition contracts
  │  ├─ Aggregate dependency graph composed across all 5 documents
  │  ├─ Topological sort verified acyclic per Workflow §2.6 exit criterion
  │  └─ Pre-P6-CK coherence pass (full coverage matrix + dependency graph audit)
  │
  ▼
P6-CK entry-gate AUTHORIZED per Workflow §2.6.1
  │
  ▼
P6-CK adversarial review session (1 session per Workflow §2.6.1 Sessions field)
  │  ├─ harness-adversarial-reviewer SKILL.md activated (implementation plan review mode)
  │  ├─ Inputs: full implementation plan (per-axis plans + composition document)
  │  └─ Output: Adversarial_Review_6.md
  │
  ▼
P6-CK disposition routing:
  ├─ CLEARED → project transitions to build phase
  ├─ CONDITIONAL CLEARANCE → revision pass per Workflow §4.1.2 modified path
  └─ FAIL (Class 3 finding) → §4.1.3 phase re-open (Phase 5 spec revision OR Phase 4 PRD revision OR Phase 3d ADD revision)
```

### 2.2 Per-session session prompt authoring pattern

Each Phase 6 session authors the next session's session prompt at session close, following the Phase 5 per-session pattern. Session prompt scope per session:

- Which axis (or cross-axis composition) is in scope
- Which spec contracts are absorbed at the session (ID + section enumeration per `implementation-planner` SKILL.md §4.2 sub-discipline 2)
- Which substrate documents are read at session entry (axis spec primary; prior-axis plans + composition doc seam exports as inherited substrate)
- Coverage matrix delta scope (per-axis subset of full Phase 6 coverage matrix)
- Per-axis exit gate (atomic-unit decomposition complete; per-axis dependency graph acyclic; per-axis coverage complete)

---

## §3 Phase 6 inputs per Workflow §2.6

### 3.1 Primary input — Phase 5 specification (post-P5-CK-cleared)

Per `Project_Workflow_v1_5.md` §2.6 Inputs field. The cleared specification artifact set:

| Spec artifact | Path | Revision | Role at Phase 6 |
|---|---|---|---|
| `Spec_Information_Substrate_v1.md` | `/mnt/project/` | **v1.2** (P5-CK iter-2 revision pass close) | Canonical IS-axis contract source (C-IS-01 through C-IS-10) |
| `Spec_Action_Surface_v1.md` | `/mnt/project/` | **v1.1** (P5-CK iter-1 revision pass close; no v1.2 amendments) | Canonical AS-axis contract source (C-AS-01 through C-AS-16) |
| `Spec_Control_Plane_v1.md` | `/mnt/project/` | **v1.2** (P5-CK iter-2 revision pass close; §24.1 restructured into §24.1.A/B/C; C-CP-13 §13.3 D3 v1.2 bump) | Canonical CP-axis contract source (C-CP-01 through C-CP-24) |
| `Spec_Operational_Discipline_v1.md` | `/mnt/project/` | **v1.2** (P5-CK iter-2 revision pass close; 14 D3 v1.2 body-citation sites) | Canonical OD-axis contract source (C-OD-01 through C-OD-23) |
| `Specification_v1.md` | `/mnt/project/` | **v1.1** (P5-CK iter-1 revision pass close; no v1.2 amendments) | Cross-axis composition contract source (§1 top-level index + §2 citation matrices + §3 T-perm-1 + §4 T-perm-2 + §5 T-perm-3 + §6 cost-attribution + §7 bridging-arc + §8 traceability matrices) |

**Citation discipline.** Per implementation-planner SKILL.md §9 + Workflow §7 use-latest-version body-citation-alignment clause: plan units cite spec contracts at the **latest filed version**. Contracts in IS / CP / OD spec are cited at v1.2; AS spec and composition document at v1.1.

### 3.2 Secondary inputs — ADD, PRD, persona document

Per Workflow §2.6 Inputs field. Deeper substrate is consulted for cross-cutting context only; the specification is the canonical input for unit authoring per implementation-planner SKILL.md §2.

| Secondary input | Path | Revision | Role at Phase 6 |
|---|---|---|---|
| `Architectural_Design_Document_v1.md` | `/mnt/project/` | v1.2 (P3-CK cleared) | Architectural substrate; consulted for cross-axis composition reasoning per ADD §5.2 / §5.3 / §6 sections |
| `PRD_v1_0.md` | `/mnt/project/` | v1.0.1 (P5-CK iter-1 revision pass close; corrections to F-CP-* citation discipline) | Requirements substrate (R-IS-01 through R-IS-04 / R-AS-01 through R-AS-07 / R-CP-01 through R-CP-12 / R-OD-01 through R-OD-08); plan does NOT cite PRD directly per spec-to-plan-traceability discipline; PRD cited transitively through spec contracts |
| `Persona_Document_v1.md` | `/mnt/project/` | v1 | Persona anchor substrate; consulted for persona-tier discipline at units implementing monotonic-tier propagation (C-AS-12 / C-CP-19 / C-OD-13) |

### 3.3 Workflow authority

| Document | Role |
|---|---|
| `Project_Workflow_v1_5.md` | Workflow authority; §2.6 phase definition; §2.6.1 P6-CK definition; §4.1 finding-class disposition routing; §6.4 implementation-planner skill specification; §7 use-latest-version body-citation-alignment clause |
| `Project_Workflow_Revision_log.md` | Revision history (v1.5 entry consolidates Pattern P1+P2 PHASE-5 meta-resolution) |

### 3.4 Substrate retrieval discipline per session

Each Phase 6 session reads at session entry:

1. **In-scope axis spec** at section granularity for the contracts being decomposed at that session (e.g., Session 1 reads IS spec §1 through §10 for C-IS-01 through C-IS-10 decomposition)
2. **Composition document substrate seam exports** for the in-scope axis (e.g., IS spec §10 → composition doc §2 cross-axis citation matrices for IS substrate seam exports)
3. **Prior-session-filed plans** for cross-axis dependency declaration (`Depends on: [U-N (cross-axis: Y)]` per SKILL.md §7)
4. **ADD cross-axis composition sections** (§5.2 / §5.3) only when authoring units at composition seams
5. **Persona document** only when authoring units implementing persona-tier-monotonic disciplines

Substrate read is operationalized via `project_knowledge_search` against named sections — extending Phase 4/5 substrate-read posture.

---

## §4 Phase 6 expected output per Workflow §2.6 + OD-6-2.A

### 4.1 Per-axis multi-document plan structure

Per OD-6-2.A. Five deliverables produced across Phase 6 Sessions 1–5:

| # | Document | Authoring session | Scope |
|---|---|---|---|
| 1 | `Implementation_Plan_Information_Substrate_v1.md` | Session 1 (recommended; see §5.1) | Atomic units derived from C-IS-01 through C-IS-10; per-axis dependency graph |
| 2 | `Implementation_Plan_Action_Surface_v1.md` | Session 2 | Atomic units derived from C-AS-01 through C-AS-16; per-axis dependency graph |
| 3 | `Implementation_Plan_Control_Plane_v1.md` | Session 3 | Atomic units derived from C-CP-01 through C-CP-24; per-axis dependency graph |
| 4 | `Implementation_Plan_Operational_Discipline_v1.md` | Session 4 | Atomic units derived from C-OD-01 through C-OD-23; per-axis dependency graph |
| 5 | `Implementation_Plan_v1.md` | Session 5 | Cross-axis composition plan — units derived from `Specification_v1.md` §3 (T-perm-1) + §4 (T-perm-2) + §5 (T-perm-3) + §6 (cost-attribution cross-cutting) + §7 (bridging-arc cross-cutting); aggregate dependency graph composing all 5 documents; topological sort verification; aggregate coverage matrix |

### 4.2 Per-unit declaration shape

Per `Project_Workflow_v1_5.md` §2.6 Activity field + implementation-planner SKILL.md §3 + §4. Each plan unit declares:

| Field | Content | Source discipline |
|---|---|---|
| **Unit ID** | `U-<axis>-<seq>` (e.g., `U-IS-01`, `U-CP-23`) or `U-X-<seq>` for cross-axis units | Convention; sequential within axis |
| **Title** | Short imperative phrase naming the single coherent change | SKILL.md §3.1 |
| **Spec traceability** | `Implements: [C-IS-NN §N.N, C-AS-NN §N.N, ...]` — ≥1 spec contract by ID + section | SKILL.md §4 sub-discipline 2 |
| **Dependencies** | `Depends on: [U-N, U-M (cross-axis: Y), ...]` or `(none)` for foundational units | SKILL.md §7 |
| **Inputs** | Named inputs to the unit (substrate / signatures / schemas inherited from prior units) | Workflow §2.6 Activity field |
| **Files affected** | Logical file names (e.g., "the routing manifest schema definition file" — not filesystem paths) | SKILL.md §4 sub-discipline 4 |
| **Signatures** | Function / class / schema signatures introduced or modified (named at spec; planner names them, does not redesign) | SKILL.md §4 sub-discipline 4 |
| **Acceptance criteria** | Testable conditions for unit completion | Workflow §2.6 + SKILL.md §3.3 |
| **Tests** | Test specification — unit test names + behavioral assertion (NOT implementation) | Workflow §2.6 Activity field |
| **Rollback boundary** | Single coherent change reversible as one logical revert | SKILL.md §3.4 |

### 4.3 Plan-layer disciplines preserved at unit authoring

| Discipline | Source | Authoring application |
|---|---|---|
| Atomic-decomposition | SKILL.md §3 (four operational criteria: single coherent change + single focused session + independently testable + coherent rollback boundary) | Tested at each authored unit; under-decomposition (multi-axis buckets) or over-decomposition (one-line edits) trigger re-authoring |
| Spec-traceability | SKILL.md §4 sub-discipline 2 | Every unit cites ≥1 spec contract by ID + section; section-level citation mandatory; aggregate coverage of every spec contract by ≥1 unit verified at Session 5 close |
| Dependency-graph acyclic | SKILL.md §7 | Topological sort verified at each per-axis session close + final verification at Session 5 close per Workflow §2.6 exit criterion |
| No-spec-extension | SKILL.md §2 + §10 anti-pattern | Plan does not introduce libraries, frameworks, protocols not named in spec; gap surfaced as finding → back-flow to Phase 5 per Workflow §4 fork-handling |
| Implementation-grade-detail | SKILL.md §4 sub-discipline 4 | Each unit names files, signatures, acceptance — vagueness is a defect; back to re-author |
| Persona-tier monotonic-ascension preservation | ADR-F1 / D1 / D5 multiplicative tunable disciplines (cited in spec) | Units implementing C-AS-12 / C-CP-19 / C-OD-13 multiplicative-tunable contracts preserve monotonic-ascension at execution boundaries |
| Cross-axis composition seams | Specification_v1.md §3–§7 + Phase 5 axis-spec §[substrate-seam] declarations | Cross-axis units flagged per SKILL.md §7; composition seams cite axis-spec §[seam] sections explicitly |

---

## §5 Per-axis sequencing recommendation per OD-6-3.A topological-sort

### 5.1 Recommended axis sequencing

Per OD-6-3.A (dependency-graph topological sort) + OD-6-5.A (5-session sequence). The sequencing below is **recommended**; implementation-planner judgment at Session 1 entry may diverge based on per-axis substrate density.

| Session | Axis | Contracts in scope | Output | Rationale |
|---|---|---|---|---|
| 1 | **Information Substrate** | C-IS-01 through C-IS-10 (10 contracts) | `Implementation_Plan_Information_Substrate_v1.md` | Smallest axis surface (10 contracts vs 16/23/24 elsewhere); foundational tier — state-ledger entry shape (C-IS-05/06/07) + canonical paths (C-IS-01) + checkpoint/worktree opt-in (C-IS-08/09) + substrate-seam exports (C-IS-10) form the substrate every downstream axis composes against. Natural Session-1 warmup locking the substrate contract for the arc |
| 2 | **Action Surface** | C-AS-01 through C-AS-16 (16 contracts) | `Implementation_Plan_Action_Surface_v1.md` | Action-surface units consume IS substrate (audit composition C-AS-08 depends on C-IS-05/06; secret-fetch fail-class C-AS-07 ledger entries depend on C-IS-05/06). Sequenced after IS so AS units cite filed IS plan units for substrate-seam dependencies |
| 3 | **Control Plane** | C-CP-01 through C-CP-24 (24 contracts) | `Implementation_Plan_Control_Plane_v1.md` | Largest axis (24 contracts); heaviest cross-axis composition — HITL audit ledger (C-CP-16/C-CP-20) cites AS substrate seam exports; sub-agent privilege inheritance (C-CP-12) composes with AS sandbox-tier (C-AS-11); HandoffContext (C-CP-13) composes with IS state-ledger (C-IS-05). Sequenced after AS so CP units cite filed AS plan units for cross-axis seam dependencies |
| 4 | **Operational Discipline** | C-OD-01 through C-OD-23 (23 contracts) | `Implementation_Plan_Operational_Discipline_v1.md` | Telemetry-substrate composition — OD absorbs span attribute namespaces from all prior axes (C-OD-05 15 specialization-layer namespaces cite IS / AS / CP source contracts); OD plan units depend on all three prior axes' filed plans for namespace-source declarations. Sequenced LAST per-axis because composes against everything else |
| 5 | **Cross-axis composition** | `Specification_v1.md` §3 + §4 + §5 + §6 + §7 (5 composition contract sections) | `Implementation_Plan_v1.md` | Cross-axis emergent properties get dedicated session: T-perm-1 5-axis multiplicative tunable (§3) composes C-AS-12 + C-CP-19 + C-OD-13; T-perm-2 multi-seam (§4) composes C-IS-10 + C-AS-16 + C-CP-24 + C-OD-23 substrate seams; T-perm-3 three-layer engine substrate (§5) composes C-CP-07/C-CP-23; cost-attribution cross-cutting (§6) composes C-OD-14/15/16; bridging-arc cross-cutting (§7) composes C-OD-22 + per-axis bridging-invariant clauses. Aggregate dependency graph topological sort verified at this session close |

### 5.2 Within-axis topological-sort posture

Per implementation-planner SKILL.md §7. Each per-axis plan session orders units by acyclic dependency relation. Foundational-first ordering anchors the within-axis graph:

| Axis | Foundational units (`Depends on: (none)` or minimal) | Consumer units |
|---|---|---|
| Information Substrate | Canonical-path schema (C-IS-01); artifact-tier layering (C-IS-02); state-ledger entry shape (C-IS-05); hash-chain integrity discipline (C-IS-06) | Read/write contract pair (C-IS-07) depends on C-IS-05/06; substrate-seam exports (C-IS-10) depends on all prior IS contracts |
| Action Surface | Tier-set enumeration (C-AS-01); `sandbox.fail.class` taxonomy (C-AS-04); `SecretRef` signature (C-AS-05) | `max()` composition formula (C-AS-02) depends on C-AS-01; substrate seam exports (C-AS-16) depends on all prior AS contracts |
| Control Plane | Provider abstraction (C-CP-01); engine-class taxonomy (C-CP-07); topology taxonomy (C-CP-10); four-response palette (C-CP-16) | Cross-family fallback chain (C-CP-04) depends on C-CP-01; sub-agent privilege inheritance (C-CP-12) depends on C-CP-10/11 + C-AS-11 cross-axis; substrate seam exports (C-CP-24) depends on all prior CP contracts |
| Operational Discipline | 9-cell matrix (C-OD-01); span schema base layer (C-OD-04); breaker-trip event schema (C-OD-07) | 15 specialization-layer namespaces (C-OD-05) depends on C-OD-04 + cross-axis source contracts; substrate seam exports (C-OD-23) depends on all prior OD contracts |
| Cross-axis composition | T-perm-1/2/3 tunables (§3/§4/§5) compose per-axis tunable contracts | Cost-attribution (§6) and bridging-arc (§7) compose against composed tunables and substrate seams |

### 5.3 Sequencing divergence permissions

If Session 1 implementation-planner judgment surfaces unanticipated per-axis density (e.g., IS C-IS-05 hash-chain integrity decomposes into 8+ atomic units rather than expected 3–4), the axis sequencing may extend within the 5-session budget. Operator may also collapse Sessions 4–5 if OD plan density is low and cross-axis composition is compact. Implementation-planner surfaces session-count adjustment at session close per per-session-session-prompt-authoring discipline.

---

## §6 Skill build status per OD-6-1.C

### 6.1 Verification result

| Item | Status |
|---|---|
| `/mnt/skills/user/implementation-planner/SKILL.md` presence | ✅ **VERIFIED PRESENT** at session entry |
| Skill body conformance to session-prompt Stage 2 specification | ✅ Atomic-decomposition (§3) + spec-traceability (§4) + dependency-graph acyclic (§7) + implementation-grade-detail (§4.4) + no-spec-extension (§2) all encoded |
| Skill activation discipline | ✅ §1 Mode discipline declares initial-authoring sub-mode (Phase 6 entry; no prior plan filed) + revision-pass sub-mode (spec v1.x → v1.y or P6-CK absorption); third row "skill should not have activated; stand down" handles non-Phase-6 invocations |
| Skill V3 deference | ✅ §9 declares V3 owns confidence-tag schema + citation conventions + anti-fabrication; skill operates under Workflow §7 use-latest-version body-citation-alignment |
| Skill reference files declared | ✅ §11 declares 4 reference files: `references/implementation-plan-template.md` + `references/spec-to-plan-decomposition.md` + `references/dependency-graph-discipline.md` + `references/plan-authoring-protocol.md` |
| OD-6-1 resolution path | **C** — adopt existing; skip Stage 2 JIT build (A); skip multi-session build (B) |

### 6.2 Skill activation discipline at Phase 6 sessions

| Session | Skill activation | Sub-mode | Output target |
|---|---|---|---|
| This entry session | **spec-writer** (entry handoff + Session 1 session prompt) | n/a (canonical spec-writer mode for handoff/session-prompt artifacts) | `Phase_6_Entry_Handoff.md` + `Phase_6_Session_1_Session_Prompt.md` |
| Phase 6 Sessions 1–4 (per-axis plan authoring) | **implementation-planner** | Initial authoring | `Implementation_Plan_<Axis>_v1.md` per session |
| Phase 6 Session 5 (cross-axis composition) | **implementation-planner** | Initial authoring | `Implementation_Plan_v1.md` |
| P6-CK session | **harness-adversarial-reviewer** | Implementation plan review mode | `Adversarial_Review_6.md` |
| Revision-pass sessions (if any) | **implementation-planner** | Revision-pass | `Implementation_Plan_<Axis>_vN+1.md` per affected document |

---

## §7 Session count estimate per OD-6-5.A

### 7.1 Five-session sequence

| # | Session label | Skill | Primary deliverable | Workflow §2.6 conformance |
|---|---|---|---|---|
| 1 | First-axis plan authoring | implementation-planner | `Implementation_Plan_Information_Substrate_v1.md` (per §5.1 recommendation) | Within "2–4 sessions" §2.6 Sessions estimate as plan-authoring session #1 |
| 2 | Second-axis plan authoring | implementation-planner | `Implementation_Plan_Action_Surface_v1.md` | Plan-authoring session #2 |
| 3 | Third-axis plan authoring | implementation-planner | `Implementation_Plan_Control_Plane_v1.md` | Plan-authoring session #3 |
| 4 | Fourth-axis plan authoring | implementation-planner | `Implementation_Plan_Operational_Discipline_v1.md` | Plan-authoring session #4 — exceeds §2.6 nominal "2–4 sessions" by 1; rationale per §7.2 |
| 5 | Cross-axis composition + pre-P6-CK coherence pass | implementation-planner | `Implementation_Plan_v1.md` + coherence pass artifact (embedded in `Implementation_Plan_v1.md` §[coherence pass]) | Plan-authoring session #5 — exceeds §2.6 nominal estimate by 2; rationale per §7.2 |

### 7.2 Workflow §2.6 Sessions estimate divergence rationale

Workflow §2.6 Sessions field reads "2–4 sessions". The 5-session OD-6-5.A sequence exceeds nominal estimate by 1–3 sessions. Rationale:

- **Spec contract count.** 73 axis-spec contracts (10 IS + 16 AS + 24 CP + 23 OD) plus 5 cross-axis composition contract sections (§3–§7) exceed any volume implicit in the §2.6 estimate. The Workflow estimate was authored prior to Phase 5 specification authoring; actual spec density is observed.
- **Per-axis multi-document precedent.** OD-5-1.A established per-axis multi-document specification structure (Phase 5 ran 5 sessions for the same reason). Phase 6 OD-6-2.A inherits the per-axis pattern; matching per-axis session count.
- **Cross-axis composition session necessity.** `Specification_v1.md` §3–§7 cross-axis composition contracts require dedicated session for aggregate dependency graph composition + topological-sort verification + aggregate coverage matrix. Folding cross-axis composition into a per-axis session risks under-decomposition at composition seams.

Phase 6 sessions 4 + 5 are within OD-6-5.A scope, not workflow divergence requiring fork-handling. The Workflow §2.6 Sessions field is advisory; OD-6-5 governs.

### 7.3 Phase 5 5-session precedent reference

For continuity with operator expectation. Phase 5 session count:

| Phase 5 session | Output |
|---|---|
| 1 | `Spec_Information_Substrate_v1.md` v1 |
| 2 | `Spec_Action_Surface_v1.md` v1 |
| 3 | `Spec_Control_Plane_v1.md` v1 |
| 4 | `Spec_Operational_Discipline_v1.md` v1 |
| 5 | `Specification_v1.md` v1 (cross-axis composition) |

Phase 6 mirrors this sequencing at the plan layer; deliverable count and session count match.

---

## §8 P6-CK aggregation strategy per OD-6-4.A

### 8.1 Aggregate review scope

Per Workflow §2.6.1 + OD-6-4.A. One P6-CK invocation after all five plan documents file.

| Item | Value |
|---|---|
| P6-CK session count | 1 session per Workflow §2.6.1 Sessions field |
| P6-CK input | Full implementation plan: 4 per-axis plans + 1 cross-axis composition document |
| P6-CK skill | harness-adversarial-reviewer SKILL.md (implementation plan review mode) |
| P6-CK output | `Adversarial_Review_6.md` |
| P6-CK review surface | Dependency ordering correctness; hidden coupling between units; missing test coverage; spec contract coverage gaps; atomic-decomposition defects (under/over-decomposition); cross-axis dependency declaration completeness |

### 8.2 P6-CK entry-gate items

P6-CK entry-gate fires when all of the following hold:

| # | Check | Verification |
|---|---|---|
| 1 | All 5 plan documents filed | Per-axis plans (4) + composition document at `/mnt/project/` |
| 2 | Aggregate topological sort acyclic | Composition document §[topological sort] section emits acyclic ordering across all axis dependency graphs |
| 3 | Aggregate coverage matrix complete | Every spec contract (73 axis + 5 cross-axis composition) covered by ≥1 unit; composition document §[coverage matrix] enumerates |
| 4 | Every unit has explicit acceptance criteria | Per-unit declaration shape per §4.2 includes acceptance field; non-empty for every unit |
| 5 | Every unit has explicit test specification | Per-unit declaration shape includes tests field; non-empty for every unit |
| 6 | Pre-P6-CK coherence pass complete | Composition document §[coherence pass] returns ✅ PASS at all dimensions |

### 8.3 P6-CK disposition routing per Workflow §4.1

| Disposition | Routing path | Workflow reference |
|---|---|---|
| **CLEARED** — all Class 3 findings resolved; plan implementation-ready | Project transitions to **build phase**; Phase 6 closes; harness execution begins | Workflow §2.6.1 exit criteria |
| **CONDITIONAL CLEARANCE** — Class 2 findings present | Revision pass per Workflow §4.1.2 modified path; operator-authored revision with documented rationale; implementation-planner skill activates in revision-pass sub-mode per SKILL.md §8 | Workflow §4.1.2 |
| **FAIL** — Class 3 findings present | §4.1.3 phase re-open — three candidate paths: (a) Phase 5 spec revision (defect at contract level); (b) Phase 4 PRD revision (defect at requirement level); (c) Phase 3d ADD revision (defect at architectural level). Class 3 finding rationale dictates path | Workflow §4.1.3 |

P6-CK iteration ceiling: 2 standard iterations + §4.1.2 escalation path, matching P5-CK precedent.

---

## §9 Inputs traceability matrix — spec contracts → expected unit class

Per session-prompt Stage 1 enumerated item 7. The matrix below maps every Phase 5 specification contract to its **expected implementation plan unit class** at decomposition. Unit classes are derived from contract content shape; actual unit count per contract depends on per-contract atomic-decomposition granularity at the authoring session.

**Unit class taxonomy.** Eight classes encode the contract content shape:

| Class | Description |
|---|---|
| `data-type` | Schema definition, type signature, or enum |
| `api-surface` | Function signature, interface contract, or callable boundary |
| `algorithm` | Algorithm or discipline (e.g., hash-chain construction, fail-class taxonomy mapping) |
| `composition-formula` | Composition combinator over prior units (e.g., `max()` over inputs) |
| `provider-binding` | Provider or backend integration (e.g., observability backend cell binding) |
| `telemetry-schema` | Attribute namespace + emission paths |
| `policy-enforcement` | Policy function + integration sites (e.g., sampling, redaction) |
| `module-boundary` | Substrate seam export declaration + downstream consumer wiring |

### 9.1 Information Substrate axis (C-IS-01 through C-IS-10)

| Spec contract | Expected unit class(es) | Decomposition notes |
|---|---|---|
| **C-IS-01** Canonical filesystem path contract (§1) | `data-type` | Path schema definition + canonicalization helper |
| **C-IS-02** Artifact-tier layering schema (§2) | `data-type` | Three-tier layering definition + tier-membership predicate |
| **C-IS-03** Combined git tier role decomposition (§3) | `algorithm` + `module-boundary` | Tier-role decomposition logic + git-tier seam declaration |
| **C-IS-04** Atomic prompt + code + eval + manifest deploy contract (§4) | `api-surface` + `algorithm` | Deploy-contract API + atomic-deploy discipline |
| **C-IS-05** State-ledger entry shape signature (§5) | `data-type` | Six-field schema with field types + canonicalization library binding |
| **C-IS-06** Hash-chain integrity construction discipline (§6) | `algorithm` | Hash-chain construction logic + canonicalization-then-hash discipline + verification path |
| **C-IS-07** State-ledger read/write contract pair (§7) | `api-surface` + `algorithm` | Read/write API + T-perm-2 F2-layer resolution discipline |
| **C-IS-08** Workload-class-opt-in shadow-Git checkpoint contract (§8) | `policy-enforcement` + `api-surface` | Opt-in policy + checkpoint-cadence enforcement |
| **C-IS-09** Workload-class-opt-in worktree-isolation contract (§9) | `policy-enforcement` + `api-surface` | Opt-in policy + worktree-isolation read-coordination |
| **C-IS-10** Substrate seam exports surface (§10) | `module-boundary` | Cross-axis composition seam declarations (consumed by AS / CP / OD) |

**IS-axis dependency-graph anchor.** Foundational units: C-IS-01 (paths), C-IS-02 (layering), C-IS-05 (ledger entry), C-IS-06 (hash-chain). Consumer units: C-IS-07 depends on C-IS-05/06; C-IS-10 substrate seam depends on all prior IS contracts.

### 9.2 Action Surface axis (C-AS-01 through C-AS-16)

| Spec contract | Expected unit class(es) | Decomposition notes |
|---|---|---|
| **C-AS-01** Four-tier sandbox-isolation tier-set (§1) | `data-type` | Tier enum + tier-ordering relation |
| **C-AS-02** Per-tool sandbox tier `max()` composition formula (§2) | `composition-formula` | `max()` over minimum_tier × context floor × operator floor |
| **C-AS-03** Per-tool `minimum_tier` authoring-time declaration (§3) | `data-type` + `policy-enforcement` | Tool-manifest field schema + declaration-time enforcement |
| **C-AS-04** Sandbox-violation `sandbox.fail.class` taxonomy (§4) | `data-type` | Seven-value enum |
| **C-AS-05** `fetch_secret(name, scope) -> SecretRef` signature (§5) | `api-surface` + `data-type` | API signature + SecretRef shape |
| **C-AS-06** Per-tool `required_secrets` allowlist (§6) | `data-type` + `policy-enforcement` | Allowlist field + enforcement logic |
| **C-AS-07** Secret-fetch fail-class taxonomy (§7) | `data-type` | Five cause-attribution refinements enum |
| **C-AS-08** Secret-fetch structure-not-content audit composition (§8) | `algorithm` + `composition-formula` | `outputs_hash` formula composing IS C-IS-05/06 substrate |
| **C-AS-09** 12-cell deployment-surface × blast-radius-tier sandbox provider matrix (§9) | `provider-binding` | 12-cell provider matrix; per-cell binding |
| **C-AS-10** Per-MCP-transport sandbox-tier floor (§10) | `policy-enforcement` | Per-transport floor enforcement |
| **C-AS-11** Sub-agent sandbox-tier monotonic-ascension contract (§11) | `algorithm` + `policy-enforcement` | Monotonic-ascension discipline + enforcement at sub-agent dispatch |
| **C-AS-12** T-perm-1 D2-layer 5-axis multiplicative tunable (§12) | `composition-formula` + `policy-enforcement` | 5-axis multiplicative composition + cross-deployment monotonicity |
| **C-AS-13** Eleven-primitive Anthropic-adoption-depth matrix (§13) | `data-type` + `provider-binding` | 12-cell × 11-primitive adoption-depth matrix |
| **C-AS-14** Six Anthropic-primitive attribute namespace declarations (§14) | `telemetry-schema` | Six namespace declarations (consumed by OD C-OD-05) |
| **C-AS-15** Sandbox-bounded span schema (`sandbox.*` namespace) (§15) | `telemetry-schema` | `sandbox.*` namespace (consumed by OD C-OD-05) |
| **C-AS-16** Action Surface substrate seam exports surface (§16) | `module-boundary` | Cross-axis composition seam declarations (consumed by CP / OD) |

**AS-axis dependency-graph anchor.** Foundational units: C-AS-01 (tier-set), C-AS-04 (fail-class), C-AS-05 (SecretRef), C-AS-07 (secret-fetch fail-class). Cross-axis dependencies: C-AS-08 audit composition depends on IS C-IS-05/06 (`cross-axis: IS`). Consumer units: C-AS-02/11/12 depend on C-AS-01; C-AS-16 substrate seam depends on all prior AS contracts.

### 9.3 Control Plane axis (C-CP-01 through C-CP-24)

| Spec contract | Expected unit class(es) | Decomposition notes |
|---|---|---|
| **C-CP-01** Capability-aware multi-LLM provider abstraction (§1) | `api-surface` | F1 capability-introspection API surface |
| **C-CP-02** Layered cheapest-deterministic-first routing strategy (§2) | `algorithm` | Three-layer routing (declarative → embedding → LLM-as-router) |
| **C-CP-03** Per-layer time budget + deterministic-fallback-on-budget-exceeded (§3) | `policy-enforcement` + `algorithm` | Per-layer time budget + fallback discipline |
| **C-CP-04** Cross-family fallback chain composition (§4) | `composition-formula` | Fallback chain composition formula |
| **C-CP-05** F3 capability-floor lifecycle event surface (§5) | `data-type` + `telemetry-schema` | Eight event classes (consumed by OD C-OD-06) |
| **C-CP-06** Manifest-declaration invocation discipline + per-step opt-in override (§6) | `policy-enforcement` | Declaration-then-invoke discipline + override semantics |
| **C-CP-07** Five-element engine-class taxonomy + per-deployment-surface candidate mapping (§7) | `data-type` + `provider-binding` | Five-element enum + per-cell candidate mapping |
| **C-CP-08** Replay-resumption semantics per engine class (§8) | `algorithm` + `policy-enforcement` | Per-engine-class replay semantics; engine-class-visible granularity per [CF-1] |
| **C-CP-09** `engine.*` span attribute namespace declaration (§9) | `telemetry-schema` | `engine.*` namespace (consumed by OD C-OD-05) |
| **C-CP-10** Six-pattern multi-agent topology taxonomy (§10) | `data-type` | Six-pattern enum |
| **C-CP-11** Per-workload-class topology commitment + 2D matrix workload-class × engine-class (§11) | `policy-enforcement` + `provider-binding` | 2D matrix per workload-class × engine-class cell |
| **C-CP-12** Sub-agent privilege inheritance contract with monotonic-only descent (§12) | `algorithm` + `policy-enforcement` | Monotonic-descent discipline + enforcement at dispatch |
| **C-CP-13** HandoffContext + brief object structure (§13) | `data-type` + `api-surface` | HandoffContext schema + brief API |
| **C-CP-14** Multi-agent span hierarchy + concurrent-prompt-cache warm-up (§14) | `telemetry-schema` + `algorithm` | Span-hierarchy schema + warm-up algorithm |
| **C-CP-15** Cross-sibling audit-ledger discipline (§15) | `policy-enforcement` + `algorithm` | Cross-sibling ledger semantics |
| **C-CP-16** Four-response palette + audit ledger entry shape (§16) | `data-type` + `api-surface` | Four-response enum + ledger entry schema |
| **C-CP-17** Three-placement HITL topology primitive + interface signature (§17) | `api-surface` + `algorithm` | Three-placement primitive (allow/ask/deny) + interface |
| **C-CP-18** Synchrony-class × HITL-primitive-shape matrix per persona-tier × D1-engine-class (§18) | `data-type` + `policy-enforcement` | 4-dim matrix |
| **C-CP-19** T-perm-1 D5-layer multiplicative gate-level composition rule + cross-deployment monotonicity (§19) | `composition-formula` + `policy-enforcement` | D5-layer multiplicative composition; cross-deployment monotonicity |
| **C-CP-20** Per-persona-tier audit-ledger cryptographic shape + `audit.*` attribute namespace (§20) | `data-type` + `algorithm` + `telemetry-schema` | Per-tier crypto shape + `audit.*` namespace (consumed by OD C-OD-05) |
| **C-CP-21** Pre-HITL escalation order + `validator.fail.*` taxonomy (§21) | `algorithm` + `data-type` | Escalation order + fail-class taxonomy |
| **C-CP-22** Context revalidation on HITL resume (§22) | `algorithm` | Revalidation discipline |
| **C-CP-23** T-perm-3 multi-layer resolution composition (§23) | `composition-formula` | T-perm-3 composition over C-CP-07 + topology + engine substrate |
| **C-CP-24** Control Plane substrate seam exports surface (§24) | `module-boundary` | Cross-axis composition seam declarations; restructured into §24.1.A/B/C per F-iter2-01 resolution (consumed by OD C-OD-05 + composition document §2) |

**CP-axis dependency-graph anchor.** Foundational units: C-CP-01 (provider abstraction), C-CP-07 (engine-class), C-CP-10 (topology), C-CP-16 (response palette). Cross-axis dependencies: C-CP-12 depends on C-AS-11 (`cross-axis: AS`); C-CP-13 depends on C-IS-05 (`cross-axis: IS`); C-CP-16 audit ledger depends on C-IS-05/06 (`cross-axis: IS`). Consumer units: C-CP-19/23 multi-layer composition depend on prior CP contracts; C-CP-24 substrate seam depends on all prior CP contracts.

### 9.4 Operational Discipline axis (C-OD-01 through C-OD-23)

| Spec contract | Expected unit class(es) | Decomposition notes |
|---|---|---|
| **C-OD-01** 9-cell deployment-surface × persona-tier matrix (§1) | `data-type` | 9-cell matrix definition |
| **C-OD-02** Per-cell observability backend class commitment + provider candidate witness columns (§2) | `provider-binding` | Per-cell backend class + witness columns |
| **C-OD-03** Cell-selection contract — deferred candidate-within-class (§3) | `policy-enforcement` | Cell-selection discipline |
| **C-OD-04** Unified span schema base layer (OTel GenAI semconv 1.41.0) (§4) | `telemetry-schema` | OTel GenAI base layer schema |
| **C-OD-05** 15 specialization-layer namespace ingestion contract (§5) | `telemetry-schema` + `module-boundary` | 15 specialization-layer namespaces with cross-axis citation per CP §24 restructured 6+4+1 framing; ingestion discipline |
| **C-OD-06** F3 capability-floor (iv) lifecycle event-to-span-event mapping (§6) | `telemetry-schema` + `algorithm` | F3 lifecycle events (from CP C-CP-05) → span events mapping |
| **C-OD-07** `harness.breaker.*` seven-attribute breaker-trip event schema (§7) | `telemetry-schema` | Seven-attribute schema |
| **C-OD-08** Namespace collision discipline (§8) | `policy-enforcement` | Namespace collision resolution discipline |
| **C-OD-09** Sampling discipline: head-based-dev / tail-based-prod + always-sampled set (§9) | `policy-enforcement` + `algorithm` | Two-mode sampling + always-sampled exception set |
| **C-OD-10** Base-rate set + tail-keep-on-classification (§10) | `policy-enforcement` | Base-rate set + tail-keep discipline |
| **C-OD-11** Cardinality budget per cell + cardinality-safe-attribute discipline (§11) | `policy-enforcement` | Per-cell cardinality budget + discipline |
| **C-OD-12** Redaction discipline: default-off content + default-on structure (§12) | `policy-enforcement` | Redaction-discipline two-mode posture |
| **C-OD-13** Per-persona-tier content-capture override gradient + cross-deployment monotonic-tightening (§13) | `policy-enforcement` + `composition-formula` | Per-tier gradient + monotonic-tightening |
| **C-OD-14** Cost-attribution-per-span formula composing pricing + sandbox-tier + per-sibling rollup (§14) | `composition-formula` + `algorithm` | Three-input composition formula |
| **C-OD-15** Cross-family pricing differential + tokenization-version anchor (§15) | `data-type` + `algorithm` | Pricing schema + tokenization-anchor logic |
| **C-OD-16** Per-cell cost-attribution dashboard binding (§16) | `provider-binding` | Per-cell dashboard bindings |
| **C-OD-17** Five operator-burden eval primitives + separate-child-span eval emission (§17) | `algorithm` + `telemetry-schema` | Five primitives + eval emission discipline |
| **C-OD-18** Alignment-floor drift detection + eval-vs-runtime-gate distinction (§18) | `algorithm` + `policy-enforcement` | Drift-detection + distinction discipline |
| **C-OD-19** Local-first OTLP collector at solo-developer × local-development (§19) | `provider-binding` + `policy-enforcement` | Local-first collector configuration |
| **C-OD-20** Per-cell OTLP collector placement + F4 process-tier reachability (§20) | `provider-binding` | Per-cell collector placement |
| **C-OD-21** Multi-tenant tenant-isolation in observability surface (§21) | `policy-enforcement` | Tenant-isolation discipline |
| **C-OD-22** Bridging-arc traversal preservation across observability dimensions (§22) | `policy-enforcement` + `composition-formula` | Bridging-arc preservation across 8 in-scope transitions |
| **C-OD-23** Operational Discipline substrate seam exports surface (§23) | `module-boundary` | Cross-axis composition seam declarations (consumed by composition document §2) |

**OD-axis dependency-graph anchor.** Foundational units: C-OD-01 (9-cell matrix), C-OD-04 (span schema base), C-OD-07 (breaker schema). Cross-axis dependencies: C-OD-05 specialization-layer namespaces depend on AS C-AS-14/15 + CP C-CP-09/20 + IS C-IS-* (`cross-axis: AS, CP, IS` per restructured 6+4+1 framing); C-OD-06 depends on CP C-CP-05 (`cross-axis: CP`); C-OD-14 cost-attribution depends on AS C-AS-09 sandbox-tier (`cross-axis: AS`). Consumer units: C-OD-23 substrate seam depends on all prior OD contracts.

### 9.5 Cross-axis composition (Specification_v1.md §3–§7)

Cross-axis composition contracts authored at Phase 6 Session 5. Each section below maps to expected composition-unit class(es).

| Composition contract section | Expected unit class(es) | Decomposition notes |
|---|---|---|
| **§3** T-perm-1 resolution surface — 5-axis multiplicative gate-level tunable | `composition-formula` + `policy-enforcement` | Composes C-AS-12 (D2-layer) + C-CP-19 (D5-layer) + C-OD-13 (per-tier content-capture); 5-axis multiplicative composition with cross-deployment monotonicity invariant |
| **§4** T-perm-2 resolution surface — within-turn / across-turn seam at D6 OTLP collector boundary | `composition-formula` + `module-boundary` | Composes C-IS-10 + C-AS-16 + C-CP-24 + C-OD-23 substrate seam exports; D6 OTLP collector boundary as within-turn / across-turn split site |
| **§5** T-perm-3 resolution surface — three-layer engine substrate composition | `composition-formula` | Composes C-CP-07 (engine-class) + C-CP-23 (multi-layer composition) + C-CP-10 (topology) at engine-class × topology-pattern Cartesian product |
| **§6** Cost-attribution as cross-cutting architectural property | `composition-formula` + `policy-enforcement` | Composes C-OD-14/15/16 across per-axis cost-attribution sites; cross-cutting integration |
| **§7** Bridging-arc traversal preservation as cross-cutting architectural property | `policy-enforcement` + `composition-formula` | Composes C-OD-22 with per-axis bridging-invariant clauses across 8 in-scope transitions per IVR §5.1 |

**Cross-axis dependency-graph anchor.** All §3–§7 composition units depend on the corresponding per-axis contracts as cross-axis dependencies. Composition units have no foundational predecessors at the cross-axis layer; their dependencies are entirely external to the cross-axis composition document.

### 9.6 Aggregate coverage summary

| Axis | Spec contracts | Expected unit classes (instance count per contract varies) |
|---|---|---|
| Information Substrate | 10 | 10–15 units estimated |
| Action Surface | 16 | 18–24 units estimated |
| Control Plane | 24 | 28–36 units estimated |
| Operational Discipline | 23 | 26–34 units estimated |
| Cross-axis composition | 5 (§3–§7) | 8–12 units estimated |
| **Aggregate** | **78 contracts** | **90–121 units estimated** |

Estimate range based on per-contract atomic-decomposition granularity expectations. Actual unit count surfaced at per-session authoring; coverage discipline (every contract → ≥1 unit) verified at Session 5 close and re-verified at P6-CK.

---

## §10 Forward-flagged concerns from Phase 5 close

Three forward-flagged concerns carried into Phase 6 substrate per `P5-CK_Iteration_2_Revision_Pass_Close_Handoff.md` + session prompt §5.2.

### 10.1 [FF-1] Composition document framing-granularity drift (2-path vs 3-path)

| Dimension | Status |
|---|---|
| Origin | Per session prompt §5.2 Path A disposition. CP spec §24.1 restructured at iter-2 from 2-section / matrix-pair framing into §24.1.A (6 specialization-layer rows) + §24.1.B (4 F3-lifecycle-event-attribute rows) + §24.1.C (inheritance-composition note for `routing.*`) per F-iter2-01 Path A resolution. Composition document §2.6 retains coarser matrix-pair traversal at 2-path granularity |
| Current state | Forward-flagged at v1.2 CP spec close; not blocking Phase 6 entry. Composition document §2.6 is functionally correct at coarser granularity; CP §24.1 v1.2 three-composition-path structure is the authoritative source for OD C-OD-05 ingestion |
| Phase 6 disposition | Implementation-planner reads CP §24.1 v1.2 three-composition-path structure directly per session prompt §5.2 cross-stage discipline; composition doc §2.6 serves coarser-granularity matrix-pair traversal but is not the citation target at OD C-OD-05 unit authoring. Plan units citing the namespace ingestion structure cite CP §24.1.A / §24.1.B / §24.1.C explicitly |
| Forward routing | Closure expected at next Phase 5 revision pass (if triggered by P6-CK finding requiring composition document re-alignment); not iter-3-pending; operator-discretionary |

### 10.2 [FF-2] F-CP-01 attribute semantic-loss re-evaluation

| Dimension | Status |
|---|---|
| Origin | CP spec v1.1 Change-note §"Forward-flagged out-of-scope discoveries" enumerated F-CP-01 `breaker.cause` + `breaker.cooldown_ms` re-introduction as forward-flagged. Adjudicated as NOT-FINDING at iter-2 review §5.1 per OD-iter2-1.A independent judgment. Status at v1.2 close: REMAINS FORWARD-FLAGGED |
| Current state | Operator-discretionary; not iter-3-pending; not blocking Phase 6 entry. Closure not required for plan authoring |
| Phase 6 disposition | Plan units implementing C-OD-07 (`harness.breaker.*` seven-attribute schema) cite the v1.2 schema as authoritative; semantic-loss re-evaluation is a future revision pass concern, not a Phase 6 authoring concern |
| Forward routing | Closure at operator discretion; out-of-scope for current Phase 6 arc |

### 10.3 [FF-3] [CF-1] F2-12 D1 v1.1 → v1.2 replay-trace-emission contract

| Dimension | Status |
|---|---|
| Origin | ADD v1.2 §6.3.1 deferred-acknowledged; carried at PRD §[carry-forwards] [CF-1]; carried at Phase 5 §[carry-forwards]; impacts R-CP-07 contract precision |
| Current state | Deferred-acknowledged at Phase 5 close. C-CP-08 (Replay-resumption semantics per engine class) binds at engine-class-visible granularity only; per-event-class replay-emission contract carries forward |
| Phase 6 disposition | Plan units implementing C-CP-08 are authored at engine-class-visible granularity per spec contract; per-event-class replay-emission units are NOT authored at this Phase 6 arc (per [CF-1] disposition). If implementation surfaces a per-event-class need, surface as spec gap → back-flow to Phase 5 per implementation-planner SKILL.md §2 consequence 1 |
| Forward routing | Closure expected as D1 v1.1 → v1.2 + D6 v1.1 → v1.2 absorbed into ADD v1.3 → PRD revision pass → Phase 5 revision-pass at affected spec sections → Phase 6 revision-pass at affected plan units. Parallel `council-orchestrator` C7 + C9 session at operator discretion per ADD §6.3.1 |

---

## §11 Entry-gate verification

Six entry-gate criteria. Implementation-planner verifies all six at Phase 6 Session 1 open before authoring begins.

| # | Verification | Source of evidence |
|---|---|---|
| 1 | All 5 Phase 5 specification artifacts filed and P5-CK-cleared | IS spec v1.2 + AS spec v1.1 + CP spec v1.2 + OD spec v1.2 + composition doc v1.1 present at `/mnt/project/`; `P5-CK_Iteration_2_Revision_Pass_Close_Handoff.md` §10 closing footer |
| 2 | ADD v1.2 ratified and P3-CK-cleared | `Adversarial_Review_3_iter3.md` §7.1 disposition §4.1.1 CLEARANCE; ADD status block reads v1.2 |
| 3 | PRD v1.0.1 filed and P5-CK-iter-1-cleared | `PRD_v1_0.md` present at `/mnt/project/`; revision tag v1.0.1 reflects iter-1 corrections |
| 4 | `Persona_Document_v1.md` available | Present at `/mnt/project/` |
| 5 | F1–F5 + D1–D6 ADRs available | All 11 ADR files present at `/mnt/project/`; canonical commitment substrate consulted transitively via ADD/PRD/spec citation |
| 6 | `implementation-planner` SKILL.md available | Skill at `/mnt/skills/user/implementation-planner/SKILL.md`; activated in initial-authoring sub-mode at Session 1 per skill description |

If any precondition fails at Phase 6 Session 1 open, implementation-planner halts and surfaces the gap before authoring begins.

---

## §12 Exit criteria

Phase 6 exits at P6-CK clearance per Workflow §2.6.1. Two-stage exit:

### 12.1 Stage 1 — Phase 6 implementation plan authoring close

| Criterion | Verification |
|---|---|
| All 5 implementation plan documents filed | Per-axis plans (4) + composition document at `/mnt/user-data/outputs/` and moved to `/mnt/project/` |
| Topological sort of units is acyclic | Composition document §[topological sort] emits acyclic ordering across all axis dependency graphs per Workflow §2.6 exit criterion |
| Every specification contract covered by ≥1 unit | Composition document §[coverage matrix] enumerates 78 spec contracts → unit coverage (full-coverage discipline per implementation-planner SKILL.md §4 sub-discipline 2 aggregate) |
| Every unit has explicit acceptance criteria | Per-unit declaration shape per §4.2 acceptance field non-empty for every unit per Workflow §2.6 exit criterion |
| Every unit has explicit test specification | Per-unit declaration shape tests field non-empty for every unit |
| Pre-P6-CK coherence pass complete | Composition document §[coherence pass] returns ✅ PASS at all dimensions |
| Phase 6 §[carry-forwards] documented | [FF-1] composition framing-granularity drift + [FF-2] F-CP-01 attribute semantic-loss + [FF-3] F2-12 replay-trace-emission documented as carry-forwards into post-Phase-6 |

### 12.2 Stage 2 — P6-CK adversarial review clearance

Per Workflow §2.6.1:

| Criterion | Verification |
|---|---|
| `Adversarial_Review_6.md` filed | Output present at `/mnt/user-data/outputs/` and moved to `/mnt/project/` |
| All Class-3 findings resolved | Per Workflow §2.6.1 exit criteria; severe defects require plan revision pass at affected sections; iteration ceiling 2 + §4.1.2 escalation |
| Plan is implementation-ready | Per Workflow §2.6.1 exit criteria; coverage gaps, hidden coupling between units, missing test coverage all resolved |

P6-CK CLEARED → project transitions to build phase. Phase 6 closes; the design chain terminates per implementation-planner SKILL.md §2 consequence 2 ("Post-plan, only execution remains").

---

## §13 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_6_Entry_Handoff.md` |
| Status | Filed |
| Phase | 5 close → Phase 6 entry boundary |
| Routing target | (a) Phase 6 Session 1 (first-axis plan authoring per §5.1 recommendation: Information Substrate) → Sessions 2–4 (per-axis plan authoring) → Session 5 (cross-axis composition) → (b) P6-CK aggregate adversarial review per OD-6-4.A → (c) project close OR §4.1.2 escalation OR §4.1.3 phase re-open |
| Predecessor | `P5-CK_Iteration_2_Revision_Pass_Close_Handoff.md` (filed 2026-05-13) |
| Successor | `Phase_6_Session_1_Session_Prompt.md` (Stage 3 output; authored at Segment 2 of current session) |
| Filing destination | `/mnt/user-data/outputs/Phase_6_Entry_Handoff.md` |
| Date | 2026-05-14 |

---

*Filed 2026-05-14 at Phase 5 close → Phase 6 entry boundary. Phase 6 implementation plan authoring entry-gate AUTHORIZED per `P5-CK_Iteration_2_Revision_Pass_Close_Handoff.md` §10 closing footer with operator push of 5 revised artifacts to `/mnt/project/`. Defaults captured: OD-6-1.C (adopt existing implementation-planner skill) + OD-6-2.A (per-axis multi-document) + OD-6-3.A (topological sort) + OD-6-4.A (aggregate P6-CK) + OD-6-5.A (5-session sequence: 4 per-axis + 1 cross-axis composition). Arc shape: 5 plan-authoring sessions per Workflow §2.6 (exceeds nominal 2–4 estimate per §7.2 rationale) + 1 P6-CK session per §2.6.1. Exit target: full implementation plan filed; topological sort acyclic; every specification contract covered by ≥1 unit; every unit has explicit acceptance criteria; P6-CK CLEARED → project transitions to build phase.*

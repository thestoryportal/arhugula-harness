---
name: phase-7-back-flow-routing
description: Detect and route Phase 7 execution-time forks to design-phase channels per Project_Workflow_v1_8.md §2.7.6 + Phase_7_Kickoff_Prompt.md §6. Activates when an architectural defect surfaces at execution-time ("the spec contract under-specifies this surface", "the plan signature cannot be materialized", "I need to extend the CXA edge enumeration", "the ADR commitment is contradicted at implementation"), when a Class 1 fork is detected by any of the other Phase 7-specific skills, when the user references back-flow, fork classification, design-phase routing, halt-execution, or any defect-surfacing event. Always use this skill whenever the user mentions fork, halt, defect, routing target, design-phase channel, ADR revision, spec revision, plan revision, ADD revision, PRD revision, CXA revision, Workflow revision, X-AL-3 violation, silent absorption, or any architectural-artifact defect that requires re-issuing the design-phase artifact before Phase 7 execution can proceed. Triggers on words like "halt", "fork", "defect", "back-flow", "route to design-phase", "Class 1", "spec mismatch", "ADR violated", "silent absorption", "design extension surfaced", or any event where Phase 7 execution cannot proceed without design-phase artifact re-issue. This skill is the critical-failure-mode skill — silent absorption of design-phase defects contaminates downstream implementation and propagates to every dependent atomic unit.
---

# phase-7-back-flow-routing

Phase 7 fork detection + design-phase channel routing discipline. Active across ALL sub-phases (7a–7d). The critical-failure-mode skill: silent absorption of design-phase defects is the worst possible failure mode at Phase 7 execution.

## 1. Activation surface

### 1.1 Active across ALL sub-phases

This skill operates as a cross-cutting concern. It activates on **fork detection events**, not on sub-phase boundaries.

| Sub-phase | Activation trigger |
|---|---|
| 7a (bootstrap) | Any architectural defect surfacing during minimum-viable substitution scaffolding |
| 7b (per-axis-stream) | Halt conditions per `phase-7-implementation` skill §6 |
| 7c (cross-axis composition) | Halt conditions per `phase-7-cross-axis-composition` skill §7 |
| 7d (substitution retirement) | Halt conditions per `phase-7-substitution-retirement` skill §7 |

### 1.2 Cross-cutting relationship with other Phase 7-specific skills

| Sibling skill | Routes here when |
|---|---|
| `phase-7-implementation` | Halt conditions per its §6 |
| `phase-7-cross-axis-composition` | Halt conditions per its §7 |
| `phase-7-substitution-retirement` | Halt conditions per its §7 |

Operator-direct invocation of this skill bypasses sibling-skill triggering when fork is detected outside an atomic operation (e.g., operator notices ADR contradiction during review).

### 1.3 Critical-failure-mode classification

**Silent absorption of design-phase defects is the worst Phase 7 failure mode** per workspace root `CLAUDE.md` §4.3. Defect absorption at execution-time:

1.3.1 Contaminates downstream implementation against an invalid spec
1.3.2 Propagates the defect to every dependent atomic unit
1.3.3 Violates X-AL-3 (no silent H_T design extension)
1.3.4 Compromises the canonical authority chain (ADR → ADD → PRD → spec → plan → implementation)

This skill exists to ensure forks are surfaced explicitly, classified correctly, and routed to the appropriate design-phase channel for re-issue.

## 2. Fork class taxonomy

Per `Project_Workflow_v1_8.md` §2.6.5.3 + §2.7.6:

### 2.1 Class 1 — halt-execution

| Property | Value |
|---|---|
| Trigger | Architectural defect; design-phase artifact requires revision |
| Behavior | HALT Phase 7 sub-phase execution; cannot proceed until artifact re-issued |
| Routing | Applicable design-phase channel (see §3) |
| Operator surface | Required — operator authorizes back-flow + route |
| Recording | Sub-phase log + design-phase Canonical Substrate Inventory update |

### 2.2 Class 2 — in-execution operator decision

| Property | Value |
|---|---|
| Trigger | In-session decision-point requiring operator selection between substantive alternatives (NOT an architectural defect) |
| Behavior | PAUSE Phase 7 sub-phase execution; operator decision required; can proceed after decision |
| Routing | Operator decision in this workspace; record at sub-phase log |
| Operator surface | Required |
| Recording | Sub-phase log only (no design-phase artifact revision) |

### 2.3 Class 3 — informational

| Property | Value |
|---|---|
| Trigger | Observation requiring documentation; non-blocking |
| Behavior | CONTINUE Phase 7 sub-phase execution |
| Routing | Phase 7 execution log + `Canonical_Substrate_Inventory.md` update at design-phase workspace (deferred to session close) |
| Operator surface | Logged; surfaced at session close handoff |
| Recording | Session close handoff |

### 2.4 Class disambiguation

Distinguishing Class 1 from Class 2:

| Class 1 indicator | Class 2 indicator |
|---|---|
| Spec contract under-specifies a surface | Operator preference between substantive design alternatives that both satisfy the spec |
| Plan signature cannot be materialized at target stack | Operator decision between equivalent implementations (e.g., two acceptable library choices both within framework-pull discipline) |
| ADR commitment contradicted at execution-time | Operator decision on bounded-residual substitution classification |
| New H_T primitive surfaced (X-AL-3 violation) | Operator decision on edge-cardinality drift (e.g., CXA-OD-IS-EDGE-DRIFT 6 vs 4 disposition) |
| Cross-axis edge cardinality contradicts CXA v2.1 | Operator decision on session sequencing or cluster-traversal ordering |

When uncertain, default to Class 1 (more conservative; preserves design-phase authority chain).

## 3. Routing targets

Per `Project_Workflow_v1_8.md` §2.7.6:

### 3.1 Class 1 routing table

| Defect locus | Routing channel | Predecessor cleared at |
|---|---|---|
| Plan atomic unit (signature unimplementable; cross-unit dependency wrong; acceptance criterion incompatible) | Phase 6 plan revision-pass at design-phase workspace | P6-CK Iter 4 (Phase 6 close 2026-05-14) |
| Spec contract (under-specifies surface; spec inconsistent with ADR) | Phase 5 spec revision-pass | P5-CK Iter 2 |
| ADR (foundational F1–F5 or derivative D1–D6) anchor decision | Phase 3a/3b ADR revision via council convening | P3a-CK + P3-CK |
| ADD (Architectural Design Document) attestation mismatch | Phase 3d ADD revision | P3-CK Iter 3 |
| PRD (Product Requirements Document) observable-behavior gap | Phase 4 PRD revision | (P4 close) |
| CXA (Cross-Axis Composition Document) edge enumeration / cardinality / Pattern P1 | Phase 6 CXA revision-pass | (Phase 6 close) |
| Workflow governance defect | Workflow revision (path-delta amendment process) | `Project_Workflow_v1_8.md` |

### 3.2 Workspace ↔ design-phase workspace transitions

Per `Project_Workflow_v1_8.md` §2.7.2 workspace bidirectional discipline:

```
Phase 7 workspace (this workspace)
        │
        │ Class 1 fork detected
        ▼
Halt sub-phase execution
        │
        │ Surface to operator
        ▼
Operator routes to design-phase workspace
        │
        │ Open design-phase session at relevant phase channel
        ▼
Design-phase artifact revision (e.g., spec v1.x → v1.y)
        │
        │ Revision cleared (e.g., revision-pass complete)
        ▼
Design-phase artifact re-issued
        │
        │ Operator pushes re-issued artifact to design-phase /mnt/project/
        ▼
Phase 7 workspace re-loads artifact
        │
        │ Verify byte-exact integrity
        ▼
Resume Phase 7 sub-phase execution from halt point
        OR
Restart sub-phase if revised artifact invalidates prior progress
```

### 3.3 Workspace-local Class 2 routing

Class 2 forks route within this workspace:

```
Class 2 fork surfaced
        │
        │ Surface to operator
        ▼
Operator decision via ask_user_input_v0 or equivalent
        │
        │ Decision recorded at sub-phase log
        ▼
Resume Phase 7 sub-phase execution
```

No design-phase workspace transition required.

## 4. Per-event fork-handling shape

### 4.1 Step 1 — Classify the fork

Per §2.4 disambiguation:

| Step | Question |
|---|---|
| 1.a | Does this defect imply a design-phase artifact (ADR / ADD / PRD / spec / plan / CXA / Workflow) is incorrect or under-specified? → Class 1 |
| 1.b | Does this surface an in-session decision-point with substantive alternatives that both satisfy design intent? → Class 2 |
| 1.c | Is this an observation that documents an artifact state but does not block execution? → Class 3 |

### 4.2 Step 2 — Class 1: identify routing target

Per §3.1 routing table. Concretely:

| Defect category | Verification |
|---|---|
| Plan defect | Locate the affected per-axis plan version (IS v2.2 / AS v1 / CP v2.3 / OD v2.4) + the affected atomic unit |
| Spec defect | Locate the affected per-axis spec version (IS v1.2 / AS v1.1 / CP v1.3 / OD v1.3) + the affected contract |
| ADR defect | Locate the affected ADR (F1 v1.2 / F2 v1.2 / F3 v1.1 / F4 v1.1 / F5 v1.1 / D1 v1.2 / D2 v1.1 / D3 v1.2 / D4 v1.1 / D5 v1.3 / D6 v1.2) + the contradicted decision |
| ADD defect | ADD v1.3 — locate attestation row |
| PRD defect | PRD v1.1 — locate observable-behavior row |
| CXA defect | CXA v2.1 — locate the §2.3.X bucket + edge declaration |
| Workflow defect | `Project_Workflow_v1_8.md` — locate the affected workflow section |

### 4.3 Step 3 — Halt sub-phase execution

Halt at the current atomic unit / seam-instantiation step / retirement event. Do NOT proceed past the halt point. Capture halted state:

| State element | Capture |
|---|---|
| Halt point | Specific atomic unit ID / CXA edge / substitution ID |
| Halt timestamp | Session + segment reference |
| Halt rationale | Defect description + cited canonical artifact location |
| Routing target | Per §3.1 |

### 4.4 Step 4 — Surface to operator

Operator-surface format:

```
CLASS 1 FORK DETECTED — HALT PHASE 7 SUB-PHASE EXECUTION

Defect locus: [artifact + version + section/unit ID]
Defect description: [concise statement]
Routing target: [design-phase channel per §3.1]
Halt point: [atomic unit / edge / substitution]
Resumption requires: [design-phase artifact re-issue + workspace re-load]

Operator decision required:
  (A) Authorize route to [routing target]; halt Phase 7 until re-clearance
  (B) Re-classify as Class 2 (operator decision between alternatives)
  (C) Re-classify as Class 3 (informational; non-blocking)
```

### 4.5 Step 5 — Wait for re-issued artifact

After operator authorizes route, this workspace HALTS until:

1. Design-phase session opens at routing target's phase
2. Design-phase artifact revision-pass completes (e.g., spec v1.2 → v1.3)
3. Revised artifact re-cleared at applicable checkpoint (e.g., P5-CK for spec revisions, P6-CK for plan revisions)
4. Operator pushes re-issued artifact to design-phase `/mnt/project/`
5. Re-issued artifact loaded into this workspace

### 4.6 Step 6 — Verify byte-exact integrity of re-issued artifact

Per workspace root `CLAUDE.md` §8 invariant I-1: canonical artifact citations resolve byte-exact per Workflow v1.8 §7.4.2. Verify:

| Verification | Action |
|---|---|
| Version bump applied | Re-issued artifact at v1.y (where y > x of halted version) |
| Defect resolved | Defect locus addressed at re-issued artifact |
| Downstream coverage | Dependent artifacts (e.g., plan if spec revised) reflect re-issued artifact's content |
| Cross-axis coverage | If CXA-affected, CXA v2.x reflects re-issued artifact's content |

### 4.7 Step 7 — Resume or restart

| Condition | Action |
|---|---|
| Re-issued artifact preserves halted progress (e.g., the unit's substrate is now sufficient) | Resume from halt point; verify acceptance criteria against re-issued artifact |
| Re-issued artifact invalidates halted progress (e.g., unit signature changed substantively) | Restart unit; re-run §3.1–§3.6 of `phase-7-implementation` against re-issued artifact |
| Re-issued artifact reshapes cluster boundaries | Restart cluster; re-run cluster traversal per Meta-Architecture §10.2.4 |

## 5. Anti-leakage discipline

### 5.1 X-AL-3 binding (Meta-Architecture §7.7)

> **X-AL-3.** **No silent H_T design extension at Phase 7 execution.** New H_T primitives surfaced at execution-time route to design-phase back-flow (Class 1) before implementation proceeds.

X-AL-3 is the canonical anti-leakage rule for this skill. Any new H_T primitive surfaced at execution-time:

5.1.1 IS a Class 1 fork
5.1.2 MUST halt sub-phase execution
5.1.3 MUST route to design-phase ADR back-flow (or spec/plan if the primitive shape exists at ADR but is under-specified at downstream artifact)
5.1.4 MUST NOT be silently implemented

### 5.2 Cross-cutting rules at fork detection

| Rule | Application |
|---|---|
| X-AL-1 | Forks involving cross-substrate boundary (e.g., MCP server boundary) require explicit boundary preservation at re-issued artifact |
| X-AL-2 | Forks involving substitution retirement require retirement criterion preservation at re-issued artifact (cited unit IDs may need re-anchoring) |

### 5.3 Class 3 informational discipline

Class 3 forks are NOT silent absorption. They are documented at sub-phase log + Canonical Substrate Inventory update at design-phase workspace. Examples of legitimate Class 3 forks:

| Class 3 example | Recording |
|---|---|
| CXA-OD-IS-EDGE-DRIFT (CXA v2.1 §2.3.5 6 edges vs OD plan v2.4 §4.5.1 4 edges) | Already documented at IS plan v2.2 §0.9 + OD plan v2.4 §0.9 |
| Cluster name citation imprecise (cluster-N vs Cluster N proper-noun grammar) | Sub-phase log; defer to next session formatting review |
| Citation section-name-only (per Workflow v1.8 §7.4.4 citation-only grammar) where absolute section number unavailable | Sub-phase log; canonical-substrate authority preserved at section-name citation |

Class 3 ≠ Class 1 → Class 3 demotion of an actual defect IS silent absorption. Disambiguate carefully per §2.4.

## 6. Common fork scenarios

### 6.1 Spec under-specification surfaces during unit implementation

Example: `phase-7-implementation` at Step 5 finds the cited spec contract section does not specify a required signature element.

| Step | Action |
|---|---|
| Classify | Class 1 (spec contract under-specifies surface) |
| Route | Phase 5 spec revision-pass |
| Halt | At unit implementation |
| Re-issue | Spec v1.x → v1.y at design-phase workspace |
| Resume | Re-run unit implementation against re-issued spec |

### 6.2 Plan signature unimplementable at target stack

Example: `phase-7-implementation` at Step 5 finds the plan's signature requires a primitive not available in Python 3.12+ + Pydantic v2 + asyncio + uv stack.

| Step | Action |
|---|---|
| Classify | Class 1 (plan signature unimplementable) |
| Route | Phase 6 plan revision-pass |
| Halt | At unit implementation |
| Re-issue | Plan v2.x → v2.y at design-phase workspace |
| Resume | Re-run unit implementation against re-issued plan |

### 6.3 ADR contradicted at implementation

Example: `phase-7-implementation` at Step 5 finds the implementation that satisfies the plan signature contradicts the parent ADR commitment.

| Step | Action |
|---|---|
| Classify | Class 1 (ADR commitment contradicted at execution-time) |
| Route | Phase 3a/3b ADR revision via council convening |
| Halt | At unit implementation |
| Re-issue | ADR v1.x → v1.y at design-phase workspace; ADD v1.3 → v1.4 if attestation affected |
| Cascade | Spec v1.x → v1.y; Plan v2.x → v2.y if downstream affected |
| Resume | Re-run unit implementation against re-issued ADR + ADD + spec + plan |

### 6.4 New H_T primitive surfaced

Example: Operator notices that implementing U-CP-22 requires a new H_T primitive not present at CP spec v1.3.

| Step | Action |
|---|---|
| Classify | Class 1 — X-AL-3 violation (new H_T primitive); DO NOT silently extend |
| Route | Phase 3a/3b ADR (new primitive requires anchor decision) |
| Halt | At unit implementation; sub-phase paused |
| Re-issue | New ADR (or extension to existing ADR); cascade to ADD + PRD + spec + plan |
| Resume | Re-run sub-phase against expanded design |

### 6.5 CXA edge cardinality contradicts consumer-side plan

Example: `phase-7-cross-axis-composition` at §4.4 finds CXA v2.1 §2.3.X bucket cardinality contradicts consumer-side plan declaration.

| Step | Action |
|---|---|
| Classify | Class 1 — CXA defect OR consumer-side plan defect (operator decision on locus) |
| Route | Phase 6 CXA revision OR consumer-side plan revision |
| Halt | At seam instantiation |
| Re-issue | CXA v2.x → v2.y OR plan v2.x → v2.y at design-phase workspace |
| Resume | Re-run seam instantiation against re-issued artifact |

### 6.6 Substitution retirement criterion partial satisfaction

Example: `phase-7-substitution-retirement` at Step 6 finds condition (A) met but condition (B) not met.

| Step | Action |
|---|---|
| Classify | Class 1 — X-AL-2 violation if recorded without both conditions |
| Route | Code review at substitution site; locate residual invocation; halt until removed |
| Halt | At retirement event |
| Resolution | Remove residual H_E surface invocation at substitution site; verify condition (B); record retirement |

## 7. Reference artifacts

| Reference | Location | Authority |
|---|---|---|
| `Project_Workflow_v1_8.md` §2.7.6 | Design-phase workspace | Back-flow routing canonical |
| `Project_Workflow_v1_8.md` §2.6.5.3 | Design-phase workspace | In-project fork management |
| `Phase_7_Kickoff_Prompt.md` §6 | Design-phase workspace | Phase 7 back-flow discipline reference |
| `Phase_7_Meta_Architecture_v1.md` §10.5.3 | Design-phase workspace | Back-flow routing aggregate |
| `Phase_7_Meta_Architecture_v1.md` §7.7 | Design-phase workspace | X-AL-1 / X-AL-2 / X-AL-3 cross-cutting anti-leakage |
| Workspace root `CLAUDE.md` §4.3 | This workspace | Back-flow routing summary + critical-failure-mode classification |
| Per-axis `CLAUDE.md` §5 | This workspace | Per-axis Class 1 routing table |
| `Sub_Agent_Boundary_Specification_v1.md` §7.3 | This workspace | Sub-agent back-flow routing |
| `Canonical_Substrate_Inventory.md` | Design-phase workspace | Updated at session close to reflect Class 3 informational items |

---

*End of `phase-7-back-flow-routing` skill. Active across ALL Phase 7 sub-phases. Critical-failure-mode skill: silent absorption of design-phase defects is the worst Phase 7 failure mode.*

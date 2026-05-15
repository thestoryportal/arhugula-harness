# Phase 6.5 Session 6 Kickoff — Claude Code CLI Bootstrap Substrate (ε)

*Session entry artifact for Phase 6.5 Session 6. Loaded as substrate at session open. Authored at Session 5 (γ) close; executed in a new session in this same project workspace.*

---

## §1 Session identity

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_6_Kickoff.md` |
| Phase | Phase 6.5 (pre-transition arc) |
| Session number | 6 of 7 |
| Session designator | ε |
| Session name | Claude Code CLI Bootstrap Substrate |
| Skill activation | `systems-architect` SKILL.md (Phase 7 substrate authoring; analog to Phase 3d ADD consolidation discipline) + `skill-creator` SKILL.md (for Phase 7-specific skills); `spec-writer` SKILL.md at Segment close for canonicalization |
| Authoring authority | Operator directive 2026-05-14 (Phase 6.5 arc entry); `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 Session 6 enumeration; `Project_Workflow_v1_8.md` §2.6.5.4 criterion 6 |
| Predecessor artifact | `Phase_6_5_Session_5_Close_Handoff.md` (Session 5 γ close); `Project_Workflow_v1_8.md` (Session 5 γ primary deliverable — canonical workflow at v1.8) |
| Companion artifact (canonical for entire arc) | `Phase_6_5_Pre_Transition_Arc_Manifest.md`; `Canonical_Substrate_Inventory.md` |
| Successor artifact (at session close) | Claude Code CLI bootstrap substrate (root + per-axis `CLAUDE.md`; custom skills; sub-agent boundary specification); `Phase_6_5_Session_6_Close_Handoff.md`; `Phase_6_5_Session_7_Kickoff.md` |

---

## §2 Session scope

### §2.1 In scope

Author the concrete Claude Code CLI substrate the new workspace receives at Phase 7 entry. Per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 Session 6 + Workflow v1.8 §2.6.5.4 criterion 6:

#### §2.1.1 Root `CLAUDE.md`

Workspace-level guidance authored against the Phase 7 execution discipline. Authoring scope:

| Sub-section | Content |
|---|---|
| Project framing | H_T (target harness per v2.3 plans) built in H_E (Claude Code CLI) per `Phase_7_Meta_Architecture_v1.md` §1 chicken-and-egg paradox resolution; ADR + ADD + specs + plans canonical authority |
| Canonical artifact pointers | Per-axis spec / plan / CXA v2.1 / ADD v1.3 / PRD v1.1 / canonical ADRs pointers + `Project_Workflow_v1_8.md` §2.7 execution discipline reference + `Phase_7_Meta_Architecture_v1.md` substitution discipline reference + `Target_Stack_Commitment_v1.md` stack reference |
| Stack discipline | Python 3.12+ + Pydantic v2 + asyncio + uv workspace per `Target_Stack_Commitment_v1.md`; framework-pull discipline per `Plan_Executability_Audit_v1.md` |
| Substitution discipline reference | `Phase_7_Meta_Architecture_v1.md` §5 substitution mapping table + §7 anti-leakage rules; canonical at design-phase workspace |
| Back-flow routing | Phase 7 execution-time forks route to design-phase workspace per `Project_Workflow_v1_8.md` §2.7.6 + `Phase_7_Kickoff_Prompt.md` §6 |
| Sub-agent boundary | Claude Code sub-agent topology is H_E only; NOT H_T CP-axis topology per anti-leakage rule CP-AL-1 |

#### §2.1.2 Per-axis `CLAUDE.md` (4 files: IS / AS / CP / OD)

Per-axis subdirectory `CLAUDE.md` files anchoring axis-specific guidance. Authoring scope per axis:

| Sub-section | Content |
|---|---|
| Axis scope | Per-axis spec content boundary (e.g., IS = ledger + index + cache; AS = tool contracts + MCP integration; CP = topology + retry + breaker + workflow lifecycle; OD = HITL + ledger schema + cost attribution + observability) |
| Per-axis canonical artifacts | Axis spec + axis plan + CXA v2.1 axis edge inventory; per-axis ADR pointers (F-axis + D-axis decisions) |
| Per-axis dependency-graph entry-points | Topological level 0 units per axis plan (foundational primitives); cluster sequencing per axis plan |
| Per-axis substitution surface | Per-axis subset of `Phase_7_Meta_Architecture_v1.md` §5 substitution mapping table (IS=9 / AS=6 / CP=21 / OD=8 entries) + axis-specific anti-leakage rules per §7 |
| Per-axis back-flow channels | Axis-specific revision-pass routing if Phase 7 surfaces axis-specific design defect |

#### §2.1.3 Custom skills authoring

Phase 7-specific skills authored at this session per `skill-creator` SKILL.md discipline. Skills authored at ε land in the Claude Code CLI workspace, not this design-phase workspace.

Candidate skill scope (operator decision at session entry):

| Skill candidate | Purpose | Authoring scope at ε |
|---|---|---|
| `phase-7-implementation` | Phase 7 execution discipline at unit-level (per-axis plan unit consumption + acceptance-criteria-driven implementation + cross-unit dependency-graph traversal) | Phase 7-specific; consumes v2.2 / v1 / v2.3 / v2.4 plans as canonical |
| `phase-7-cross-axis-composition` | Phase 7 sub-phase 7c execution discipline (CXA v2.1 composition seam instantiation) | Phase 7-specific; consumes CXA v2.1 as canonical |
| `phase-7-substitution-retirement` | Phase 7 sub-phase 7d execution discipline (per-primitive substitution retirement against `Phase_7_Meta_Architecture_v1.md` §6 gradient) | Phase 7-specific; consumes substitution mapping table + self-hosting milestone gradient |
| `phase-7-back-flow-routing` | Phase 7 execution-time fork detection + design-phase channel routing | Phase 7-specific; consumes Workflow v1.8 §2.7.6 + Phase 7 Kickoff §6 |

Operator decision at Segment 1 entry: which subset of candidate skills to author at ε vs defer to Phase 7 execution-time skill-creation surfaces.

#### §2.1.4 Sub-agent boundary specification

Claude Code sub-agent topology specification per H_E capability surface. Authoring scope:

| Element | Specification |
|---|---|
| Sub-agent count + scope | Operator-discretion at session execution; bounded by Claude Code documented sub-agent surface |
| Per-sub-agent responsibility | Phase 7 sub-phase 7b axis-stream parallelism candidates (per OD-S4-S4-14 from Session 4 close §7.4 Class 3 C3-S4-14 scheduling recommendation) |
| Anti-leakage discipline | Claude Code sub-agent topology is H_E only; NOT H_T CP-axis topology per anti-leakage rule CP-AL-1; explicit citation at sub-agent boundary specification |

### §2.2 Out of scope

- IS / AS / CP / OD plan revisions (preserved at v2.2 / v1 / v2.3 / v2.4 canonical revisions)
- ADR / ADD / PRD revisions (cleared at Phase 6 close)
- Spec revisions (preserved at canonical Phase 5 revisions)
- Meta-architecture revisions (`Phase_7_Meta_Architecture_v1.md` filed at Session 4 close; revision scope out-of-session)
- Workflow revisions (`Project_Workflow_v1_8.md` filed at Session 5 close; revision scope out-of-session)
- Phase 7 Session 1 Entry Directive authoring (Session 7 β owns)
- Implementation in any form (no H_T code authored at this session — ε authors H_E-workspace bootstrap substrate only)
- Stack revisions (`Target_Stack_Commitment_v1.md` preserved per Session 1 close)
- H_T design extension (canonical at Phase 6 / Phase 5 / Phase 3 artifacts; no extension at ε)

If authoring surfaces a question about any of these, route per §6 fork-handling.

### §2.3 Deliverables

Variable artifact count at session close depending on skill scope decision at Segment 1:

**Minimum scope (root + per-axis CLAUDE.md + sub-agent boundary only):**

| # | Artifact | Role |
|---|---|---|
| 1 | `CLAUDE.md` (root) | Workspace-level guidance for Claude Code CLI workspace |
| 2 | `harness-is/CLAUDE.md` | IS-axis subdirectory guidance |
| 3 | `harness-as/CLAUDE.md` | AS-axis subdirectory guidance |
| 4 | `harness-cp/CLAUDE.md` | CP-axis subdirectory guidance |
| 5 | `harness-od/CLAUDE.md` | OD-axis subdirectory guidance |
| 6 | `Sub_Agent_Boundary_Specification_v1.md` | Sub-agent boundary specification |
| 7 | `Phase_6_5_Session_6_Close_Handoff.md` | Session close handoff |
| 8 | `Phase_6_5_Session_7_Kickoff.md` | Session 7 (β — Phase 7 Session 1 Entry Directive) entry artifact |

**Extended scope (minimum + 1–4 Phase 7-specific skills):**

Each Phase 7-specific skill adds one `SKILL.md` artifact + per-skill supporting files. Skill scope per operator decision at Segment 1 entry.

---

## §3 Substrate retrieval

### §3.1 Canonical Phase 6.5 substrate (load first)

| # | Artifact | Path | Role |
|---|---|---|---|
| 1 | `Phase_6_5_Pre_Transition_Arc_Manifest.md` | `/mnt/project/` | Arc framing + sequence context + fork-handling discipline |
| 2 | `Canonical_Substrate_Inventory.md` | `/mnt/project/` | KB navigation anchor; disambiguates canonical vs superseded artifacts |
| 3 | `Phase_6_5_Session_5_Close_Handoff.md` | `/mnt/project/` (after operator push) | Session 5 close record; canonical-substrate carry-forward |
| 4 | `Project_Workflow_v1_8.md` | `/mnt/project/` (after operator push) | Session 5 primary deliverable; canonical workflow at v1.8 with §2.6.5 + §2.7 + §4.1.4.6 specifications |
| 5 | `Phase_7_Meta_Architecture_v1.md` | `/mnt/project/` | Session 4 primary deliverable; canonical Phase 7 execution discipline + substitution mapping + anti-leakage rules |
| 6 | `Phase_7_Kickoff_Prompt.md` | `/mnt/project/` | Portable kickoff; referenced at root `CLAUDE.md` |

### §3.2 Stack + plan substrate

| Artifact | Role |
|---|---|
| `Target_Stack_Commitment_v1.md` | Canonical stack commitment; referenced at root `CLAUDE.md` stack discipline section |
| `Plan_Executability_Audit_v1.md` | Plan executability validation; referenced at root `CLAUDE.md` framework-pull discipline |
| `Implementation_Plan_Information_Substrate_v2_2.md` | IS plan canonical; referenced at `harness-is/CLAUDE.md` |
| `Implementation_Plan_Action_Surface_v1.md` | AS plan canonical; referenced at `harness-as/CLAUDE.md` |
| `Implementation_Plan_Control_Plane_v2_3.md` | CP plan canonical; referenced at `harness-cp/CLAUDE.md` |
| `Implementation_Plan_Operational_Discipline_v2_4.md` | OD plan canonical; referenced at `harness-od/CLAUDE.md` |
| `Cross_Axis_Composition_Document_v2_1.md` | CXA v2.1 canonical; referenced across per-axis `CLAUDE.md` for cross-axis edges |

### §3.3 Spec + ADR + ADD + PRD substrate (referenced from per-axis `CLAUDE.md`)

Per `Phase_7_Meta_Architecture_v1.md` §0 status block predecessor enumeration:

- IS spec v1.2 / AS spec v1.1 / CP spec v1.3 / OD spec v1.3 — per-axis spec canonical
- ADR-F1 v1.2 / ADR-F2 v1.2 / ADR-F3 v1.1 / ADR-F4 v1.1 / ADR-F5 v1.1 — foundational ADR canonical
- ADR-D1 v1.2 / ADR-D2 v1.1 / ADR-D3 v1.2 / ADR-D4 v1.1 / ADR-D5 v1.3 / ADR-D6 v1.2 — derivative ADR canonical
- ADD v1.3 — Architectural Design Document canonical
- PRD v1.1 — Product Requirements Document canonical

Per-axis `CLAUDE.md` artifacts cite relevant subsets; full enumeration at root `CLAUDE.md`.

### §3.4 V3 system prompt

Loaded at workspace level. Confidence tagging + source-grounding + anti-fabrication discipline apply. Particularly relevant at root + per-axis `CLAUDE.md` authoring: bootstrap substrate citations to canonical artifacts must resolve byte-exact.

### §3.5 Skill activation

| Skill | Sub-mode | Trigger |
|---|---|---|
| `systems-architect` | Phase 7 bootstrap substrate authoring (analog to Phase 3d ADD consolidation discipline) | Root + per-axis `CLAUDE.md` authoring + sub-agent boundary specification |
| `skill-creator` | Phase 7-specific skill authoring | Custom skill authoring per §2.1.3 candidate skill scope |
| `spec-writer` | Canonicalization at Segment close | Final artifact composition; cross-section traceability verification |

---

## §4 Entry-gate verification

At session open, verify:

| # | Check | Verification |
|---|---|---|
| 1 | Phase 6.5 manifest accessible | `project_knowledge_search` returns content |
| 2 | `Phase_6_5_Session_5_Close_Handoff.md` accessible at `/mnt/project/` | `project_knowledge_search` returns content; operator pushed between sessions |
| 3 | `Project_Workflow_v1_8.md` accessible at `/mnt/project/` | Same |
| 4 | `Phase_7_Meta_Architecture_v1.md` accessible | Same |
| 5 | `Target_Stack_Commitment_v1.md` accessible | Same |
| 6 | `Plan_Executability_Audit_v1.md` accessible | Same |
| 7 | All v2.2 / v1 / v2.3 / v2.4 plans + CXA v2.1 accessible | Same |
| 8 | All canonical specs + ADRs + ADD v1.3 + PRD v1.1 accessible | Same |
| 9 | No open Class 1 / Class 2 forks from Session 5 (γ) | Per `Phase_6_5_Session_5_Close_Handoff.md` §5.4 (no Class 1; §4.1.4.7 placement Class 2 sub-decision dispositioned OD-γ-3 within session; H_T-CP-1 carry-forward preserved at Workflow v1.8 §2.6.5.7 + §2.7.7) |

If any entry-gate item fails, halt session open; surface to operator before proceeding.

---

## §5 Session execution discipline

### §5.1 Segmented delivery contract

4–6 segments estimated per bootstrap substrate scope:

| Segment | Scope | Approximate output |
|---|---|---|
| 1 | Substrate read + skill-scope operator decision + root `CLAUDE.md` authoring | Phase 7-specific skill scope selection (4 candidates); root `CLAUDE.md` 6-section authoring |
| 2 | Per-axis `CLAUDE.md` authoring (IS + AS) | 2 per-axis `CLAUDE.md` files authored per §2.1.2 5-section structure |
| 3 | Per-axis `CLAUDE.md` authoring (CP + OD) + sub-agent boundary specification | 2 per-axis `CLAUDE.md` files + sub-agent boundary specification |
| 4 | Phase 7-specific skill authoring (per OD scope decision from Segment 1) | 1–4 Phase 7-specific skills authored per `skill-creator` discipline |
| 5 | Coherence pass across bootstrap substrate (root + 4 per-axis + sub-agent + skills) | 5-dimension coherence pass: cross-artifact consistency + canonical citation resolution + anti-leakage rule application + stack discipline consistency + sub-agent boundary alignment |
| 6 | Artifact filing + close handoff + Session 7 kickoff | Bootstrap substrate filed; this artifact close handoff filed; `Phase_6_5_Session_7_Kickoff.md` filed |

Segment count varies by Segment 1 skill-scope decision: minimum scope (no skills) collapses Segment 4; extended scope (all 4 skills) may split Segment 4 into 4a + 4b.

### §5.2 Authoring methodology

Per `systems-architect` SKILL.md Phase 7 bootstrap substrate authoring discipline + `skill-creator` SKILL.md skill authoring discipline:

5.2.1 **Substrate-first authoring.** Every `CLAUDE.md` citation to canonical artifacts MUST resolve byte-exact (per Workflow v1.8 §7.4.2 byte-exact verification grammar, even though `CLAUDE.md` artifacts are out-of-scope of §7.4.6 audit per §7.4.6.4 — citation discipline applies as canonical-substrate authority).

5.2.2 **Anti-leakage discipline application at authoring time.** Every bootstrap substrate artifact MUST distinguish H_E primitives (Claude Code sub-agents; tool surface; CLAUDE.md hierarchy) from H_T primitives (CP-axis topology; AS-axis tool contracts; IS-axis state primitives). The 18 anti-leakage rules per `Phase_7_Meta_Architecture_v1.md` §7 are the canonical reference; sub-agent boundary specification (§2.1.4) is the most-direct application point.

5.2.3 **Cross-artifact consistency.** Per-axis `CLAUDE.md` files cite the same canonical artifacts via consistent paths; cross-axis edges per CXA v2.1 are cited consistently across per-axis `CLAUDE.md` files.

5.2.4 **Sub-agent boundary explicit anti-leakage citation.** Sub-agent boundary specification MUST cite anti-leakage rule CP-AL-1 (Claude Code sub-agent topology ≠ H_T CP-axis topology) verbatim or per `Phase_7_Meta_Architecture_v1.md` §7 citation-only grammar per §7.4.4.

5.2.5 **Custom skill authoring discipline.** Phase 7-specific skills authored per `skill-creator` SKILL.md frontmatter convention. Skill descriptions encode trigger conditions per `tool_search`-driven activation. Skills land in Claude Code CLI workspace at `/CLAUDE_CODE_WORKSPACE/.claude/skills/<skill-name>/SKILL.md` (path operator-confirmed at Segment 1 entry; Claude Code CLI skill-directory convention).

5.2.6 **Coherence pass at Segment 5.** End-to-end read across all bootstrap substrate artifacts: verify (a) citation resolution to canonical artifacts; (b) anti-leakage rule application at sub-agent boundary; (c) stack discipline consistency across per-axis files; (d) cross-axis edge consistency per CXA v2.1; (e) sub-agent boundary alignment with §2.1.4 specification.

### §5.3 Operator confirmation cadence

| Boundary | Confirmation form |
|---|---|
| Segment 1 close | Skill-scope decision + root `CLAUDE.md` review + Segment 2 entry confirmation |
| Segment 2 close | IS + AS per-axis `CLAUDE.md` review + Segment 3 entry confirmation |
| Segment 3 close | CP + OD per-axis `CLAUDE.md` + sub-agent boundary review + Segment 4 entry confirmation |
| Segment 4 close (skills) | Per-skill review + Segment 5 entry confirmation |
| Segment 5 close (coherence) | Coherence pass disposition + Segment 6 entry confirmation |
| Segment 6 close | Final artifact filing confirmation + Session 7 kickoff readiness |

---

## §6 Fork-handling

### §6.1 Class disposition routing

Per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4 + Workflow v1.8 §2.6.5.3 in-project fork management:

| Class | Routing |
|---|---|
| Class 1 (halt-arc) | Halt session; surface to operator; route per Manifest §4.2 |
| Class 2 (operator-decision-blocking) | Surface to operator with options menu; resume after disposition per Manifest §4.3 |
| Class 3 (informational) | Log at session close; route per Manifest §4.4 |

### §6.2 Session 6 specific fork surfaces

| Surface | Trigger | Routing |
|---|---|---|
| Bootstrap authoring surfaces H_T primitive gap | A canonical artifact (spec / plan / CXA / ADD / PRD) is incomplete or under-specified at a citation site | Class 1 — halt; surface to operator; route to Phase 6 plan revision (back-flow) OR Phase 5 spec revision OR Phase 3 ADR revision per defect locus |
| Bootstrap authoring surfaces H_E ↔ H_T boundary ambiguity | Claude Code CLI capability surface ambiguity at sub-agent boundary specification | Class 2 — surface to operator with options; resolve at sub-agent boundary specification with explicit citation to `Phase_7_Meta_Architecture_v1.md` §7 |
| Custom skill authoring surfaces design extension | A candidate skill scope (§2.1.3) requires H_T design extension to be authored cleanly | Class 1 — halt; surface to operator; route to design-phase back-flow (DO NOT silently extend H_T design at ε per anti-leakage discipline) |
| Per-axis `CLAUDE.md` cross-axis edge inconsistency | Cross-axis edge cited at axis A `CLAUDE.md` does not align with CXA v2.1 canonical edge inventory | Class 2 — surface; resolve at per-axis `CLAUDE.md` revision OR route to CXA v2.1 revision back-flow if canonical edge inventory is incomplete |
| Stack discipline application surfaces framework-pull risk | Bootstrap authoring surfaces a framework adoption that exceeds `Plan_Executability_Audit_v1.md` framework-pull discipline | Class 2 — surface; resolve at bootstrap authoring scope OR route to executability audit revision if framework-pull discipline is incomplete |

**Critical anti-leakage discipline at ε.** Per `Phase_7_Meta_Architecture_v1.md` §7 + §9 + Workflow v1.8 §2.6.5.7: bootstrap substrate authoring at ε MUST NOT extend H_T design. Bootstrap substrate is the H_E-workspace authoring surface; H_T canonical authority is at design-phase artifacts (ADR + ADD + specs + plans + CXA + Workflow). Any candidate H_T extension surfacing at ε routes per §6.2 surface table to design-phase back-flow.

---

## §7 Exit criteria

Session 6 (ε) closes when:

| # | Criterion |
|---|---|
| 1 | Root `CLAUDE.md` filed at `/mnt/user-data/outputs/` |
| 2 | Per-axis `CLAUDE.md` filed (IS + AS + CP + OD; 4 artifacts) |
| 3 | Sub-agent boundary specification filed |
| 4 | Phase 7-specific skills authored per OD scope decision (0–4 skills per Segment 1 operator decision) |
| 5 | `Phase_6_5_Session_6_Close_Handoff.md` filed |
| 6 | `Phase_6_5_Session_7_Kickoff.md` filed |
| 7 | All Class 1 / Class 2 forks dispositioned with operator decision recorded |
| 8 | Coherence pass verified at bootstrap substrate (5 dimensions per §5.2.6) |
| 9 | Anti-leakage discipline application verified at sub-agent boundary specification |
| 10 | No H_T design extension surfaced at ε (per anti-leakage discipline) |

---

## §8 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_6_Kickoff.md` |
| Status | Filed at Session 5 (γ) close 2026-05-15 |
| Phase | Phase 6.5 Session 6 (ε) entry |
| Authoring discipline | Workflow v1.8 §7 fidelity-grammar (workflow-document-itself out-of-scope of §7.4.6 per §7.4.6.4 but citation discipline applies); `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 session enumeration |
| Predecessor | `Phase_6_5_Session_5_Close_Handoff.md`; `Project_Workflow_v1_8.md` (Session 5 γ primary deliverable) |
| Successor (at session close) | Bootstrap substrate artifacts (root + per-axis `CLAUDE.md` + sub-agent boundary specification + 0–4 Phase 7-specific skills); `Phase_6_5_Session_6_Close_Handoff.md`; `Phase_6_5_Session_7_Kickoff.md` |
| Filing destination | `/mnt/user-data/outputs/Phase_6_5_Session_6_Kickoff.md` → operator pushes to `/mnt/project/` |
| Date | 2026-05-15 |

---

*End of Phase 6.5 Session 6 (ε) Kickoff. Session 6 entry authorized; awaiting operator session open.*

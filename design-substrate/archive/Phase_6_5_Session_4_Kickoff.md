# Phase 6.5 Session 4 Kickoff — Chicken-and-egg Meta-architecture + Phase 7 Internal Workflow (η + θ)

*Session entry artifact for Phase 6.5 Session 4. Loaded as substrate at session open. Authored at Session 3 (ζ) close; executed in a new session in this same project workspace.*

---

## §1 Session identity

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_4_Kickoff.md` |
| Phase | Phase 6.5 (pre-transition arc) |
| Session number | 4 of 7 |
| Session designator | η + θ |
| Session name | Chicken-and-egg meta-architecture (η) + Phase 7 internal workflow (θ) |
| Skill activation | `council-orchestrator` SKILL.md in **selective-convening sub-mode** (C1 + C7 + C11 voices) + `spec-writer` SKILL.md for canonicalization at Segment close |
| Authoring authority | Operator directive 2026-05-14 (Phase 6.5 arc entry); `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 Session 4 enumeration |
| Predecessor artifact | `Phase_6_5_Session_3_Close_Handoff.md` (Session 3 ζ close); IS plan v2.2 + OD plan v2.4 (canonical post-ζ substrate) |
| Companion artifact (canonical for entire arc) | `Phase_6_5_Pre_Transition_Arc_Manifest.md`; `Canonical_Substrate_Inventory.md` |
| Successor artifact (at session close) | `Phase_7_Meta_Architecture_v1.md` (combined OR split with `Phase_7_Internal_Workflow_v1.md` per Segment 1 operator decision); `Phase_6_5_Session_4_Close_Handoff.md`; `Phase_6_5_Session_5_Kickoff.md` |

---

## §2 Session scope

### §2.1 In scope

Two coupled scopes per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 Session 4:

#### §2.1.1 η — Meta-architecture authoring

Canonicalize the H_T ↔ H_E substitution discipline. Specifically:

| Surface | Content |
|---|---|
| H_T components catalog | Per-axis canonical primitives (IS / AS / CP / OD) sourced from v2.2 / v1 / v2.3 / v2.4 plans + CXA v2.1 + ADD v1.3 |
| H_E capabilities catalog | Claude Code CLI's tool surface (file ops, bash, web, sub-agent), turn loop, CLAUDE.md hierarchy, filesystem + git access, MCP integration surface |
| Capability overlap map | Per-primitive enumeration of where H_E natively provides an H_T-shaped capability vs where it does not |
| Substitution mapping table | Per not-yet-built-H_T-primitive: H_E substitution + bounded scope + retirement criterion at self-hosting milestone |
| Substitution-risk discipline | Anti-leakage rules preventing H_E patterns from contaminating H_T design (illustrative: Claude Code's sub-agent topology is NOT H_T's CP-axis topology; do not copy) |
| Self-hosting milestone gradient | Per H_T primitive: when it goes live → when the corresponding H_E substitution retires |

**Critical fork-handling discipline.** Per manifest §3.2 Session 4: this is the only Phase 6.5 session doing genuine *new* architectural work. If η surfaces a question about H_T design that wasn't resolved at Phase 6, route per §6 fork-handling — DO NOT silently extend H_T design at η. The discipline is: η authors the substitution discipline; it does NOT extend H_T's commitments.

#### §2.1.2 θ — Phase 7 internal workflow

Author Phase 7's sub-phase structure with discipline overlay. Specifically:

| Sub-phase | Content |
|---|---|
| 7a — Bootstrap | Foundational Level 0 units across all axes; minimum viable IS + OD + CP primitives operational |
| 7b — Per-axis interior execution | Axis-level cluster completion; intra-axis dependency-graph traversal |
| 7c — Cross-axis integration | CXA v2.1 composition seams; per-bucket edge instantiation |
| 7d — Self-hosting milestones | Per η substitution-retirement schedule; H_T primitives replace H_E substitutions |

Per-sub-phase requirements:

- Entry-gate criteria
- Exit criteria
- Back-flow routing (analog to Phase 6.5 §4 in-project fork management)
- Reduced-HITL viability assessment (which sub-phases are overnight-executable; which require operator presence)

### §2.2 Out of scope

- IS / AS / CP / OD plan revisions (preserved at v2.2 / v1 / v2.3 / v2.4 canonical revisions)
- ADR / ADD / PRD revisions (cleared at Phase 6 close)
- Spec revisions (preserved at canonical Phase 5 revisions)
- Workflow v1.8 promotion (Session 5 γ owns)
- Bootstrap substrate authoring at Claude Code CLI level (Session 6 ε owns)
- Phase 7 Session 1 Entry Directive authoring (Session 7 β owns)
- Implementation in any form (no code authored at this session)
- Stack revisions (Target_Stack_Commitment_v1.md preserved per Session 1 close)

### §2.3 Deliverables

Three artifacts filed at session close (combined-artifact path) OR four artifacts (split-artifact path) per Segment 1 operator decision:

**Combined path (default):**

| # | Artifact | Role |
|---|---|---|
| 1 | `Phase_7_Meta_Architecture_v1.md` | Combined η + θ: H_T↔H_E substitution discipline + Phase 7 sub-phase structure |
| 2 | `Phase_6_5_Session_4_Close_Handoff.md` | Session close handoff |
| 3 | `Phase_6_5_Session_5_Kickoff.md` | Session 5 (γ — Workflow v1.7 → v1.8 promotion) entry artifact |

**Split path (operator-elective):**

| # | Artifact | Role |
|---|---|---|
| 1 | `Phase_7_Meta_Architecture_v1.md` | η only: H_T↔H_E substitution discipline |
| 2 | `Phase_7_Internal_Workflow_v1.md` | θ only: Phase 7 sub-phase structure |
| 3 | `Phase_6_5_Session_4_Close_Handoff.md` | Session close handoff |
| 4 | `Phase_6_5_Session_5_Kickoff.md` | Session 5 entry artifact |

Default selection: **combined path** (η and θ are tightly coupled: θ sub-phase 7d is parameterized by η self-hosting milestone gradient; reading both together preserves coherence).

---

## §3 Substrate retrieval

### §3.1 Canonical Phase 6.5 substrate (load first)

| # | Artifact | Path | Role |
|---|---|---|---|
| 1 | `Phase_6_5_Pre_Transition_Arc_Manifest.md` | `/mnt/project/` | Arc framing + sequence context + fork-handling discipline |
| 2 | `Canonical_Substrate_Inventory.md` | `/mnt/project/` | KB navigation anchor; disambiguates canonical vs superseded artifacts |
| 3 | `Phase_7_Kickoff_Prompt.md` | `/mnt/project/` | Phase 7 entry framing + back-flow routing; θ output informs Phase 7 entry directive |
| 4 | `Phase_6_5_Session_3_Close_Handoff.md` | `/mnt/project/` (after operator push) | Session 3 ζ close record; canonical-substrate carry-forward |
| 5 | `Target_Stack_Commitment_v1.md` | `/mnt/project/` | Stack commitment (Session 1 δ); informs H_E capability binding per stack-specific Claude Code CLI behavior |
| 6 | `Plan_Executability_Audit_v1.md` | `/mnt/project/` | Session 2 α deliverable; framework-pull + monorepo-subdivision + instrumentation-genai findings inform substitution-risk surfaces |

### §3.2 Implementation plan substrate (H_T canonical content)

Per Workflow v1.7 §7 use-latest-version discipline:

| Plan | Canonical file | Role at Session 4 |
|---|---|---|
| IS axis | `Implementation_Plan_Information_Substrate_v2_2.md` | H_T IS-axis primitives catalog (17 units; substrate seam exports) |
| AS axis | `Implementation_Plan_Action_Surface_v1.md` | H_T AS-axis primitives catalog (33 units; tool / skill / sandbox surface) |
| CP axis | `Implementation_Plan_Control_Plane_v2_3.md` | H_T CP-axis primitives catalog (55 units; orchestration + topology + retry + breaker + handoff) |
| OD axis | `Implementation_Plan_Operational_Discipline_v2_4.md` | H_T OD-axis primitives catalog (34 units; observability + HITL + audit + cost-attribution) |
| CXA | `Cross_Axis_Composition_Document_v2_1.md` | H_T cross-axis composition seams (~80+ edges across AS↔IS, CP↔IS, CP↔AS, OD↔IS, OD↔AS, OD↔CP) |

### §3.3 ADR + ADD + PRD substrate (H_T architectural commitment substrate)

Consulted ad-hoc per meta-architecture authoring need:

- **ADR-F1 v1.2** — provider portability (multi-LLM); informs H_E provider binding
- **ADR-F2 v1.2** — state ledger substrate
- **ADR-F3 v1.1** — engine event history; informs H_E execution-trace shape
- **ADR-F5 v1.1** — local-deployment ergonomics; informs H_E local-stack binding
- **ADR-D1 v1.2** — engine + replay; informs H_E re-execution discipline
- **ADR-D2 v1.1** — sandbox / blast-radius; informs H_E containment substitution
- **ADR-D6 v1.2** — observability + cost-attribution; informs H_E telemetry binding
- **Architectural_Design_Document_v1_3.md** — axis decomposition canonical
- **PRD_v1_1.md** — observable-behavior commitments

### §3.4 Spec substrate (consulted ad-hoc)

| Spec | Canonical file |
|---|---|
| IS spec v1.2 | `Spec_Information_Substrate_v1.md` |
| AS spec v1.1 | `Spec_Action_Surface_v1.md` |
| CP spec v1.3 | `Spec_Control_Plane_v1_3.md` |
| OD spec v1.3 | `Spec_Operational_Discipline_v1_3.md` |

### §3.5 V3 system prompt

Loaded at workspace level. Confidence tagging + source-grounding + anti-fabrication discipline apply at this session. Particularly relevant at η: substitution mapping claims must distinguish H_E *verified* capabilities (consult Anthropic Claude Code documentation; web-search permitted) from H_E *speculative* capabilities ([SPECULATIVE] tag mandatory).

### §3.6 Skill activation

`council-orchestrator` SKILL.md in **selective-convening sub-mode** per §3.2 Session 4 manifest framing. Voices to engage:

| Voice | Role at η + θ |
|---|---|
| C1 — Orchestration & Control | CP-axis meta-design; sub-agent topology distinction H_T vs H_E; loop-shape contracts |
| C7 — Observability | OD-axis meta-design; span schema; OTel binding under H_E; cost-attribution carrier |
| C11 — Operator Loop & Local Deployment | HITL primitive substitution; local-deployment substitution gradient; sqlite + keychain bindings |

Full-council convening NOT required per manifest §3.2 ("η is not a primary architectural decision; it's a build-time discipline overlay"). Voices invoked when meta-architecture surface engages their domain.

`spec-writer` SKILL.md activated at Segment close for canonicalization of the meta-architecture artifact.

---

## §4 Entry-gate verification

At session open, verify:

| # | Check | Verification |
|---|---|---|
| 1 | Phase 6.5 manifest accessible | `project_knowledge_search` returns content |
| 2 | `Phase_6_5_Session_3_Close_Handoff.md` accessible at `/mnt/project/` | `project_knowledge_search` returns content; operator pushed between sessions |
| 3 | IS plan v2.2 + OD plan v2.4 accessible (Session 3 ζ deliverables) | Same |
| 4 | AS plan v1 + CP plan v2.3 + CXA v2.1 accessible | Same |
| 5 | `Target_Stack_Commitment_v1.md` accessible | Same |
| 6 | `Plan_Executability_Audit_v1.md` accessible | Same |
| 7 | ADD v1.3 + PRD v1.1 + canonical ADRs accessible | Same |
| 8 | All canonical specs accessible | Same |
| 9 | No open Class 1 / Class 2 forks from Session 3 | Per `Phase_6_5_Session_3_Close_Handoff.md` §7.4 (none surfaced or carried forward) |

If any entry-gate item fails, halt session open; surface to operator before proceeding.

---

## §5 Session execution discipline

### §5.1 Segmented delivery contract

6-segment delivery per manifest §3.2 Session 4 estimate:

| Segment | Scope | Approximate output |
|---|---|---|
| 1 | Artifact-structure decision + H_T components catalog + H_E capabilities catalog | Combined vs split artifact operator decision; H_T per-axis primitives enumeration (sourced from v2.2 / v1 / v2.3 / v2.4 plans); H_E capabilities catalog (Claude Code CLI tool surface; consult Anthropic documentation for verification) |
| 2 | Capability overlap map | Per-primitive enumeration: H_E provides natively (✓) vs H_E does not provide (✗) vs H_E partial-substitute (~) |
| 3 | Substitution mapping table authoring | Per H_T primitive lacking H_E native support: substitution + scope + retirement criterion |
| 4 | Substitution-risk discipline | Anti-leakage rules; per-axis discipline statements; canonical examples (Claude Code sub-agent ≠ H_T CP topology; etc.) |
| 5 | Phase 7 sub-phase structure (θ) | 7a / 7b / 7c / 7d structure; per-sub-phase entry-gate + exit + back-flow + HITL viability |
| 6 | Coherence pass + close handoff + Session 5 kickoff | Meta-architecture artifact filing; close handoff authoring; Session 5 (γ) kickoff authoring |

Segments 1–4 are η scope. Segment 5 is θ scope. Segment 6 closes session.

### §5.2 Authoring methodology

Per `council-orchestrator` SKILL.md selective-convening sub-mode + `spec-writer` SKILL.md canonicalization discipline:

5.2.1 **Substrate-first cataloging.** η components catalog sourced from filed v2.2 / v1 / v2.3 / v2.4 plans. No new H_T commitments; cataloging only.

5.2.2 **H_E capability verification.** Claude Code CLI capability claims require source verification — consult Anthropic documentation; web-search permitted per V3 system prompt. Speculative claims tagged [SPECULATIVE].

5.2.3 **Per-axis discipline statement authoring.** Anti-leakage rules per axis surface, with canonical illustrative examples grounded in plan content.

5.2.4 **Self-hosting milestone gradient.** Per-primitive cross-reference to atomic-unit IDs (e.g., "U-IS-11 going live retires the H_E filesystem write substitution"). Cross-reference fidelity per `implementation-planner` SKILL.md §4 spec-traceability discipline (cite by unit ID).

5.2.5 **Phase 7 sub-phase structure derivation.** Sub-phase entry-gate / exit / back-flow / HITL-viability authored against dependency-graph topology + cross-axis composition seams (CXA v2.1).

5.2.6 **Coherence pass.** End-to-end read at Segment 6; verify η ↔ θ coupling (substitution retirements in η align with self-hosting milestones in 7d).

### §5.3 Operator confirmation cadence

| Boundary | Confirmation form |
|---|---|
| Segment 1 close | Combined vs split artifact decision; H_T + H_E catalogs review; Segment 2 entry confirmation |
| Segment 2 close | Capability overlap map review; Segment 3 entry confirmation |
| Segment 3 close | Substitution mapping table review; Segment 4 entry confirmation |
| Segment 4 close | Substitution-risk discipline review; Segment 5 entry confirmation (η → θ pivot) |
| Segment 5 close | Phase 7 sub-phase structure review; Segment 6 entry confirmation |
| Segment 6 close | Final artifact filing confirmation; Session 5 kickoff readiness |

---

## §6 Fork-handling

### §6.1 Class disposition routing

Per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4 in-project fork management:

| Class | Routing |
|---|---|
| Class 1 (halt-arc) | Halt session; surface to operator; route per Manifest §4.2 |
| Class 2 (operator-decision-blocking) | Surface to operator with options menu; resume after disposition per Manifest §4.3 |
| Class 3 (informational) | Log at session close; route per Manifest §4.4 |

### §6.2 η-specific fork-handling (load-bearing)

Per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 Session 4 explicit discipline:

> If η surfaces a question about H_T design that wasn't resolved at Phase 6, route per §6 fork-handling — DO NOT silently extend H_T design at η. The discipline is: η authors the substitution discipline; it does NOT extend H_T's commitments.

This discipline binds at every segment. Surface candidate forks:

| Surface | Trigger | Routing |
|---|---|---|
| Cataloging surfaces H_T primitive gap | A plan-cited primitive is incomplete or under-specified | Class 2 — surface to operator; route to Phase 6 revision (back-flow) OR defer to Phase 7 execution-time fork per Phase 7 Kickoff §6 |
| Capability overlap reveals H_E primitive H_T didn't anticipate | H_E provides capability not in H_T architectural decomposition | Class 2 — surface; route to ADR back-flow (Phase 3) if H_T should adopt; OR document at substitution-risk discipline as anti-leakage if H_T should reject |
| Substitution scope ambiguity | H_E substitution boundary blurs with H_T primitive scope | Class 2 — surface; resolve at operator decision with explicit boundary declaration |
| Self-hosting milestone ordering ambiguity | Two H_T primitives could retire one H_E substitution in different orders | Class 3 — log; route to Phase 7 execution-time scheduling |

### §6.3 θ-specific fork-handling

Per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 Session 4 θ scope:

| Surface | Trigger | Routing |
|---|---|---|
| Sub-phase boundary conflicts dependency-graph topology | A unit's dependencies span an authored sub-phase boundary | Class 2 — surface; resolve at sub-phase boundary redrawing OR explicit cross-sub-phase dependency declaration |
| HITL-viability assessment surfaces operator-burden concern | Sub-phase requires operator presence beyond practical sustainment | Class 3 — log; document at sub-phase HITL declaration; surface to Session 6 (ε) bootstrap substrate for HITL primitive substitution |

---

## §7 Exit criteria

Session 4 (η + θ) closes when:

| # | Criterion |
|---|---|
| 1 | `Phase_7_Meta_Architecture_v1.md` filed at `/mnt/user-data/outputs/` (combined path) OR `Phase_7_Meta_Architecture_v1.md` + `Phase_7_Internal_Workflow_v1.md` filed (split path) |
| 2 | `Phase_6_5_Session_4_Close_Handoff.md` filed |
| 3 | `Phase_6_5_Session_5_Kickoff.md` filed |
| 4 | All Class 1 / Class 2 forks dispositioned with operator decision recorded |
| 5 | η components catalog complete (all H_T canonical primitives per v2.2 / v1 / v2.3 / v2.4 + CXA v2.1 enumerated) |
| 6 | η capability overlap map complete (per H_T primitive: H_E status — native / partial / absent) |
| 7 | η substitution mapping table complete (per H_T primitive lacking H_E native support: substitution + scope + retirement criterion) |
| 8 | η substitution-risk discipline authored (per-axis anti-leakage rules + canonical examples) |
| 9 | η self-hosting milestone gradient authored (per-primitive: live-criterion + substitution-retirement-criterion) |
| 10 | θ Phase 7 sub-phase structure authored (7a + 7b + 7c + 7d with entry-gate + exit + back-flow + HITL viability per sub-phase) |
| 11 | η ↔ θ coupling verified (substitution retirements in η align with self-hosting milestones in 7d) |
| 12 | No H_T design extension surfaced at η (per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 Session 4 discipline) |

---

## §8 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_4_Kickoff.md` |
| Status | Filed at Session 3 (ζ) close 2026-05-15 |
| Phase | Phase 6.5 Session 4 (η + θ) entry |
| Authoring discipline | Workflow v1.7 §7 fidelity-grammar; `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 session enumeration |
| Predecessor | `Phase_6_5_Session_3_Close_Handoff.md`; IS plan v2.2 + OD plan v2.4 (Session 3 ζ deliverables) |
| Successor (at session close) | `Phase_7_Meta_Architecture_v1.md` (combined or split per Segment 1 operator decision); `Phase_6_5_Session_4_Close_Handoff.md`; `Phase_6_5_Session_5_Kickoff.md` |
| Filing destination | `/mnt/user-data/outputs/Phase_6_5_Session_4_Kickoff.md` → operator pushes to `/mnt/project/` |
| Date | 2026-05-15 |

---

*End of Phase 6.5 Session 4 (η + θ) Kickoff. Session 4 entry authorized; awaiting operator session open.*

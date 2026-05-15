# Phase 6.5 Session 7 Kickoff — Phase 7 Session 1 Entry Directive (β)

*Session entry artifact for Phase 6.5 Session 7. Loaded as substrate at session open. Authored at Session 6 (ε) close; executed in a new session in this same project workspace. Final session of the Phase 6.5 pre-transition arc. Operator-side workspace transfer to the new Claude Code CLI workspace occurs at this session's close per arc manifest §3.4 + DP-4 default.*

---

## §1 Session identity

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_7_Kickoff.md` |
| Phase | Phase 6.5 (pre-transition arc) |
| Session number | 7 of 7 — **final session of Phase 6.5 arc** |
| Session designator | β |
| Session name | Phase 7 Session 1 Entry Directive |
| Skill activation | `systems-architect` SKILL.md (Phase 7 entry directive authoring; analog to Phase 4 PRD authoring discipline — directive-from-substrate inverted ordering); `spec-writer` SKILL.md at Segment close for canonicalization |
| Authoring authority | Operator directive 2026-05-14 (Phase 6.5 arc entry); `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 Session 7 enumeration; `Project_Workflow_v1_8.md` §2.6.5.4 criteria 7 + 8 + 9 |
| Predecessor artifact | `Phase_6_5_Session_6_Close_Handoff.md` (Session 6 ε close); 10 bootstrap substrate artifacts at `/mnt/user-data/outputs/` (Session 6 ε primary deliverables) |
| Companion artifact (canonical for entire arc) | `Phase_6_5_Pre_Transition_Arc_Manifest.md`; `Canonical_Substrate_Inventory.md` |
| Successor artifact (at session close) | `Phase_7_Session_1_Entry_Directive_v1.md`; handoff package (bootstrap substrate + design-phase artifact pointers); `Phase_6_5_Session_7_Close_Handoff.md`; Phase 6.5 arc closure record |
| Workspace transfer trigger | Session close → operator-side push of bootstrap substrate to new Claude Code CLI workspace per arc manifest §3.4 |

---

## §2 Session scope

### §2.1 In scope

Author the canonical Phase 7 Session 1 Entry Directive — the entry artifact for the first Phase 7 session in the new Claude Code CLI workspace. Per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 Session 7 + Workflow v1.8 §2.6.5.4 criteria 7 + 8 + 9:

#### §2.1.1 Phase 7 Session 1 Entry Directive (`Phase_7_Session_1_Entry_Directive_v1.md`)

Workspace-level entry artifact for Phase 7 sub-phase 7a (bootstrap) execution at the new Claude Code CLI workspace. Authoring scope:

| Sub-section | Content |
|---|---|
| Session identity | Phase 7 Session 1 framing; workspace target = new Claude Code CLI workspace; entry-gate authority chain |
| Substrate inventory | 10 bootstrap substrate artifacts present at workspace; canonical design-phase artifact pointers (49+ artifacts at design-phase workspace) |
| Phase 7 sub-phase 7a entry-gate verification | Per `Phase_7_Meta_Architecture_v1.md` §10.1 entry-gate criteria |
| First atomic units to land | Foundational L0 entry-points across IS / AS / CP / OD per per-axis `CLAUDE.md` §3 (23 total L0 units: 5 IS + 3 AS + 13 CP + 2 OD) |
| Per-cluster confirmation cadence at 7a | Per Meta-Architecture §10.1 + §10.2.4 |
| 7a exit criteria | Per Meta-Architecture §10.1.6 |
| Substitution scaffolding declaration | H_E substitutions active at 7a entry per Meta-Architecture §5; H_T-CP-1 single-LLM-during-7a substitution explicit |
| Sub-agent topology activation | Sub-agent count + activation sequence per `Sub_Agent_Boundary_Specification_v1.md` §3 + §4 |
| Skill activation surface | 4 Phase 7-specific skills available per `.claude/skills/` per OD-ε-1 + OD-ε-2 |
| Back-flow routing | Class 1 fork routes to design-phase workspace per workspace root `CLAUDE.md` §4.3 + `phase-7-back-flow-routing` skill |
| Anti-leakage discipline binding | 18 anti-leakage rules per Meta-Architecture §7 + 3 cross-cutting X-AL-1 / X-AL-2 / X-AL-3 binding from Phase 7 Session 1 onward |

#### §2.1.2 Handoff package assembly

Per Workflow v1.8 §2.6.5.4 criterion 8: handoff package assembled for new-workspace transfer. Content:

| Element | Source | Target |
|---|---|---|
| Bootstrap substrate (10 artifacts) | `/mnt/user-data/outputs/` (Session 6 ε output) | `<new_workspace_root>/` |
| Phase 7 Session 1 Entry Directive (this session's primary deliverable) | `/mnt/user-data/outputs/Phase_7_Session_1_Entry_Directive_v1.md` | `<new_workspace_root>/` |
| Canonical design-phase artifact reference list | Authored at this session as part of Phase 7 Session 1 Entry Directive | Phase 7 Session 1 reads via design-phase workspace `/mnt/project/` |

Note: design-phase artifacts (ADRs / ADD / PRD / specs / plans / Meta-Architecture / Workflow / CXA) are NOT transferred to the new workspace. The new workspace reads them via cross-workspace reference per arc manifest §6 each-session opening read pattern.

#### §2.1.3 Phase 6.5 arc closure record

Per Workflow v1.8 §2.6.5.4 criterion 9. Filed at `Phase_6_5_Session_7_Close_Handoff.md` §[arc closure]. Records:

| Element | Content |
|---|---|
| All 9 arc-completion criteria satisfied | Verified at session close §[arc closure status] |
| All Class 1 / Class 2 forks dispositioned | Per `Project_Workflow_v1_8.md` §2.6.5.3 in-project fork management |
| Workspace transfer authorized | Operator-side push of bootstrap substrate authorized at session close |
| Phase 7 entry authorization | Phase 7 sub-phase 7a execution authorized at new workspace |

### §2.2 Out of scope

- Bootstrap substrate revisions (10 artifacts preserved at canonical Session 6 ε close versions)
- Workflow revisions (`Project_Workflow_v1_8.md` canonical; revision scope out-of-session)
- Meta-architecture revisions (`Phase_7_Meta_Architecture_v1.md` canonical; revision scope out-of-session)
- Plan / spec / ADR / ADD / PRD revisions (canonical at Phase 6 close + Phase 6.5 closures)
- Stack revisions (`Target_Stack_Commitment_v1.md` canonical)
- Implementation in any form (no H_T code authored at this session; no H_E sub-agent activation; Phase 7 execution begins at new workspace Session 1, NOT here)
- H_T design extension (per X-AL-3 binding)
- New Class 1 / Class 2 fork introduction (arc-completion-criteria requires all forks dispositioned)

If authoring surfaces a question about any of these, route per §6 fork-handling.

### §2.3 Deliverables

| # | Artifact | Path | Target |
|---|---|---|---|
| 1 | `Phase_7_Session_1_Entry_Directive_v1.md` | `/mnt/user-data/outputs/Phase_7_Session_1_Entry_Directive_v1.md` | New Claude Code CLI workspace root |
| 2 | `Phase_6_5_Session_7_Close_Handoff.md` | `/mnt/user-data/outputs/Phase_6_5_Session_7_Close_Handoff.md` | Design-phase `/mnt/project/` |
| 3 | Phase 6.5 arc closure record | Embedded at close handoff §[arc closure] | Design-phase `/mnt/project/` |
| 4 | Workspace transfer authorization | Embedded at close handoff §[workspace transfer] | Design-phase `/mnt/project/` + operator action |

---

## §3 Substrate retrieval

### §3.1 Canonical Phase 6.5 substrate (load first)

| # | Artifact | Path | Role |
|---|---|---|---|
| 1 | `Phase_6_5_Pre_Transition_Arc_Manifest.md` | `/mnt/project/` | Arc framing + sequence context + fork-handling discipline |
| 2 | `Canonical_Substrate_Inventory.md` | `/mnt/project/` | KB navigation anchor |
| 3 | `Phase_6_5_Session_6_Close_Handoff.md` | `/mnt/project/` (after operator push) | Session 6 close record; substrate carry-forward |
| 4 | `Project_Workflow_v1_8.md` | `/mnt/project/` | Canonical workflow at v1.8 |
| 5 | `Phase_7_Meta_Architecture_v1.md` | `/mnt/project/` | Phase 7 execution discipline + sub-phase enumeration |
| 6 | `Phase_7_Kickoff_Prompt.md` | `/mnt/project/` | Portable Phase 7 kickoff |
| 7 | `Target_Stack_Commitment_v1.md` | `/mnt/project/` | Stack discipline |
| 8 | `Plan_Executability_Audit_v1.md` | `/mnt/project/` | Framework-pull discipline |

### §3.2 Bootstrap substrate (Session 6 ε output — read at authoring time)

| Artifact | Path |
|---|---|
| Root `CLAUDE.md` | `/mnt/user-data/outputs/CLAUDE.md` |
| 4 per-axis `CLAUDE.md` files | `/mnt/user-data/outputs/harness-{is,as,cp,od}/CLAUDE.md` |
| `Sub_Agent_Boundary_Specification_v1.md` | `/mnt/user-data/outputs/Sub_Agent_Boundary_Specification_v1.md` |
| 4 Phase 7-specific `SKILL.md` files | `/mnt/user-data/outputs/.claude/skills/phase-7-{implementation,cross-axis-composition,substitution-retirement,back-flow-routing}/SKILL.md` |

### §3.3 Spec + plan + ADR substrate (cited at Phase 7 Session 1 Entry Directive)

Per Canonical Substrate Inventory §3.6 (post-Session 6 close):

| Artifact family | Canonical version |
|---|---|
| Specs | IS v1.2 / AS v1.1 / CP v1.3 / OD v1.3 |
| Plans | IS v2.2 / AS v1 / CP v2.3 / OD v2.4 |
| Cross-axis composition | CXA v2.1 |
| Foundational ADRs | F1 v1.2 / F2 v1.2 / F3 v1.1 / F4 v1.1 / F5 v1.1 |
| Derivative ADRs | D1 v1.2 / D2 v1.1 / D3 v1.2 / D4 v1.1 / D5 v1.3 / D6 v1.2 |
| ADD | v1.3 |
| PRD | v1.1 |

### §3.4 V3 system prompt

Loaded at workspace level. Confidence tagging + source-grounding + anti-fabrication discipline apply. Particularly relevant at Phase 7 Session 1 Entry Directive authoring: directive citations to canonical artifacts must resolve byte-exact per Workflow v1.8 §7.4.2.

### §3.5 Skill activation

| Skill | Sub-mode | Trigger |
|---|---|---|
| `systems-architect` | Phase 7 entry directive authoring (analog to Phase 4 PRD authoring discipline — directive-from-substrate inverted ordering) | Phase 7 Session 1 Entry Directive authoring |
| `spec-writer` | Canonicalization at Segment close | Final artifact composition; cross-section traceability verification |

---

## §4 Entry-gate verification

At session open, verify:

| # | Check | Verification |
|---|---|---|
| 1 | Phase 6.5 manifest accessible | `project_knowledge_search` returns content |
| 2 | Canonical Substrate Inventory accessible | `project_knowledge_search` returns content |
| 3 | `Phase_6_5_Session_6_Close_Handoff.md` accessible at `/mnt/project/` | Operator pushed between sessions |
| 4 | `Phase_6_5_Session_7_Kickoff.md` accessible at `/mnt/project/` | Operator pushed between sessions |
| 5 | All 10 bootstrap substrate artifacts present at `/mnt/user-data/outputs/` | Per Session 6 close §4.1 inventory |
| 6 | No open Class 1 / Class 2 forks from Session 6 (ε) | Per Session 6 close §5.1 + §5.2 — both zero |
| 7 | `Project_Workflow_v1_8.md` + `Phase_7_Meta_Architecture_v1.md` + `Target_Stack_Commitment_v1.md` + `Plan_Executability_Audit_v1.md` + `Phase_7_Kickoff_Prompt.md` accessible | Already at `/mnt/project/` from arc entry |
| 8 | All canonical specs + plans + ADRs + ADD v1.3 + PRD v1.1 + CXA v2.1 accessible | Already at `/mnt/project/` from Phase 6 close |

If any entry-gate item fails, halt session open; surface to operator before proceeding.

---

## §5 Session execution discipline

### §5.1 Segmented delivery contract

3–4 segments estimated per Phase 7 Session 1 Entry Directive scope:

| Segment | Scope | Approximate output |
|---|---|---|
| 1 | Substrate read + Phase 7 Session 1 Entry Directive structure decision + directive §1–§4 authoring (identity + substrate inventory + entry-gate verification + 7a sub-phase activation) | Entry directive ~50% authored |
| 2 | Directive §5–§8 authoring (first atomic units + per-cluster cadence + 7a exit criteria + substitution scaffolding declaration + sub-agent topology activation + skill activation surface + back-flow routing) | Entry directive complete |
| 3 | Coherence pass + handoff package assembly + Phase 6.5 arc closure record authoring | Close handoff complete |
| 4 | Final filing + workspace transfer authorization | Workspace transfer ready |

Segment count amendable per operator direction at session execution.

### §5.2 Authoring methodology

Per `systems-architect` SKILL.md Phase 7 entry directive authoring discipline:

5.2.1 **Substrate-first authoring.** Every directive citation to canonical artifacts MUST resolve byte-exact (per Workflow v1.8 §7.4.2 byte-exact verification grammar). The Phase 7 Session 1 Entry Directive is the substrate authority for Phase 7 sub-phase 7a execution; citation discipline applies.

5.2.2 **No H_T design extension at directive authoring.** Per X-AL-3 binding: the directive enumerates what Phase 7 Session 1 reads + executes. It does NOT extend H_T design. New H_T primitives surfaced at directive authoring route to design-phase back-flow.

5.2.3 **Cross-workspace reference discipline.** The directive lives at the new Claude Code CLI workspace; design-phase artifacts live at the design-phase workspace. Cross-workspace references at the directive cite design-phase artifact paths (`/mnt/project/` from design-phase perspective).

5.2.4 **Phase 6.5 arc closure preservation.** All 9 arc-completion criteria verified at session close handoff. Workspace transfer authorized only after closure verification.

5.2.5 **Coherence pass at Segment 3.** End-to-end read across Phase 7 Session 1 Entry Directive + handoff package + arc closure record: verify (a) citation resolution to canonical artifacts; (b) anti-leakage discipline binding at directive; (c) sub-agent activation alignment with Sub_Agent_Boundary_Specification_v1.md; (d) skill activation alignment with 4 Phase 7-specific skills; (e) arc-completion-criteria verification.

### §5.3 Operator confirmation cadence

| Boundary | Confirmation form |
|---|---|
| Segment 1 close | Directive §1–§4 review + Segment 2 entry confirmation |
| Segment 2 close | Directive §5–§8 review + Segment 3 entry confirmation |
| Segment 3 close | Coherence pass disposition + arc closure record review + Segment 4 entry confirmation |
| Segment 4 close | Final artifact filing + workspace transfer authorization + Phase 6.5 arc CLOSED |

---

## §6 Fork-handling

### §6.1 Class disposition routing

Per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4 + Workflow v1.8 §2.6.5.3 in-project fork management:

| Class | Routing |
|---|---|
| Class 1 (halt-arc) | Halt session; surface to operator; route per Manifest §4.2; **Class 1 at this session blocks workspace transfer** until disposition |
| Class 2 (operator-decision-blocking) | Surface to operator with options menu; resume after disposition per Manifest §4.3 |
| Class 3 (informational) | Log at session close; route per Manifest §4.4 |

### §6.2 Session 7 specific fork surfaces

| Surface | Trigger | Routing |
|---|---|---|
| Directive authoring surfaces bootstrap substrate gap | A bootstrap artifact (root + per-axis + Sub-Agent + skill) is incomplete or under-specified at a citation site | Class 1 — halt; surface to operator; route to bootstrap substrate revision (loop back to Session 6 scope) |
| Directive authoring surfaces design-phase artifact gap | A canonical design-phase artifact is incomplete at a directive citation site | Class 1 — halt; surface to operator; route to design-phase back-flow (Phase 6 plan / Phase 5 spec / Phase 3 ADR / Phase 4 PRD / Phase 6 CXA) |
| Directive authoring surfaces Phase 7 sub-phase 7a entry-gate gap | A 7a entry-gate criterion (Meta-Architecture §10.1.5) cannot be verified at directive authoring | Class 1 — halt; surface to operator; route to Meta-Architecture §10.1 revision OR Phase 7 entry-gate criteria refinement |
| Arc closure record surfaces missing arc-completion criterion | A 9-criterion completion gate item not satisfied | Class 1 — halt; surface to operator; route to applicable Session 1–6 re-execution |
| Workspace transfer authorization conditional surface | Operator declines workspace transfer at session close | Class 2 — operator decision; workspace transfer deferred; Phase 6.5 arc remains OPEN until authorization |

**Critical discipline at β.** Per arc manifest §5 + Workflow v1.8 §2.6.5.4: arc-completion-criteria gating workspace transfer is non-negotiable. Class 1 forks at this session block both workspace transfer AND Phase 6.5 arc closure.

---

## §7 Exit criteria

Session 7 (β) closes — and the Phase 6.5 arc closes — when:

| # | Criterion |
|---|---|
| 1 | `Phase_7_Session_1_Entry_Directive_v1.md` filed at `/mnt/user-data/outputs/` |
| 2 | `Phase_6_5_Session_7_Close_Handoff.md` filed at `/mnt/user-data/outputs/` |
| 3 | All Class 1 / Class 2 forks dispositioned with operator decision recorded |
| 4 | Coherence pass verified at Phase 7 Session 1 Entry Directive (5 dimensions per §5.2.5) |
| 5 | Anti-leakage discipline binding verified at directive (X-AL-1 / X-AL-2 / X-AL-3 + 18 axis rules) |
| 6 | No H_T design extension surfaced at β (per X-AL-3 binding) |
| 7 | 9-criterion arc-completion gate all satisfied (per Workflow v1.8 §2.6.5.4) |
| 8 | Workspace transfer authorization recorded at close handoff |
| 9 | Operator-side push of bootstrap substrate to new Claude Code CLI workspace authorized |
| 10 | Phase 6.5 arc closure record filed at close handoff §[arc closure] |
| 11 | Phase 7 entry authorization at new Claude Code CLI workspace granted |

Phase 6.5 arc CLOSES at exit criteria 1–11 all satisfied. Phase 7 sub-phase 7a executes at new workspace Session 1.

---

## §8 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_7_Kickoff.md` |
| Status | Filed at Session 6 (ε) close 2026-05-15 |
| Phase | Phase 6.5 Session 7 (β) entry — **final session of arc** |
| Authoring discipline | Workflow v1.8 §7 fidelity-grammar; arc manifest §3.2 Session 7 enumeration |
| Predecessor | `Phase_6_5_Session_6_Close_Handoff.md`; 10 bootstrap substrate artifacts at `/mnt/user-data/outputs/` |
| Successor (at session close) | `Phase_7_Session_1_Entry_Directive_v1.md`; `Phase_6_5_Session_7_Close_Handoff.md`; Phase 6.5 arc closure record; workspace transfer authorization |
| Filing destination | `/mnt/user-data/outputs/Phase_6_5_Session_7_Kickoff.md` → operator pushes to design-phase `/mnt/project/` |
| Workspace transfer trigger | Session 7 close = operator-side push of bootstrap substrate to new Claude Code CLI workspace per arc manifest §3.4 + DP-4 default |
| Date | 2026-05-15 |

---

*End of Phase 6.5 Session 7 (β) Kickoff. Session 7 entry authorized; awaiting operator session open. Phase 6.5 arc closes at this session's close.*

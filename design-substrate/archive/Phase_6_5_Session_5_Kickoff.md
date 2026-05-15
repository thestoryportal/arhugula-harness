# Phase 6.5 Session 5 Kickoff — Workflow v1.7 → v1.8 Promotion (γ)

*Session entry artifact for Phase 6.5 Session 5. Loaded as substrate at session open. Authored at Session 4 (η + θ) close; executed in a new session in this same project workspace.*

---

## §1 Session identity

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_5_Kickoff.md` |
| Phase | Phase 6.5 (pre-transition arc) |
| Session number | 5 of 7 |
| Session designator | γ |
| Session name | Workflow v1.7 → v1.8 Promotion |
| Skill activation | `spec-writer` SKILL.md (workflow-promotion variant); `implementation-planner` SKILL.md §8 revision-pass sub-mode (workflow revision discipline) |
| Authoring authority | Operator directive 2026-05-14 (Phase 6.5 arc entry); `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 Session 5 enumeration |
| Predecessor artifact | `Phase_6_5_Session_4_Close_Handoff.md` (Session 4 η+θ close); `Phase_7_Meta_Architecture_v1.md` (Session 4 primary deliverable) |
| Companion artifact (canonical for entire arc) | `Phase_6_5_Pre_Transition_Arc_Manifest.md`; `Canonical_Substrate_Inventory.md` |
| Successor artifact (at session close) | `Project_Workflow_v1_8.md`; `Project_Workflow_Revision_log.md` (updated); `Phase_6_5_Session_5_Close_Handoff.md`; `Phase_6_5_Session_6_Kickoff.md` |

---

## §2 Session scope

### §2.1 In scope

Promote `Project_Workflow_v1_7.md` to `Project_Workflow_v1_8.md` absorbing all amendments enumerated at `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md`. Specifically:

#### §2.1.1 §6.5 formal pre-transition arc specification

Retroactively codify the Phase 6.5 arc executed across Sessions δ (Session 1) + α (Session 2) + ζ (Session 3) + η+θ (Session 4) + this session (γ) + ε (Session 6) + β (Session 7). Authoring scope:

| Sub-section | Content |
|---|---|
| §6.5.1 Arc framing | Pre-transition arc bridging Phase 6 close → Phase 7 entry; chicken-and-egg paradox framing |
| §6.5.2 Session enumeration | 7-session canonical sequence with per-session scope statement |
| §6.5.3 In-project fork management | All forks routed to design-phase channels per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4 |
| §6.5.4 Arc completion criteria | 9-criterion completion gate per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §5 |
| §6.5.5 Each-session opening read pattern | Canonical 7-artifact session-open load discipline per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §6 |
| §6.5.6 Each-session close handoff pattern | Canonical 2-artifact session-close discipline (close handoff + next-session kickoff) per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §7 |
| §6.5.7 Anti-leakage discipline preservation | H_T ↔ H_E substitution-risk discipline per `Phase_7_Meta_Architecture_v1.md` §7 (18 anti-leakage rules); H_T-CP-1 Class 2 substitution-risk surface visibility per `Phase_7_Meta_Architecture_v1.md` §9 |

#### §2.1.2 §2.7 Phase 7 specification

Codify Phase 7 execution discipline referencing canonical substrate. Authoring scope:

| Sub-section | Content |
|---|---|
| §2.7.1 Phase 7 framing | Execution phase; H_T (target harness) build inside H_E (Claude Code CLI execution harness); chicken-and-egg paradox resolution per `Phase_7_Meta_Architecture_v1.md` §1 |
| §2.7.2 Workspace discipline | DP-4 default — Phase 7 runs in a separate Claude Code CLI workspace from this design-phase project workspace; design-phase workspace remains canonical archive + back-flow target |
| §2.7.3 Sub-phase structure | Reference to `Phase_7_Meta_Architecture_v1.md` §10 (7a Bootstrap / 7b Per-axis interior execution / 7c Cross-axis integration / 7d Self-hosting milestones) as canonical Phase 7 internal workflow |
| §2.7.4 Substitution discipline | Reference to `Phase_7_Meta_Architecture_v1.md` §5 (49-entry substitution mapping table) + §7 (anti-leakage rules) as canonical substitution governance |
| §2.7.5 Self-hosting milestone gradient | Reference to `Phase_7_Meta_Architecture_v1.md` §6 (per-primitive retirement gradient) as canonical Phase 7 progression metric |
| §2.7.6 Back-flow routing | Reference to `Phase_7_Kickoff_Prompt.md` §6 back-flow discipline + `Phase_7_Meta_Architecture_v1.md` §10.5.3 back-flow routing aggregate |
| §2.7.7 Class 2 substitution-risk visibility | H_T-CP-1 multi-LLM commitment substitution-risk surface per `Phase_7_Meta_Architecture_v1.md` §9; risk-management discipline preserved at Workflow §2.7 |

#### §2.1.3 §4.1.4.6 amendment per `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md`

Absorb the §4.1.4.6 amendment authored at `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md`. Specifics deferred to substrate inspection at session open.

#### §2.1.4 Any §1–§N amendments arising from absorption discipline

Workflow v1.8 may require §1–§N amendments to maintain global consistency under §6.5 + §2.7 absorption. Examples (non-exhaustive):

- §1 phase enumeration may require Phase 6.5 + Phase 7 reference updates
- §2.6 (Phase 6) may require closure-state notes referencing Phase 6.5 arc
- §3 (checkpoint discipline) may require P6.5-CK or similar checkpoint enumeration if applicable
- §7 fidelity-grammar may require version-citation alignment updates

Authoring scope at session execution discipline (§5).

### §2.2 Out of scope

- IS / AS / CP / OD plan revisions (preserved at v2.2 / v1 / v2.3 / v2.4 canonical revisions)
- ADR / ADD / PRD revisions (cleared at Phase 6 close)
- Spec revisions (preserved at canonical Phase 5 revisions)
- Meta-architecture revisions (`Phase_7_Meta_Architecture_v1.md` filed at Session 4 close; revision scope out-of-session)
- Bootstrap substrate authoring at Claude Code CLI level (Session 6 ε owns)
- Phase 7 Session 1 Entry Directive authoring (Session 7 β owns)
- Implementation in any form (no code authored at this session)
- Stack revisions (Target_Stack_Commitment_v1.md preserved per Session 1 close)

If revision authoring surfaces a question about any of these, route per §6 fork-handling.

### §2.3 Deliverables

Four artifacts filed at session close:

| # | Artifact | Role |
|---|---|---|
| 1 | `Project_Workflow_v1_8.md` | Canonical workflow at v1.8; absorbs §6.5 + §2.7 + §4.1.4.6 + any §1–§N amendments |
| 2 | `Project_Workflow_Revision_log.md` (updated) | Revision log entry for v1.7 → v1.8 promotion |
| 3 | `Phase_6_5_Session_5_Close_Handoff.md` | Session close handoff per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §7 canonical pattern |
| 4 | `Phase_6_5_Session_6_Kickoff.md` | Session 6 (ε — Claude Code CLI bootstrap substrate authoring) entry artifact |

---

## §3 Substrate retrieval

### §3.1 Canonical Phase 6.5 substrate (load first)

| # | Artifact | Path | Role |
|---|---|---|---|
| 1 | `Phase_6_5_Pre_Transition_Arc_Manifest.md` | `/mnt/project/` | Arc framing + sequence context + fork-handling discipline |
| 2 | `Canonical_Substrate_Inventory.md` | `/mnt/project/` | KB navigation anchor; disambiguates canonical vs superseded artifacts |
| 3 | `Phase_6_5_Session_4_Close_Handoff.md` | `/mnt/project/` (after operator push) | Session 4 close record; canonical-substrate carry-forward |
| 4 | `Phase_7_Meta_Architecture_v1.md` | `/mnt/project/` (after operator push) | Session 4 primary deliverable; canonical Phase 7 execution discipline |
| 5 | `Phase_7_Kickoff_Prompt.md` | `/mnt/project/` | Portable kickoff; referenced at Workflow §2.7 |

### §3.2 Workflow predecessor + amendment substrate

| Artifact | Role |
|---|---|
| `Project_Workflow_v1_7.md` | Revision predecessor; v1.7 baseline |
| `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md` | Authored revision-log entry enumerating v1.7 → v1.8 amendment scope |
| `Project_Workflow_Revision_log.md` | Aggregate revision log; updated at this session |

### §3.3 Implementation plan + spec + ADR substrate (referenced from Workflow §2.7)

Per `Phase_7_Meta_Architecture_v1.md` §0 status block predecessor enumeration:

- v2.2 / v1 / v2.3 / v2.4 implementation plans
- CXA v2.1
- IS / AS / CP / OD specs at canonical revisions
- All canonical ADRs (F1–F5 + D1–D6)
- ADD v1.3
- PRD v1.1

Consulted at workflow §2.7 authoring time as needed.

### §3.4 V3 system prompt

Loaded at workspace level. Confidence tagging + source-grounding + anti-fabrication discipline apply. Particularly relevant at §2.7 authoring: Workflow v1.8 §2.7 cites `Phase_7_Meta_Architecture_v1.md` as canonical; cross-referenced sections must resolve byte-exact.

### §3.5 Skill activation

| Skill | Sub-mode | Trigger |
|---|---|---|
| `spec-writer` | Workflow-promotion variant | Workflow revision authoring (v1.7 → v1.8) |
| `implementation-planner` | §8 revision-pass sub-mode | Workflow revision discipline (analog to plan revision-pass authoring) |

---

## §4 Entry-gate verification

At session open, verify:

| # | Check | Verification |
|---|---|---|
| 1 | Phase 6.5 manifest accessible | `project_knowledge_search` returns content |
| 2 | `Phase_6_5_Session_4_Close_Handoff.md` accessible at `/mnt/project/` | `project_knowledge_search` returns content; operator pushed between sessions |
| 3 | `Phase_7_Meta_Architecture_v1.md` accessible at `/mnt/project/` | Same |
| 4 | `Project_Workflow_v1_7.md` accessible | Same |
| 5 | `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md` accessible | Same |
| 6 | `Project_Workflow_Revision_log.md` accessible | Same |
| 7 | `Phase_7_Kickoff_Prompt.md` accessible | Same |
| 8 | No open Class 1 / Class 2 forks from Session 4 (η + θ) | Per `Phase_6_5_Session_4_Close_Handoff.md` §5.1 + §5.2 (no Class 1; 1 Class 2 H_T-CP-1 surface dispositioned within Session 4; non-blocking at Session 5 entry) |

If any entry-gate item fails, halt session open; surface to operator before proceeding.

---

## §5 Session execution discipline

### §5.1 Segmented delivery contract

3–4 segments estimated per Workflow promotion scope:

| Segment | Scope | Approximate output |
|---|---|---|
| 1 | Path_Delta substrate verification + §6.5 + §2.7 + §4.1.4.6 absorption scope confirmation | Substrate read + amendment scope re-verification against current substrate state; operator confirmation menu |
| 2 | §6.5 + §2.7 authoring (substantive content) | Workflow v1.8 §6.5 + §2.7 prose authored |
| 3 | §4.1.4.6 + §1–§N amendments + revision log entry | §4.1.4.6 amendment + global-consistency §1–§N amendments + `Project_Workflow_Revision_log.md` entry |
| 4 | Coherence pass + artifact filing + close handoff + Session 6 kickoff | `Project_Workflow_v1_8.md` filed; this artifact close handoff filed; `Phase_6_5_Session_6_Kickoff.md` filed |

### §5.2 Authoring methodology

Per `spec-writer` SKILL.md workflow-promotion variant + `implementation-planner` SKILL.md §8 revision-pass discipline:

5.2.1 **Substrate-first amendment scope verification.** §6.5 + §2.7 + §4.1.4.6 amendment shapes are pre-declared at `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md`. Segment 1 verifies pre-declared shapes against current substrate state; surfaces any drift as Class 2 fork.

5.2.2 **Change-note discipline.** Workflow v1.8 §0 change-note enumerates predecessor (v1.7) + revision scope + sections preserved verbatim + sections revised + Class 3 informational items.

5.2.3 **Sub-section authoring.** §6.5 + §2.7 sub-sections authored against `Phase_7_Meta_Architecture_v1.md` substrate; cross-references cite section IDs explicitly (e.g., "Workflow §2.7.3 references `Phase_7_Meta_Architecture_v1.md` §10").

5.2.4 **Anti-leakage rule preservation.** H_T-CP-1 Class 2 substitution-risk surface preserved at Workflow §6.5.7 + §2.7.7 per `Phase_6_5_Session_4_Close_Handoff.md` §7.2.2.

5.2.5 **Coherence pass.** End-to-end read at Segment 4; verify §6.5 + §2.7 + §4.1.4.6 absorption consistency + §1–§N amendment consistency + revision log entry alignment.

### §5.3 Operator confirmation cadence

| Boundary | Confirmation form |
|---|---|
| Segment 1 close | Amendment scope verification + Segment 2 entry confirmation |
| Segment 2 close | §6.5 + §2.7 authored content review + Segment 3 entry confirmation |
| Segment 3 close | §4.1.4.6 + §1–§N amendments + revision log entry review + Segment 4 entry confirmation |
| Segment 4 close | Final artifact filing confirmation + Session 6 kickoff readiness |

---

## §6 Fork-handling

### §6.1 Class disposition routing

Per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4 in-project fork management:

| Class | Routing |
|---|---|
| Class 1 (halt-arc) | Halt session; surface to operator; route per Manifest §4.2 |
| Class 2 (operator-decision-blocking) | Surface to operator with options menu; resume after disposition per Manifest §4.3 |
| Class 3 (informational) | Log at session close; route per Manifest §4.4 |

### §6.2 Session 5 specific fork surfaces

| Surface | Trigger | Routing |
|---|---|---|
| Path_Delta amendment scope drift | `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md` declared amendment shape no longer aligns with current substrate (e.g., `Phase_7_Meta_Architecture_v1.md` introduces a §2.7 reference that Path_Delta did not anticipate) | Class 2 — surface to operator; resolve at amendment-scope refinement |
| §6.5 retroactive codification surfaces gap | Phase 6.5 arc execution surfaces a discipline that should be codified at §6.5 but is not pre-declared at Path_Delta | Class 2 — surface to operator; extend §6.5 scope OR defer to Workflow v1.9 |
| §2.7 Phase 7 specification surfaces a Workflow §1–§N inconsistency | Workflow §1 phase enumeration or §3 checkpoint discipline does not align with §2.7 Phase 7 specification | Class 2 — surface to operator; resolve at §1–§N amendment scope |
| Anti-leakage rule preservation surfaces design extension | Preserving H_T-CP-1 Class 2 surface at Workflow §6.5.7 surfaces a discipline that is not yet in `Phase_7_Meta_Architecture_v1.md` | Class 2 — surface to operator; route to `Phase_7_Meta_Architecture_v1.md` revision (out-of-session — would defer) OR scope-down anti-leakage rule preservation |

---

## §7 Exit criteria

Session 5 (γ) closes when:

| # | Criterion |
|---|---|
| 1 | `Project_Workflow_v1_8.md` filed at `/mnt/user-data/outputs/` |
| 2 | `Project_Workflow_Revision_log.md` updated with v1.7 → v1.8 promotion entry |
| 3 | `Phase_6_5_Session_5_Close_Handoff.md` filed |
| 4 | `Phase_6_5_Session_6_Kickoff.md` filed |
| 5 | All Class 1 / Class 2 forks dispositioned with operator decision recorded |
| 6 | §6.5 formal pre-transition arc specification authored at Workflow v1.8 |
| 7 | §2.7 Phase 7 specification authored at Workflow v1.8 |
| 8 | §4.1.4.6 amendment per Path_Delta absorbed at Workflow v1.8 |
| 9 | Any §1–§N global-consistency amendments authored at Workflow v1.8 |
| 10 | Coherence pass verified at Workflow v1.8 §0 change-note + body content |
| 11 | H_T-CP-1 Class 2 substitution-risk surface preservation verified at Workflow §6.5.7 + §2.7.7 |

---

## §8 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_5_Kickoff.md` |
| Status | Filed at Session 4 (η+θ) close 2026-05-15 |
| Phase | Phase 6.5 Session 5 (γ) entry |
| Authoring discipline | Workflow v1.7 §7 fidelity-grammar; `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 session enumeration |
| Predecessor | `Phase_6_5_Session_4_Close_Handoff.md`; `Phase_7_Meta_Architecture_v1.md` (Session 4 η+θ deliverables) |
| Successor (at session close) | `Project_Workflow_v1_8.md`; `Project_Workflow_Revision_log.md` (updated); `Phase_6_5_Session_5_Close_Handoff.md`; `Phase_6_5_Session_6_Kickoff.md` |
| Filing destination | `/mnt/user-data/outputs/Phase_6_5_Session_5_Kickoff.md` → operator pushes to `/mnt/project/` |
| Date | 2026-05-15 |

---

*End of Phase 6.5 Session 5 (γ) Kickoff. Session 5 entry authorized; awaiting operator session open.*

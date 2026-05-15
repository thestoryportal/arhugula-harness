# Phase 6.5 Session 3 Kickoff — F3-02 IS-axis Revision Pass (ζ)

*Session entry artifact for Phase 6.5 Session 3. Loaded as substrate at session open. Authored at Session 2 (α) close; executed in a new session in this same project workspace.*

---

## §1 Session identity

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_3_Kickoff.md` |
| Phase | Phase 6.5 (pre-transition arc) |
| Session number | 3 of 7 |
| Session designator | ζ |
| Session name | F3-02 IS-axis Revision Pass (broadened per OD-S2-1.A) |
| Skill activation | `implementation-planner` SKILL.md in **revision-pass sub-mode** (per SKILL.md §8 invocation when carry-forward absorption requires plan revision) |
| Authoring authority | Operator directive 2026-05-14 (Phase 6.5 arc entry); `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 session enumeration; operator decision OD-S2-1.A (broadened scope per Session 2 close) |
| Predecessor artifact | `Phase_6_5_Session_2_Close_Handoff.md` (Session 2 α close); `Plan_Executability_Audit_v1.md` (Session 2 α deliverable; F3-02 + C3-15 identified as absorption targets) |
| Companion artifact (canonical for entire arc) | `Phase_6_5_Pre_Transition_Arc_Manifest.md`; `Canonical_Substrate_Inventory.md` |
| Successor artifact (at session close) | `Implementation_Plan_Information_Substrate_v2_2.md`; `Phase_6_5_Session_3_Close_Handoff.md`; `Phase_6_5_Session_4_Kickoff.md` |

---

## §2 Session scope

### §2.1 In scope

Broadened per operator decision OD-S2-1.A (Session 2 close). Two absorption targets at a single revision-cycle:

2.1.1 **F3-02 absorption — canonical IS-axis ledger-write site unit.**

| Field | Value |
|---|---|
| Defect | IS plan v2.1 lacks the canonical IS-axis ledger-write site unit cited at OD plan v2.3 U-OD-20 acceptance #11 (`U-IS-NN` placeholder) |
| Surface | F2 ledger-write substrate at the cost-attribution-per-span composition seam |
| Routing | OD plan U-OD-20 references the missing IS unit at acceptance #11 cost-record persistence |
| Closure target | New IS unit (provisional ID: **U-IS-18**) declaring canonical ledger-write site; resolves U-OD-20 acc #11 `U-IS-NN` to `U-IS-18` |

2.1.2 **C3-15 absorption — OD plan §4.5.1 OD→IS citation reconciliation.**

| Field | Value |
|---|---|
| Defect | OD plan §4.5.1 cites non-existent IS spec contracts: `C-IS-13 §13.2`, `C-IS-13 §13.5`, `C-IS-08 §8.4`, `C-IS-14 §14.2` |
| Verification | IS spec v1.2 enumerates only C-IS-01 through C-IS-10; cited contracts do not resolve |
| Edge resolution | Edges resolve at manifest level (U-OD-34 → U-IS-17 terminal aggregate reference); per-citation drift surfaces at OD plan §4.5.1 enumeration |
| Closure target | Two paths available — operator selects at session execution per §6: (i) **remap to canonical IS contracts** at OD plan v2.4 §4.5.1 (corrects citation drift; no IS spec revision); (ii) **extend IS spec to v1.3** with C-IS-13 + C-IS-14 contract declarations + C-IS-08 §8.4 sub-section; absorb at IS plan v2.2 (canonical anchoring; broadens IS spec surface) |

### §2.2 Out of scope

- Stack revisions (Target_Stack_Commitment_v1.md preserved per OD-S2-2.A)
- ADR / ADD / PRD revisions (cleared at Phase 6 close; Class 2 forks route per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4.3 if surfaced)
- AS / CP plan revisions (F2-12 ✅ CLOSED at v2.2 cascade; preserved at v2.3)
- Meta-architecture authoring (Session 4 η owns)
- Workflow v1.8 promotion (Session 5 γ owns)
- Bootstrap substrate authoring (Session 6 ε owns)
- Implementation in any form (no code authored at this session; revision-pass is design-phase only)

### §2.3 Deliverables

Three artifacts filed at session close:

| # | Artifact | Role |
|---|---|---|
| 1 | `Implementation_Plan_Information_Substrate_v2_2.md` | IS plan revised to absorb F3-02 (new canonical ledger-write site unit) + C3-15 (per §6 operator selection: OD plan citation remap or IS spec extension to v1.3) |
| 2 | `Phase_6_5_Session_3_Close_Handoff.md` | Session close handoff per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §7 canonical pattern |
| 3 | `Phase_6_5_Session_4_Kickoff.md` | Session 4 (η — Chicken-and-egg meta-architecture) entry artifact |

Conditional fourth artifact (only if §6 path (ii) selected):

| # | Artifact | Role |
|---|---|---|
| 4 | `Spec_Information_Substrate_v1_3.md` | IS spec extended to v1.3 with C-IS-13 + C-IS-14 contract declarations + C-IS-08 §8.4 sub-section |

---

## §3 Substrate retrieval

### §3.1 Canonical Phase 6.5 substrate (load first)

| # | Artifact | Path | Role |
|---|---|---|---|
| 1 | `Phase_6_5_Pre_Transition_Arc_Manifest.md` | `/mnt/project/` | Arc framing + sequence context + fork-handling discipline |
| 2 | `Canonical_Substrate_Inventory.md` | `/mnt/project/` | KB navigation anchor; disambiguates canonical vs superseded artifacts |
| 3 | `Phase_7_Kickoff_Prompt.md` | `/mnt/project/` | Phase 7 entry framing + back-flow routing |
| 4 | `Plan_Executability_Audit_v1.md` | `/mnt/project/` (after operator push) | **Session 2 α deliverable — F3-02 + C3-15 identified as Session 3 ζ absorption targets** |
| 5 | `Phase_6_5_Session_2_Close_Handoff.md` | `/mnt/project/` (after operator push) | Session 2 close record; OD-S2-1.A + OD-S2-2.A decisions |
| 6 | `Target_Stack_Commitment_v1.md` | `/mnt/project/` | Stack commitment preserved at v1 per OD-S2-2.A |

### §3.2 Implementation plan substrate (Session-3-specific — revision targets + neighbors)

| Plan | Canonical file | Role at Session 3 |
|---|---|---|
| IS axis | `Implementation_Plan_Information_Substrate_v2_1.md` | **Revision target** — revised to v2.2 absorbing F3-02 + C3-15 |
| AS axis | `Implementation_Plan_Action_Surface_v1.md` | Preserved at v1; cross-axis edges to IS unaffected at terminal-aggregate manifest level |
| CP axis | `Implementation_Plan_Control_Plane_v2_3.md` | Preserved at v2.3 (F2-12 ✅ CLOSED cascade); cross-axis edges to IS resolve via U-IS-17 manifest |
| OD axis | `Implementation_Plan_Operational_Discipline_v2_3.md` | Preserved at v2.3 (substrate); §4.5.1 OD→IS citations + U-OD-20 acc #11 `U-IS-NN` placeholder are absorption sites |
| CXA | `Cross_Axis_Composition_Document_v2_1.md` | Preserved at v2.1; 6 OD→IS edges enumerated at §2.3.5 inform absorption reconciliation |

### §3.3 Spec substrate (revision target conditional)

Per Workflow v1.7 §7 use-latest-version discipline:

- `Spec_Information_Substrate_v1.md` (IS spec v1.2) — **conditional revision target** per §6 operator selection (path (ii) extends to v1.3)
- `Spec_Action_Surface_v1.md` (AS spec v1.1) — preserved
- `Spec_Control_Plane_v1_3.md` (CP spec v1.3) — preserved
- `Spec_Operational_Discipline_v1_3.md` (OD spec v1.3) — preserved

### §3.4 ADR substrate (consulted ad-hoc per absorption finding)

Primary references for IS-axis ledger-write site authority:

- **ADR-F2 v1.2** — state-ledger substrate authority; entry shape canonical at IS C-IS-05 § U-IS-07
- **ADR-D1 v1.2** — engine + replay; consumes IS ledger-write substrate at CP plan U-CP-18 (F2 substrate join)
- **ADR-D6 v1.2** — observability + cost-attribution; consumes IS ledger-write substrate at OD plan U-OD-20 (cost-record persistence)

### §3.5 V3 system prompt

Loaded at workspace level. Confidence tagging + source-grounding discipline apply at this session.

### §3.6 Skill activation

`implementation-planner` SKILL.md in **revision-pass sub-mode** per SKILL.md §8:

> Activates in revision-pass mode when a spec revision (v1.x → v1.y) or P6-CK finding requires plan absorption.

Phase 6.5 Session 3 (ζ) revision-pass scope: F3-02 carry-forward absorption + C3-15 citation reconciliation. Single revision-cycle per OD-S2-1.A.

---

## §4 Entry-gate verification

At session open, verify:

| # | Check | Verification |
|---|---|---|
| 1 | Phase 6.5 manifest accessible | `project_knowledge_search` returns content |
| 2 | Session 2 (α) deliverable `Plan_Executability_Audit_v1.md` accessible at `/mnt/project/` | `project_knowledge_search` returns content; operator pushed between sessions |
| 3 | Session 2 (α) close handoff `Phase_6_5_Session_2_Close_Handoff.md` accessible | Same |
| 4 | IS plan v2.1 accessible (revision target) | `project_knowledge_search` returns content |
| 5 | OD plan v2.3 accessible (absorption-site anchor) | Same |
| 6 | CP plan v2.3 + AS plan v1 + CXA v2.1 accessible (cross-axis verification) | Same |
| 7 | IS spec v1.2 accessible (conditional revision target) | Same |
| 8 | No open Class 1 forks from Session 2 | Per `Phase_6_5_Session_2_Close_Handoff.md` §5 (none surfaced) |

If any entry-gate item fails, halt session open; surface to operator before proceeding.

---

## §5 Session execution discipline

### §5.1 Segmented delivery contract

3-segment delivery (revision-pass scope narrower than Session 2 audit; 1 IS plan revision + 1 conditional IS spec revision + 2 close artifacts):

| Segment | Scope | Approximate output |
|---|---|---|
| 1 | F3-02 absorption design + C3-15 path selection | F3-02 unit authoring plan (new U-IS-18 signature surface); C3-15 path selection menu (path (i) OD remap vs path (ii) IS spec v1.3 extension); operator decision recorded |
| 2 | IS plan v2.1 → v2.2 emission (+ conditional IS spec v1.3 emission) | `Implementation_Plan_Information_Substrate_v2_2.md` filed; conditional `Spec_Information_Substrate_v1_3.md` filed per path selection; OD plan citation map authored (if path (i)) or IS spec contract declarations authored (if path (ii)) |
| 3 | Close handoff + Session 4 kickoff authoring | `Phase_6_5_Session_3_Close_Handoff.md` filed; `Phase_6_5_Session_4_Kickoff.md` filed |

Segment 1 is decision-heavy (path selection); Segment 2 is artifact-emission-heavy (1–2 substantive revisions); Segment 3 is close-handoff.

### §5.2 Revision-pass methodology

Per `implementation-planner` SKILL.md §8 revision-pass sub-mode discipline:

5.2.1 **Identify absorption sites.** F3-02: missing canonical IS-axis ledger-write site unit. C3-15: OD plan §4.5.1 citation drift to non-existent IS spec contracts.

5.2.2 **Author absorption design.** F3-02: new U-IS-18 signature surface declaring canonical ledger-write site; signature composes with U-IS-07 entry shape + U-IS-09 chain construction + U-IS-11 append-write contract. C3-15: per operator selection, either OD plan citation remap OR IS spec v1.3 extension.

5.2.3 **Verify cross-axis edge consistency.** New U-IS-18 references at OD plan U-OD-20 acc #11; CP plan unaffected; AS plan unaffected; CXA v2.1 adjacency matrix unchanged at axis granularity (OD → IS edge count may increase from 6 to 7 if U-IS-18 is a new cross-axis target).

5.2.4 **Preserve substrate-version citation discipline** (Workflow v1.7 §7 use-latest-version): IS plan v2.2 cites IS spec at v1.2 or v1.3 per path selection; CP / AS / OD plan citations unchanged.

5.2.5 **Backref reconciliation.** Apply Pattern P2 self-audit at v2.2 emission scope: all `per IS spec v1.X §Y` citations verified against canonical IS spec; all OD plan §4.5.1 citations verified against IS spec contract enumeration.

### §5.3 Operator confirmation cadence

| Boundary | Confirmation form |
|---|---|
| Segment 1 close | C3-15 path selection menu (path (i) OD remap vs path (ii) IS spec v1.3 extension) + Segment 2 entry confirmation |
| Segment 2 close | Revised artifact(s) review + Segment 3 entry confirmation |
| Segment 3 close | Final artifact filing confirmation + Session 4 kickoff readiness |

---

## §6 Fork-handling

### §6.1 Class disposition routing

Per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4 in-project fork management:

| Class | Routing |
|---|---|
| Class 1 (halt-arc) | Halt session; surface to operator; route per Manifest §4.2 |
| Class 2 (operator-decision-blocking) | Surface to operator with options menu; resume after disposition per Manifest §4.3 |
| Class 3 (informational) | Log at session close; route per Manifest §4.4 (Session 6 ε for implementation binding; downstream revision for documentation refinement) |

### §6.2 C3-15 path-selection forks

C3-15 path selection is a Class 2 disposition decision surfaced at Segment 1 close. Two paths:

6.2.1 **Path (i) — OD plan citation remap (recommended).**

| Field | Value |
|---|---|
| Action | Revise OD plan v2.3 → v2.4 §4.5.1 to remap non-existent IS spec contract citations to canonical IS spec v1.2 contracts (C-IS-01 — C-IS-10) |
| Cost | OD plan v2.4 revision; IS spec unchanged at v1.2; no broader-scope ripple |
| Confidence | [HIGH] — edges already resolve at manifest level (U-OD-34 → U-IS-17); per-citation drift is corrective only |
| Recommendation | **Default selection** — minimal-blast-radius revision |

6.2.2 **Path (ii) — IS spec extension to v1.3.**

| Field | Value |
|---|---|
| Action | Extend IS spec v1.2 → v1.3 with new contract declarations (C-IS-13 + C-IS-14) and new sub-section (C-IS-08 §8.4) matching OD plan §4.5.1 citation expectations; absorb at IS plan v2.2 |
| Cost | IS spec revision; IS plan v2.2 cites IS spec v1.3; OD plan preserved at v2.3; broader-scope precedent for IS spec extension |
| Confidence | [MODERATE] — IS spec v1.2 contract enumeration was operator-committed at P5-CK Iteration 2 close; extension warrants justification beyond C3-15 absorption |
| Recommendation | Available if operator judges canonical anchoring at IS spec preferable to OD plan correction |

### §6.3 Default disposition

Audit recommendation: **Path (i)** (OD plan citation remap). Surfaced as the default selection at Segment 1 operator decision menu; operator can override to Path (ii) if rationale warrants.

---

## §7 Exit criteria

Session 3 (ζ) closes when:

| # | Criterion |
|---|---|
| 1 | `Implementation_Plan_Information_Substrate_v2_2.md` filed at `/mnt/user-data/outputs/` |
| 2 | Conditional `Spec_Information_Substrate_v1_3.md` filed at `/mnt/user-data/outputs/` (only if Path (ii) selected) |
| 3 | Conditional `Implementation_Plan_Operational_Discipline_v2_4.md` filed (only if Path (i) selected and OD plan revision authored in-session) — alternatively, OD plan §4.5.1 remap may defer to Session 4+ if cross-axis edge consistency is preserved at v2.2 IS plan emission |
| 4 | `Phase_6_5_Session_3_Close_Handoff.md` filed |
| 5 | `Phase_6_5_Session_4_Kickoff.md` filed |
| 6 | All Class 1 / Class 2 forks dispositioned with operator decision recorded |
| 7 | F3-02 carry-forward absorbed at v2.2 with closure-summary record |
| 8 | C3-15 absorbed per Path (i) or Path (ii) per operator decision |
| 9 | Cross-axis edge consistency preserved (OD → IS edge count updated at CXA v2.1 if U-IS-18 is new cross-axis target) |

---

## §8 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_3_Kickoff.md` |
| Status | Filed at Session 2 (α) close 2026-05-15 |
| Phase | Phase 6.5 Session 3 (ζ) entry |
| Authoring discipline | Workflow v1.7 §7 fidelity-grammar; `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 session enumeration; OD-S2-1.A broadened scope per Session 2 close |
| Predecessor | `Phase_6_5_Session_2_Close_Handoff.md`; `Plan_Executability_Audit_v1.md` (Session 2 α deliverable) |
| Successor (at session close) | `Implementation_Plan_Information_Substrate_v2_2.md`; conditional `Spec_Information_Substrate_v1_3.md`; `Phase_6_5_Session_3_Close_Handoff.md`; `Phase_6_5_Session_4_Kickoff.md` |
| Filing destination | `/mnt/user-data/outputs/Phase_6_5_Session_3_Kickoff.md` → operator pushes to `/mnt/project/` |
| Date | 2026-05-15 |

---

*End of Phase 6.5 Session 3 (ζ) Kickoff. Session 3 entry authorized; awaiting operator session open.*

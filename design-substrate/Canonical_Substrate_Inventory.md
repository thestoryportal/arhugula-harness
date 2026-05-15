# Canonical Substrate Inventory — Project Knowledge Base Hygiene

*Single-source-of-truth navigation artifact for the design-phase project KB at Phase 6 close + Phase 6.5 arc entry. Loaded as substrate by every Phase 6.5 session immediately after the manifest. Authoritative answer to "what is canonical right now."*

---

## §1 Provenance + status

| Field | Value |
|---|---|
| Artifact | `Canonical_Substrate_Inventory.md` |
| Type | KB navigation artifact; canonical-vs-superseded inventory; Phase 6.5 substrate-retrieval anchor |
| Status | **Filed** at design-phase workspace; reference substrate for every Phase 6.5 + Phase 7 session |
| Date | 2026-05-14 |
| Authoring trigger | Operator directive 2026-05-14 (KB hygiene pass before Phase 6.5 Session 1 execution) |
| Predecessor | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` (Phase 6 close) |
| Companion arc artifact | `Phase_6_5_Pre_Transition_Arc_Manifest.md` |
| Maintenance discipline | Updated at each Phase 6.5 session close as new canonical artifacts file |

---

## §2 Purpose

### §2.1 Why this artifact exists

The project KB has accumulated ~75 artifacts across Phases 1–6. Several artifact families have multiple versions in KB (e.g., IS plan v1 + v2.1; CP plan v1 + v2.3; CXA v1 + v2.1; ADR-D1 + ADR-D1_v1_2; etc.). Without disambiguation, `project_knowledge_search` may surface superseded artifacts alongside canonical ones, especially for cross-cutting queries during Phase 6.5 sessions.

This inventory serves three functions:

1. **Canonical declaration.** For every artifact family, name THE canonical version + path.
2. **Superseded mapping.** For superseded versions in KB, name their successor.
3. **Navigation discipline.** Establish that future sessions load this inventory FIRST (after the manifest), so retrieval-time disambiguation has an authoritative anchor.

### §2.2 How to use this artifact

Every Phase 6.5 session opens by loading:

1. `Phase_6_5_Pre_Transition_Arc_Manifest.md` (arc framing)
2. **This artifact** (`Canonical_Substrate_Inventory.md`) — disambiguates retrieval
3. The session's kickoff prompt
4. Session-specific substrate per kickoff §3

If a session-time `project_knowledge_search` returns content from a superseded artifact, the session checks this inventory + uses the canonical successor instead. Halt-and-ask if disambiguation is unclear.

### §2.3 What this artifact is NOT

- NOT a file deletion / archival plan. All artifacts remain in KB; the inventory IS the hygiene.
- NOT a substitute for the manifest or session kickoffs.
- NOT load-bearing for the artifacts themselves (every canonical artifact is self-attesting at its filing footer; this inventory aggregates).

---

## §3 Canonical artifact inventory

### §3.1 Phase 1 — Substrate research

All Phase 1 artifacts are canonical (no revisions); referenced as Phase 1 KB substrate.

| Artifact | Path | Status |
|---|---|---|
| `Production-Grade_Multi-LLM_Agent_Harnesses__2025-2026_Landscape_Map.md` | `/mnt/project/` | Canonical |
| `Agent_Harness_Landscape_and_Thought_Leader_Inventory__2025-2026_Field_Survey.md` | `/mnt/project/` | Canonical |
| `Open-Source_Agent_Harness_Repositories_on_GitHub__Deep_Profiles_of_1_000-Star_Projects.md` | `/mnt/project/` | Canonical |
| `Orchestration_and_Control_Flow__Patterns__Routing__Sub-agents__and_Parallelism.md` | `/mnt/project/` | Canonical (Cluster 1) |
| `Context__Prompts__and_Memory__Deep-Dive_on_Agent_Harness_Infrastructure.md` | `/mnt/project/` | Canonical (Cluster 2) |
| `Tools__Skills__and_Validation__Architecting_the_Deterministic_Outer_Harness_for_LLM_Agents.md` | `/mnt/project/` | Canonical (Cluster 3) |
| `Agent_Harness_Hardening__Observability__Reliability__Security__and_Human-in-the-Loop_Primitives.md` | `/mnt/project/` | Canonical (Cluster 4) |
| `Agent_Harness_Architecture__Deployment_Surfaces__Anthropic_Primitives__and_Foundational_Tradeoffs.md` | `/mnt/project/` | Canonical (Cluster 5) |
| `Pattern_Reference_Catalog_v1_0.md` | `/mnt/project/` | Canonical (v1.0) |

### §3.2 Phase 2 — Persona

| Artifact | Path | Status |
|---|---|---|
| `Persona_Document_v1.md` | `/mnt/project/` | Canonical (v1; no revisions) |

### §3.3 Phase 3a — Foundational ADRs (F-ADRs)

F-ADR filenames do NOT carry version suffixes; content has been updated in-place across revisions per Phase 3a iteration cycles. Current content versions per `PRD_v1_1.md` attestation:

| ADR | File | Current content version | Status |
|---|---|---|---|
| F1 | `ADR-F1.md` | v1.2 | Canonical (Accepted) |
| F2 | `ADR-F2.md` | v1.2 | Canonical (Accepted) |
| F3 | `ADR-F3.md` | v1.1 | Canonical (Accepted) |
| F4 | `ADR-F4.md` | v1.1 | Canonical (Accepted) |
| F5 | `ADR-F5.md` | v1.1 | Canonical (Accepted) |

### §3.4 Phase 3b — Derivative ADRs (D-ADRs)

**Asymmetry to note:** D2 / D3 / D4 / D5 filenames do NOT carry version suffixes (content updated in-place); D1 / D6 have version-suffixed files (`ADR-D1_v1_2.md`, `ADR-D6_v1_2.md`) per F2-12 cascade Step 2 artifact-filing convention.

| ADR | Canonical file | Current content version | Status |
|---|---|---|---|
| D1 | `ADR-D1_v1_2.md` | v1.2 | **Canonical (Proposed; F2-12 cascade Step 2a; promotion to Accepted at operator discretion)** |
| D2 | `ADR-D2.md` | v1.1 | Canonical (Accepted) |
| D3 | `ADR-D3.md` | v1.2 | Canonical (Accepted) |
| D4 | `ADR-D4.md` | v1.1 | Canonical (Accepted) |
| D5 | `ADR-D5.md` | v1.3 | Canonical (Accepted) |
| D6 | `ADR-D6_v1_2.md` | v1.2 | **Canonical (Proposed; F2-12 cascade Step 2b)** |

### §3.5 Phase 3c — Integration verification

| Artifact | Path | Status |
|---|---|---|
| `Integration_Verification_Report.md` | `/mnt/project/` | Canonical (no revisions) |

### §3.6 Phase 3d — Architectural Design Document

| Artifact | Path | Status |
|---|---|---|
| `Architectural_Design_Document_v1_3.md` | `/mnt/project/` | **Canonical (v1.3; post-F2-12 cascade Step 3)** |

### §3.7 Phase 4 — PRD

| Artifact | Path | Status |
|---|---|---|
| `PRD_v1_1.md` | `/mnt/project/` | **Canonical (v1.1; post-F2-12 cascade Step 4 absorbing D1 v1.2 + D6 v1.2)** |

### §3.8 Phase 5 — Specifications

**Asymmetry to note:** CP and OD spec filenames carry `_v1_3` version suffix (post-F2-12 cascade); IS, AS, and top-level cross-axis composition spec filenames do NOT carry version suffixes (content updated in-place across pre-cascade iterations).

| Spec | Canonical file | Current content version | Status |
|---|---|---|---|
| Information Substrate | `Spec_Information_Substrate_v1.md` | v1.2 | Canonical (P5-CK cleared; pre-cascade; no v1.3 cascade) |
| Action Surface | `Spec_Action_Surface_v1.md` | v1.1 | Canonical (P5-CK cleared) |
| Control Plane | `Spec_Control_Plane_v1_3.md` | v1.3 | **Canonical (post-F2-12 cascade Step 5a)** |
| Operational Discipline | `Spec_Operational_Discipline_v1_3.md` | v1.3 | **Canonical (post-F2-12 cascade Step 5b)** |
| Cross-axis composition (top-level) | `Specification_v1.md` | v1.1 | Canonical (no cascade revision) |

### §3.9 Phase 6 — Implementation Plans

| Plan | Canonical file | Current content version | Status |
|---|---|---|---|
| Information Substrate plan | `Implementation_Plan_Information_Substrate_v2_1.md` | v2.1 | Canonical (post-P6-CK Iter 1 + Iter 2 revision passes; no Iter 3 or Iter 4 finding) |
| Action Surface plan | `Implementation_Plan_Action_Surface_v1.md` | v1 | Canonical (no findings across all P6-CK iterations) |
| Control Plane plan | `Implementation_Plan_Control_Plane_v2_3.md` | v2.3 | **Canonical (post-Iter 4 revision-cycle; absorbed F2-01 + F2-02 + F2-03)** |
| Operational Discipline plan | `Implementation_Plan_Operational_Discipline_v2_3.md` | v2.3 | **Canonical (post-Iter 4 revision-cycle; absorbed F1-01 + F2-04 + F3-01 + F3-02 acknowledged-deferred)** |
| Cross-Axis Composition Document | `Cross_Axis_Composition_Document_v2_1.md` | v2.1 | Canonical (post-Iter 2 revision; no Iter 3 or Iter 4 finding) |

### §3.10 F2-12 cascade artifacts (cross-phase substrate)

All F2-12 cascade artifacts are canonical (cascade closed at `F2-12_Closure_Declaration.md`):

| Artifact | Path | Role |
|---|---|---|
| `F2-12_Cascade_Entry_Deferral_Note.md` | `/mnt/project/` | Pre-cascade scoping artifact |
| `F2-12_Council_Deliberation_Output.md` | `/mnt/project/` | Cascade Step 1 (council deliberation) |
| `F2-12_Closure_Path_Execution_Kickoff.md` | `/mnt/project/` | Cascade kickoff (Step 1) |
| `F2-12_Closure_Declaration.md` | `/mnt/project/` | Cascade close record (Step 6 close) |

### §3.11 Adversarial reviews + checkpoint close handoffs

Adversarial reviews are canonical per-iteration. Each iteration's review is its own record; not superseded by subsequent iterations.

| Phase | Reviews + close handoffs in KB | Canonical status |
|---|---|---|
| P3a-CK | `Adversarial_Review_3a.md` + `Adversarial_Review_3a_iter2.md` + `Adversarial_Review_3a_iter3.md` + `P3a_CK_Proposing_Findings_Resolution.md` + `P3a_CK_Path_Status_Snapshot.md` + `Step_A_Enumeration_Output.md` + `P3a-CK_Final_Clearance_Audit.md` + `Adv2_Revision_Log.md` + `Adv2_Iter3_Revision_Log.md` | Canonical per-iteration |
| P3-CK | `Adversarial_Review_3.md` + `Adversarial_Review_3_iter2.md` + `Adversarial_Review_3_iter3.md` + `P3-CK_iter2_Entry_Handoff.md` + `P3-CK_iter3_Entry_Handoff.md` | Canonical per-iteration |
| P3c-CK | `Adversarial_Review_3c.md` + `Adversarial_Review_3c_iter2.md` + `Adversarial_Review_3c_iter3.md` + `P3c-CK_Final_Clearance_Audit.md` | Canonical per-iteration |
| P5-CK | `Adversarial_Review_5.md` + `Adversarial_Review_5_iter2.md` + `P5-CK_Iteration_1_Close_Handoff.md` + `P5-CK_Iteration_1_Revision_Pass_Close_Handoff.md` + `P5-CK_Iteration_2_Close_Handoff.md` + `P5-CK_Iteration_2_Revision_Pass_Close_Handoff.md` | Canonical per-iteration |
| P6-CK | `Adversarial_Review_6.md` + `Adversarial_Review_6_iter2.md` + `Adversarial_Review_6_iter4.md` + `P6-CK_Iteration_1_Close_Handoff.md` + `P6-CK_Iter1_Revision_Cycle_Close_Handoff.md` + `P6-CK_Iteration_2_Ceiling_Disposition.md` + `P6-CK_Iteration_4_Entry_Handoff.md` + `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` | Canonical per-iteration |

**Note: `Adversarial_Review_6_iter3.md` is NOT in KB.** This may be a filing omission OR Iter 3 was an entry-gate iteration without a separate review file. Verify against `P6-CK_Iteration_2_Ceiling_Disposition.md` substrate at session-time need.

### §3.12 Entry handoffs + transition artifacts

| Artifact | Path | Status |
|---|---|---|
| `Phase_4_Entry_Handoff.md` | `/mnt/project/` | Canonical |
| `Phase_5_Entry_Handoff.md` | `/mnt/project/` | Canonical |
| `Phase_5_Specification_Authoring_Close_Handoff.md` | `/mnt/project/` | Canonical |
| `Phase_6_Entry_Handoff.md` | `/mnt/project/` | Canonical |
| `Phase_6_Close_Handoff.md` | `/mnt/project/` | Canonical |

### §3.13 Workflow + revision logs

| Artifact | Path | Status |
|---|---|---|
| `Project_Workflow_v1_7.md` | `/mnt/project/` | **Canonical (workflow at design-phase close)** |
| `Project_Workflow_Revision_log.md` | `/mnt/project/` | Canonical (cumulative revision history) |
| `Path_Delta_Workflow_v1_6_to_v1_7_Revision_Log_Entry.md` | `/mnt/project/` | Canonical |
| `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md` | `/mnt/project/` | **Canonical; v1.8 amendment proposed (operator-discretion filing of v1.8 itself; non-blocking)** |
| `Iter-3_Path_C_Disposition_Cascade_Sequencing_Note.md` | `/mnt/project/` | Canonical (independent route artifact) |

### §3.14 Governance substrate (this session's filings)

| Artifact | Path | Status |
|---|---|---|
| `Governance_Substrate_Propagation_Note_F1-01.md` | `/mnt/project/` | **Canonical (F1-01 §1.5 → §14.5.1 citation correction propagation record)** |

### §3.15 Phase 7 + Phase 6.5 artifacts

| Artifact | Current path | Status |
|---|---|---|
| `Phase_7_Kickoff_Prompt.md` | `/mnt/user-data/outputs/` | **Pending push** (filed at outputs; not yet in `/mnt/project/`) |
| `Phase_6_5_Pre_Transition_Arc_Manifest.md` | `/mnt/user-data/outputs/` | **Pending push** |
| `Phase_6_5_Session_1_Kickoff.md` | `/mnt/user-data/outputs/` | **Pending push** |
| `Canonical_Substrate_Inventory.md` (THIS artifact) | `/mnt/user-data/outputs/` | **Pending push** at filing |

---

## §4 Superseded artifacts in KB (with successor pointers)

Superseded artifacts remain in KB for traceability. Future retrieval should disambiguate using this table.

| Superseded artifact | Path | Successor | Successor path | Reason |
|---|---|---|---|---|
| `Implementation_Plan_Information_Substrate_v1.md` | `/mnt/project/` | `Implementation_Plan_Information_Substrate_v2_1.md` | `/mnt/project/` | P6-CK Iter 1 + Iter 2 revision passes (F2-IS-01 + F1-IS-01 absorbed at v2; F1-IS-02 absorbed at v2.1) |
| `Implementation_Plan_Control_Plane_v1.md` | `/mnt/project/` | `Implementation_Plan_Control_Plane_v2_3.md` | `/mnt/project/` | P6-CK Iter 1 + Iter 2 + F2-12 cascade Step 6a + Iter 4 revision-cycle |
| `Implementation_Plan_Operational_Discipline_v1.md` | `/mnt/project/` | `Implementation_Plan_Operational_Discipline_v2_3.md` | `/mnt/project/` | P6-CK Iter 1 + Iter 2 + F2-12 cascade Step 6b + Iter 4 revision-cycle |
| `Cross_Axis_Composition_Document_v1.md` | `/mnt/project/` | `Cross_Axis_Composition_Document_v2_1.md` | `/mnt/project/` | P6-CK Iter 1 + Iter 2 revision passes |

### §4.1 Intermediate revisions NOT in KB

The following intermediate revisions exist in the project revision history but are NOT in KB (presumably cleaned up during prior between-session pushes):

| Family | Intermediate revisions not in KB | Reason |
|---|---|---|
| IS plan | v2 (intermediate between v1 and v2.1) | Cleaned during Iter 2 close |
| CP plan | v2 + v2.1 + v2.2 (intermediates between v1 and v2.3) | Cleaned during respective iteration closes; F2-12 cascade preserved only v2.2 baseline transiently |
| OD plan | v2 + v2.1 + v2.2 (intermediates) | Same as CP plan |
| CXA composition document | v2 (intermediate between v1 and v2.1) | Cleaned during Iter 2 close |

The intermediates can be reconstructed from revision-cycle close handoffs + the canonical successor's §0 change-note if needed. NO action required unless a specific historical reconstruction is needed.

### §4.2 ADR / Spec / ADD / PRD superseded versions

No superseded ADR / Spec / ADD / PRD files are in KB. F-ADR + D2/D3/D4/D5 content updates happened in-place (single file per ADR; revision history at ADR Status block). D1/D6 v1.2 are separate files (no v1 / v1.1 versions in KB). Specs at IS/AS/top-level updated in-place; CP/OD spec v1.3 separate files (no v1 / v1.1 / v1.2 in KB). ADD only at v1.3. PRD only at v1.1.

---

## §5 Filename version-anchor patterns + asymmetries

Three filename conventions coexist in KB:

| Pattern | Examples | Rationale |
|---|---|---|
| **Version-suffixed file per revision** | `ADR-D1_v1_2.md`, `ADR-D6_v1_2.md`, `Spec_Control_Plane_v1_3.md`, `Spec_Operational_Discipline_v1_3.md`, `Architectural_Design_Document_v1_3.md`, `PRD_v1_1.md`, `Implementation_Plan_*_v{N}_{M}.md`, `Cross_Axis_Composition_Document_v{N}_{M}.md`, `Project_Workflow_v1_{N}.md`, `Pattern_Reference_Catalog_v1_0.md` | F2-12 cascade convention + Phase 6 plan revision convention + workflow versioning |
| **No version in filename; content versions in-place** | `ADR-F1.md` through `ADR-F5.md`, `ADR-D2.md` / `D3.md` / `D4.md` / `D5.md`, `Spec_Information_Substrate_v1.md`, `Spec_Action_Surface_v1.md`, `Specification_v1.md`, `Persona_Document_v1.md` | Pre-cascade revision discipline (content updated in-place at iteration close; Status block records revision history) |
| **Per-iteration artifact (no revision)** | All `Adversarial_Review_*.md`, all close handoffs, all entry handoffs | Per-iteration records; not subject to revision |

The asymmetry between version-suffixed-file vs in-place-revision is historical (cascade convention emerged at F2-12 cascade Step 2). New filings from Phase 6.5 forward SHOULD use version-suffixed-file convention to maintain transparency at retrieval time.

---

## §6 Hygiene recommendations

### §6.1 No file deletions or moves

KB hygiene at Phase 6.5 entry does NOT require any file deletions or moves. Recommendation: **leave all artifacts in place**. The inventory IS the hygiene.

Rationale:
- All artifacts (canonical + superseded) are referenced from adversarial reviews + close handoffs + revision logs; removal breaks traceability
- `project_knowledge_search` retrieval ambiguity is mitigated by every session loading this inventory at session open
- Storage cost is negligible

### §6.2 Load discipline going forward

Each Phase 6.5 session loads at session open:

1. `Phase_6_5_Pre_Transition_Arc_Manifest.md`
2. **This inventory** (`Canonical_Substrate_Inventory.md`)
3. The session's kickoff prompt
4. Session-specific substrate per kickoff §3

Sessions also load (lazily, per session need):
- Adversarial reviews + close handoffs for context on prior iterations
- Canonical artifacts per §3 of this inventory

### §6.3 Update discipline at each session close

This inventory is updated at every Phase 6.5 session close to reflect new canonical artifacts:

| Phase 6.5 session | Expected inventory update at close |
|---|---|
| Session 1 (δ) | Add `Target_Stack_Commitment_v1.md` to canonical inventory |
| Session 2 (α) | Add `Plan_Executability_Audit_v1.md` to canonical inventory |
| Session 3 (ζ) | Add `Implementation_Plan_Information_Substrate_v2_2.md` to canonical inventory (supersedes v2.1) + `Phase_6_5_Session_3_F3-02_Resolution_Close_Handoff.md` |
| Session 4 (η + θ) | Add `Phase_7_Meta_Architecture_v1.md` to canonical inventory |
| Session 5 (γ) | Add `Project_Workflow_v1_8.md` to canonical inventory (supersedes v1.7) + revision log update |
| Session 6 (ε) | Add `Phase_7_Bootstrap_Substrate_v1/` directory to canonical inventory |
| Session 7 (β) | Add `Phase_7_Session_1_Entry_Directive.md` to canonical inventory + final handoff package |

The session close-handoff template should include an "Inventory update" sub-section listing the additions.

### §6.4 Anti-fabrication discipline at retrieval

Per V3 system prompt + memory edit #7: NEVER cite a version or path that cannot be verified against this inventory at session-time. If a retrieval surfaces content with an apparent version that does not match this inventory, halt-and-ask.

---

## §7 Forward usage discipline

### §7.1 Inventory load at every session open

Phase 6.5 + Phase 7 sessions: load this inventory immediately after the manifest. Without the inventory, retrieval-time disambiguation depends on the session agent's training-time priors — which is exactly the failure mode the inventory exists to prevent.

### §7.2 Disambiguation pattern at session-time retrieval

When `project_knowledge_search` returns content that may be from a superseded artifact:

| Signal | Action |
|---|---|
| Result references v1 plan content but session is on Phase 6.5 / Phase 7 work | Cross-check this inventory §4; use canonical successor |
| Result references intermediate revision (v2 / v2.1 / v2.2 for CP/OD plans) | Intermediate revisions NOT in KB; canonical is v2.3 |
| Result references ADR-D1 or ADR-D6 without version suffix | Likely fabrication or training-time content; canonical is `_v1_2.md` files |
| Result version disagrees with this inventory | Halt; surface to operator |

### §7.3 New artifact filing discipline

New artifacts filed at Phase 6.5 sessions:

- USE version-suffixed filenames (e.g., `Target_Stack_Commitment_v1.md`, `Phase_7_Meta_Architecture_v1.md`)
- ADD to this inventory at session close
- File at `/mnt/user-data/outputs/` first; push to `/mnt/project/` between sessions
- Reference in this inventory marked **Pending push** until `/mnt/project/` push confirmed

---

## §8 Filing footer

| Field | Value |
|---|---|
| Artifact | `Canonical_Substrate_Inventory.md` |
| Status | Filed at design-phase workspace |
| Phase | Phase 6 close → Phase 6.5 arc entry (KB hygiene anchor) |
| Authoring discipline | Operator directive 2026-05-14 (KB hygiene pass) |
| Predecessor | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` |
| Companion arc artifact | `Phase_6_5_Pre_Transition_Arc_Manifest.md` |
| Successor | Updated at every Phase 6.5 session close per §6.3 |
| Filing destination | `/mnt/user-data/outputs/Canonical_Substrate_Inventory.md` |
| Date | 2026-05-14 |

---

*End of Canonical Substrate Inventory. Load this artifact at every Phase 6.5 + Phase 7 session opening, immediately after the manifest. Update at every session close per §6.3 discipline.*

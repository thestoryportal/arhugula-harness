# Phase 7 Workspace Design Substrate Manifest — v1

*Specification for transferring all design-phase markdown artifacts to the new Claude Code CLI workspace. Resolves the cross-workspace reference infeasibility surfaced by operator directive 2026-05-15: Claude Code CLI cannot access files in the design-phase Claude.ai project knowledge base; all context must be locally co-resident in the bootstrap workspace.*

*Companion to `Phase_7_Workspace_Bootstrap_Runbook_v1.md`. Insert §8.1 transfer procedure between Runbook §3.5 and §3.6.*

---

## 1. Problem Statement

1.1 Claude Code CLI operating in the new workspace cannot access files in the design-phase Claude.ai project knowledge base. Cross-workspace reference (as currently declared at workspace root `CLAUDE.md` §2) is not functionally available.

1.2 Consequence: every design-phase markdown artifact cited by the 11 bootstrap artifacts MUST be physically present at the new workspace. Cross-workspace reference must be reinterpreted as **local filesystem reference within the bootstrap workspace**.

1.3 This specification enumerates every required markdown file, classifies each by load-bearing role, and specifies the target path in the workspace.

---

## 2. Decision Summary

### 2.1 Directory placement decision

**Decision:** Create a top-level `design-substrate/` directory at the workspace root. Place all design-phase markdown artifacts inside it, flat (no further subdirectories within `design-substrate/` for operative substrate; one optional `archive/` subdirectory for historical context).

### 2.2 Rationale

| Alternative | Cost | Selected? |
|---|---|---|
| Flat at workspace root (all 30+ design files alongside source folders) | Workspace root cluttered with ~40 markdown files; mingles design reference with source layout | No |
| `design-substrate/` subdirectory, flat within | Adds one Glob/Read indirection for Claude Code; preserves clean workspace root | **Yes** |
| Hierarchical (`design-substrate/adrs/`, `design-substrate/plans/`, etc.) | Citation resolution requires per-citation path knowledge; fragile | No |
| Embed in `.claude/` directory | Conflates Claude Code config with design substrate; semantically wrong | No |

### 2.3 Citation resolution mechanism

Bootstrap artifacts cite design files by filename only (e.g., `per Spec_Information_Substrate_v1.md §X`), not by path. Claude Code resolves the citation via either:

| Mechanism | Operation |
|---|---|
| Direct path attempt | `Read('design-substrate/<filename>')` |
| Glob fallback | `Glob('**/<filename>')` then `Read` on result |

Both succeed when files exist at `design-substrate/`. No bootstrap artifact modification required.

### 2.4 Quantitative summary

| Category | Count | Target location |
|---|---|---|
| A — Operative (must be present) | 29 files | `design-substrate/` (flat) |
| B — Closure records (must be present) | 3 files | `design-substrate/` (flat) |
| C — Historical context (optional) | ~26 files | `design-substrate/archive/` |
| D — Not transferred | ~30+ files | (omit) |
| **Total transferred (mandatory)** | **32 files** | `design-substrate/` |

---

## 3. Category A — Operative Design Substrate (MUST Be Present)

These files are cited from bootstrap CLAUDE.md / SKILL.md / Sub-Agent Boundary Spec / Entry Directive at sites where Claude Code will need to read them during Phase 7 execution.

### 3.1 Architectural Decision Records (11 files)

| # | Source filename at design-phase `/mnt/project/` | Canonical version | Target path |
|---|---|---|---|
| A.1 | `ADR-F1.md` | v1.2 (internal) | `design-substrate/ADR-F1.md` |
| A.2 | `ADR-F2.md` | v1.2 (internal) | `design-substrate/ADR-F2.md` |
| A.3 | `ADR-F3.md` | v1.1 (internal) | `design-substrate/ADR-F3.md` |
| A.4 | `ADR-F4.md` | v1.1 (internal) | `design-substrate/ADR-F4.md` |
| A.5 | `ADR-F5.md` | v1.1 (internal) | `design-substrate/ADR-F5.md` |
| A.6 | `ADR-D1_v1_2.md` | v1.2 (in filename) | `design-substrate/ADR-D1_v1_2.md` |
| A.7 | `ADR-D2.md` | v1.1 (internal) | `design-substrate/ADR-D2.md` |
| A.8 | `ADR-D3.md` | v1.2 (internal) | `design-substrate/ADR-D3.md` |
| A.9 | `ADR-D4.md` | v1.1 (internal) | `design-substrate/ADR-D4.md` |
| A.10 | `ADR-D5.md` | v1.3 (internal) | `design-substrate/ADR-D5.md` |
| A.11 | `ADR-D6_v1_2.md` | v1.2 (in filename) | `design-substrate/ADR-D6_v1_2.md` |

### 3.2 ADR consolidation + product requirements (2 files)

| # | Source filename | Target path |
|---|---|---|
| A.12 | `Architectural_Design_Document_v1_3.md` (ADD v1.3) | `design-substrate/Architectural_Design_Document_v1_3.md` |
| A.13 | `PRD_v1_1.md` (PRD v1.1) | `design-substrate/PRD_v1_1.md` |

### 3.3 Per-axis specifications (4 files)

| # | Source filename | Canonical version | Target path |
|---|---|---|---|
| A.14 | `Spec_Information_Substrate_v1.md` | v1.2 (internal; per ADD v1.3 attestation) | `design-substrate/Spec_Information_Substrate_v1.md` |
| A.15 | `Spec_Action_Surface_v1.md` | v1.1 (internal) | `design-substrate/Spec_Action_Surface_v1.md` |
| A.16 | `Spec_Control_Plane_v1_3.md` | v1.3 | `design-substrate/Spec_Control_Plane_v1_3.md` |
| A.17 | `Spec_Operational_Discipline_v1_3.md` | v1.3 | `design-substrate/Spec_Operational_Discipline_v1_3.md` |

### 3.4 Per-axis implementation plans (4 files)

| # | Source filename | Canonical version | Target path |
|---|---|---|---|
| A.18 | `Implementation_Plan_Information_Substrate_v2_2.md` | v2.2 | `design-substrate/Implementation_Plan_Information_Substrate_v2_2.md` |
| A.19 | `Implementation_Plan_Action_Surface_v1.md` | v1 | `design-substrate/Implementation_Plan_Action_Surface_v1.md` |
| A.20 | `Implementation_Plan_Control_Plane_v2_3.md` | v2.3 | `design-substrate/Implementation_Plan_Control_Plane_v2_3.md` |
| A.21 | `Implementation_Plan_Operational_Discipline_v2_4.md` | v2.4 | `design-substrate/Implementation_Plan_Operational_Discipline_v2_4.md` |

### 3.5 Cross-axis composition (1 file)

| # | Source filename | Target path |
|---|---|---|
| A.22 | `Cross_Axis_Composition_Document_v2_1.md` | `design-substrate/Cross_Axis_Composition_Document_v2_1.md` |

### 3.6 Phase 7 governance substrate (4 files)

| # | Source filename | Role | Target path |
|---|---|---|---|
| A.23 | `Project_Workflow_v1_8.md` | Workflow canonical; §2.7 Phase 7 internal workflow; §2.7.6 back-flow routing canonical | `design-substrate/Project_Workflow_v1_8.md` |
| A.24 | `Phase_7_Meta_Architecture_v1.md` | Substitution mapping (49 entries) + anti-leakage discipline (17+3 rules) + sub-phase enumeration (§10.1–§10.4) | `design-substrate/Phase_7_Meta_Architecture_v1.md` |
| A.25 | `Target_Stack_Commitment_v1.md` | Stack discipline (Python 3.12+ / Pydantic v2 / uv / etc.) | `design-substrate/Target_Stack_Commitment_v1.md` |
| A.26 | `Plan_Executability_Audit_v1.md` | Framework-pull discipline (forbidden libraries enumeration) | `design-substrate/Plan_Executability_Audit_v1.md` |

### 3.7 Persona + navigation (2 files)

| # | Source filename | Role | Target path |
|---|---|---|---|
| A.27 | `Persona_Document_v1.md` | User persona; referenced from ADD v1.3 §1; informs HITL viability assessments per Meta-Architecture §10.5.2 | `design-substrate/Persona_Document_v1.md` |
| A.28 | `Canonical_Substrate_Inventory.md` | KB navigation anchor; cited from `phase-7-back-flow-routing/SKILL.md` §7 + multiple Phase 7-specific skills | `design-substrate/Canonical_Substrate_Inventory.md` |

### 3.8 Phase 7 portable kickoff (1 file)

| # | Source filename | Role | Target path |
|---|---|---|---|
| A.29 | `Phase_7_Kickoff_Prompt.md` | Portable Phase 7 kickoff; cited from `phase-7-back-flow-routing/SKILL.md` §7 "§6 back-flow discipline reference"; legacy framing superseded for Session 1 by the Entry Directive | `design-substrate/Phase_7_Kickoff_Prompt.md` |

**Category A total: 29 files.**

---

## 4. Category B — Closure Records (MUST Be Present)

### 4.1 F2-12 cascade closure (1 file)

| # | Source filename | Citation site | Target path |
|---|---|---|---|
| B.1 | `F2-12_Closure_Declaration.md` | `harness-cp/CLAUDE.md` §5.2 "Open carry-forwards at CP axis entry" row F2-12 cascade Step 6a; `harness-od/CLAUDE.md` §5.2 row F2-12 cascade Step 6b | `design-substrate/F2-12_Closure_Declaration.md` |

### 4.2 Phase 6.5 arc framing (1 file)

| # | Source filename | Citation site | Target path |
|---|---|---|---|
| B.2 | `Phase_6_5_Pre_Transition_Arc_Manifest.md` | Multiple Phase 7-specific SKILL.md files (`phase-7-back-flow-routing/SKILL.md` §7; `phase-7-cross-axis-composition/SKILL.md` §1.3); workspace root `CLAUDE.md` §9; Entry Directive §2.2.6 | `design-substrate/Phase_6_5_Pre_Transition_Arc_Manifest.md` |

### 4.3 Phase 6.5 arc closure record (1 file)

| # | Source filename | Citation site | Target path |
|---|---|---|---|
| B.3 | `Phase_6_5_Session_7_Close_Handoff.md` | Entry Directive §3 entry-gate criterion 7 ("No open Class 1/Class 2 forks from Phase 6.5 arc close — verified at `Phase_6_5_Session_7_Close_Handoff.md` §[arc closure status]") | `design-substrate/Phase_6_5_Session_7_Close_Handoff.md` |

**Category B total: 3 files.**

---

## 5. Category C — Historical Context (OPTIONAL Transfer)

These files may be referenced if a fork surfaces during Phase 7 that requires investigation of upstream session history or design-phase decision rationale. Not required for routine atomic unit landings.

### 5.1 Phase 6.5 session-level artifacts (13 files)

| Sub-category | Files |
|---|---|
| Phase 6.5 Session close handoffs (Sessions 1–6) | `Phase_6_5_Session_1_Close_Handoff.md` through `Phase_6_5_Session_6_Close_Handoff.md` (6 files) |
| Phase 6.5 Session kickoff prompts (Sessions 1–7) | `Phase_6_5_Session_1_Kickoff.md` through `Phase_6_5_Session_7_Kickoff.md` (7 files; Session 7 kickoff retained as substrate for fork-resolution scenarios that reference its scope decisions) |

**Sub-total:** 6 + 7 = 13 files.

### 5.2 F2-12 cascade history (3 files)

| File | Role |
|---|---|
| `F2-12_Cascade_Entry_Deferral_Note.md` | Initial deferral record |
| `F2-12_Closure_Path_Execution_Kickoff.md` | Closure path execution kickoff |
| `F2-12_Council_Deliberation_Output.md` | Phase 3a/3b council record |

### 5.3 Workflow revision history (2 files)

| File | Role |
|---|---|
| `Path_Delta_Workflow_v1_6_to_v1_7_Revision_Log_Entry.md` | Earlier workflow revision |
| `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md` | Most recent workflow revision; routable from Workflow v1.8 §[revision log] |

### 5.4 Phase boundary handoffs (5 files)

| File | Role |
|---|---|
| `Phase_4_Entry_Handoff.md` | Phase 4 PRD authoring entry |
| `Phase_5_Entry_Handoff.md` | Phase 5 spec authoring entry |
| `Phase_5_Specification_Authoring_Close_Handoff.md` | Phase 5 close |
| `Phase_6_Entry_Handoff.md` | Phase 6 plan authoring entry |
| `Phase_6_Close_Handoff.md` | Phase 6 close |

### 5.5 Integration verification + propagation notes (2 files)

| File | Role |
|---|---|
| `Integration_Verification_Report.md` | Phase 3c cross-axis integration verification clearance |
| `Governance_Substrate_Propagation_Note_F1-01.md` | F1-01 governance propagation record |

### 5.6 Disposition + sequencing notes (1 file)

| File | Role |
|---|---|
| `Iter-3_Path_C_Disposition_Cascade_Sequencing_Note.md` | Iter-3 path disposition record |

**Category C total: 26 files (operator-discretion subset transfer).**

**Target path for any Category C file transferred:** `design-substrate/archive/<filename>`.

---

## 6. Category D — NOT Transferred

These files are explicitly out of scope for transfer to the bootstrap workspace.

### 6.1 Substrate research deliverables (Phase 1 inputs, 8 files)

```
- Agent_Harness_Architecture__Deployment_Surfaces__Anthropic_Primitives__and_Foundational_Tradeoffs.md
- Agent_Harness_Hardening__Observability__Reliability__Security__and_Human-in-the-Loop_Primitives.md
- Agent_Harness_Landscape_and_Thought_Leader_Inventory__2025-2026_Field_Survey.md
- Context__Prompts__and_Memory__Deep-Dive_on_Agent_Harness_Infrastructure.md
- Open-Source_Agent_Harness_Repositories_on_GitHub__Deep_Profiles_of_1_000-Star_Projects.md
- Orchestration_and_Control_Flow__Patterns__Routing__Sub-agents__and_Parallelism.md
- Production-Grade_Multi-LLM_Agent_Harnesses__2025-2026_Landscape_Map.md
- Tools__Skills__and_Validation__Architecting_the_Deterministic_Outer_Harness_for_LLM_Agents.md
```

**Rationale:** Phase 1 substrate research informed Phase 2 persona surfacing + Phase 3 ADR authoring. Decisions encoded in ADRs / ADD / PRD / specs / plans. Research substrate adds no operative information at Phase 7 execution.

### 6.2 Superseded artifact versions

| Superseded file | Replaced by |
|---|---|
| `Project_Workflow_v1_7.md` | `Project_Workflow_v1_8.md` |
| `Implementation_Plan_Information_Substrate_v1.md` + `_v2_1.md` | `Implementation_Plan_Information_Substrate_v2_2.md` |
| `Implementation_Plan_Operational_Discipline_v1.md` + `_v2_3.md` | `Implementation_Plan_Operational_Discipline_v2_4.md` |
| `Implementation_Plan_Control_Plane_v1.md` | `Implementation_Plan_Control_Plane_v2_3.md` |
| `Cross_Axis_Composition_Document_v1.md` | `Cross_Axis_Composition_Document_v2_1.md` |
| `Specification_v1.md` (composite) | Per-axis specs |
| `Project_Workflow_Revision_log.md` | `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md` (later) |

### 6.3 Review process artifacts

```
- Adversarial_Review_3.md, _3_iter2.md, _3_iter3.md
- Adversarial_Review_3a.md, _3a_iter2.md, _3a_iter3.md
- Adversarial_Review_3c.md, _3c_iter2.md, _3c_iter3.md
- Adversarial_Review_5.md, _5_iter2.md
- Adversarial_Review_6.md, _6_iter2.md, _6_iter4.md
- Adv2_Revision_Log.md, Adv2_Iter3_Revision_Log.md
- P3-CK_iter2_Entry_Handoff.md, _iter3_Entry_Handoff.md
- P3a_CK_Path_Status_Snapshot.md, P3a_CK_Proposing_Findings_Resolution.md, P3a-CK_Final_Clearance_Audit.md
- P3c-CK_Final_Clearance_Audit.md
- P5-CK_Iteration_1_Close_Handoff.md, _Iteration_1_Revision_Pass_Close_Handoff.md
- P5-CK_Iteration_2_Close_Handoff.md, _Iteration_2_Revision_Pass_Close_Handoff.md
- P6-CK_Iter1_Revision_Cycle_Close_Handoff.md, _Iter4_Revision_Cycle_Close_Handoff.md
- P6-CK_Iteration_1_Close_Handoff.md, _Iteration_2_Ceiling_Disposition.md, _Iteration_4_Entry_Handoff.md
- Step_A_Enumeration_Output.md
```

**Rationale:** Adversarial review iterations cleared the canonical artifacts. Findings absorbed into the canonical versions. Review trail is archival; not load-bearing for Phase 7 execution.

### 6.4 Intermediate substrate

| File | Reason omitted |
|---|---|
| `Pattern_Reference_Catalog_v1_0.md` | Phase 1 pattern research; consumed during Phase 3a ADR authoring; archival |

**Category D total: ~30+ files. None transferred.**

---

## 7. Workspace Layout (Post-Transfer)

### 7.1 Full directory tree

```
<workspace_root>/                                          (e.g., harness-build/)
│
├── README.md                                              (bootstrap-generated; Runbook §4.4.7)
├── CLAUDE.md                                              (bootstrap transferred)
├── Sub_Agent_Boundary_Specification_v1.md                 (bootstrap transferred)
├── Phase_7_Session_1_Entry_Directive_v1.md                (bootstrap transferred)
├── Phase_7_Workspace_Bootstrap_Runbook_v1.md              (operator reference)
├── Phase_7_Workspace_Design_Substrate_Manifest_v1.md      (operator reference — this artifact)
├── pyproject.toml                                         (bootstrap-generated)
├── uv.lock                                                (bootstrap-generated)
├── .python-version                                        (bootstrap-generated)
├── .gitignore                                             (bootstrap-generated)
├── .gitattributes                                         (bootstrap-generated)
│
├── .claude/
│   ├── mcp.json                                           (bootstrap-generated)
│   └── skills/
│       ├── phase-7-implementation/SKILL.md                (bootstrap transferred)
│       ├── phase-7-cross-axis-composition/SKILL.md        (bootstrap transferred)
│       ├── phase-7-substitution-retirement/SKILL.md       (bootstrap transferred)
│       └── phase-7-back-flow-routing/SKILL.md             (bootstrap transferred)
│
├── .harness/                                              (runtime; gitignored)
│
├── design-substrate/                                      ◄── NEW per this specification
│   │
│   ├── ADR-F1.md                                          [Category A]
│   ├── ADR-F2.md
│   ├── ADR-F3.md
│   ├── ADR-F4.md
│   ├── ADR-F5.md
│   ├── ADR-D1_v1_2.md
│   ├── ADR-D2.md
│   ├── ADR-D3.md
│   ├── ADR-D4.md
│   ├── ADR-D5.md
│   ├── ADR-D6_v1_2.md
│   ├── Architectural_Design_Document_v1_3.md
│   ├── PRD_v1_1.md
│   ├── Spec_Information_Substrate_v1.md
│   ├── Spec_Action_Surface_v1.md
│   ├── Spec_Control_Plane_v1_3.md
│   ├── Spec_Operational_Discipline_v1_3.md
│   ├── Implementation_Plan_Information_Substrate_v2_2.md
│   ├── Implementation_Plan_Action_Surface_v1.md
│   ├── Implementation_Plan_Control_Plane_v2_3.md
│   ├── Implementation_Plan_Operational_Discipline_v2_4.md
│   ├── Cross_Axis_Composition_Document_v2_1.md
│   ├── Project_Workflow_v1_8.md
│   ├── Phase_7_Meta_Architecture_v1.md
│   ├── Target_Stack_Commitment_v1.md
│   ├── Plan_Executability_Audit_v1.md
│   ├── Persona_Document_v1.md
│   ├── Canonical_Substrate_Inventory.md
│   ├── Phase_7_Kickoff_Prompt.md
│   │
│   ├── F2-12_Closure_Declaration.md                       [Category B]
│   ├── Phase_6_5_Pre_Transition_Arc_Manifest.md
│   ├── Phase_6_5_Session_7_Close_Handoff.md
│   │
│   └── archive/                                           [Category C — optional]
│       ├── Phase_6_5_Session_1_Close_Handoff.md
│       ├── Phase_6_5_Session_2_Close_Handoff.md
│       ├── Phase_6_5_Session_3_Close_Handoff.md
│       ├── Phase_6_5_Session_4_Close_Handoff.md
│       ├── Phase_6_5_Session_5_Close_Handoff.md
│       ├── Phase_6_5_Session_6_Close_Handoff.md
│       ├── Phase_6_5_Session_1_Kickoff.md
│       ├── Phase_6_5_Session_2_Kickoff.md
│       ├── Phase_6_5_Session_3_Kickoff.md
│       ├── Phase_6_5_Session_4_Kickoff.md
│       ├── Phase_6_5_Session_5_Kickoff.md
│       ├── Phase_6_5_Session_6_Kickoff.md
│       ├── Phase_6_5_Session_7_Kickoff.md
│       ├── F2-12_Cascade_Entry_Deferral_Note.md
│       ├── F2-12_Closure_Path_Execution_Kickoff.md
│       ├── F2-12_Council_Deliberation_Output.md
│       ├── Path_Delta_Workflow_v1_6_to_v1_7_Revision_Log_Entry.md
│       ├── Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md
│       ├── Phase_4_Entry_Handoff.md
│       ├── Phase_5_Entry_Handoff.md
│       ├── Phase_5_Specification_Authoring_Close_Handoff.md
│       ├── Phase_6_Entry_Handoff.md
│       ├── Phase_6_Close_Handoff.md
│       ├── Integration_Verification_Report.md
│       ├── Governance_Substrate_Propagation_Note_F1-01.md
│       └── Iter-3_Path_C_Disposition_Cascade_Sequencing_Note.md
│
├── harness-core/                                          (H_T source layout)
│   ├── pyproject.toml
│   ├── src/harness_core/__init__.py
│   └── tests/__init__.py
│
├── harness-is/
│   ├── CLAUDE.md                                          (bootstrap transferred)
│   ├── pyproject.toml
│   ├── src/harness_is/__init__.py
│   └── tests/__init__.py
│
├── harness-as/
│   ├── CLAUDE.md                                          (bootstrap transferred)
│   ├── pyproject.toml
│   ├── src/harness_as/__init__.py
│   └── tests/__init__.py
│
├── harness-cp/
│   ├── CLAUDE.md                                          (bootstrap transferred)
│   ├── pyproject.toml
│   ├── src/harness_cp/__init__.py
│   └── tests/__init__.py
│
├── harness-od/
│   ├── CLAUDE.md                                          (bootstrap transferred)
│   ├── pyproject.toml
│   ├── src/harness_od/__init__.py
│   └── tests/__init__.py
│
└── harness-cxa/
    ├── pyproject.toml
    ├── src/harness_cxa/__init__.py
    └── tests/__init__.py
```

### 7.2 Aggregate file counts at workspace post-transfer

| Section | Markdown files | Other files | Total |
|---|---|---|---|
| Workspace root (bootstrap + reference) | 5 | 5 (pyproject.toml, lockfile, etc.) | 10 |
| `.claude/skills/` | 4 SKILL.md | 1 mcp.json | 5 |
| `design-substrate/` (Category A + B) | 32 | 0 | 32 |
| `design-substrate/archive/` (Category C optional) | 26 | 0 | 26 |
| 4× per-axis subdirectories (IS/AS/CP/OD) | 4 (CLAUDE.md) | 12 (pyproject.toml + 2 inits per axis) | 16 |
| `harness-core/`, `harness-cxa/` | 0 | 6 (2 axes × 3 files) | 6 |
| `.harness/` (runtime; empty at bootstrap) | 0 | 0 | 0 |
| **Aggregate (mandatory only — A + B + bootstrap)** | **45 markdown** | **24 non-markdown** | **69 files** |
| **Aggregate (with Category C archive)** | **71 markdown** | **24 non-markdown** | **95 files** |

---

## 8. Operator Transfer Procedure

### 8.1 Procedure for the operator

8.1.1 Open the design-phase workspace in Claude.ai. The design substrate is accessible via the project knowledge base.

8.1.2 Download each Category A file (29 files, §3 enumeration) from Claude.ai. Save to a staging folder on local machine (e.g., `~/Downloads/design-substrate-staging/`).

8.1.3 Download each Category B file (3 files, §4 enumeration). Save to same staging folder.

8.1.4 (Optional) Download Category C files (§5 enumeration) if historical context retention is desired. Save to a separate staging subfolder (`~/Downloads/design-substrate-staging/archive/`).

8.1.5 Create the target directory in the bootstrap workspace:

```
cd ~/harness-build
mkdir -p design-substrate
mkdir -p design-substrate/archive   # only if Category C transferred
```

8.1.6 Move the downloaded files to the target paths:

```
mv ~/Downloads/design-substrate-staging/*.md ./design-substrate/
mv ~/Downloads/design-substrate-staging/archive/*.md ./design-substrate/archive/   # if applicable
```

### 8.2 Sequencing relative to the Bootstrap Runbook

Insert this transfer between Runbook §3.5 (place 11 bootstrap artifacts) and §3.6 (verify file layout). Operative sequence:

```
Runbook §3.4: Create bootstrap subdirectories
Runbook §3.5: Place 11 bootstrap artifacts
   │
   ▼
THIS SPEC §8.1: Transfer design substrate to ./design-substrate/
   │
   ▼
Runbook §3.6: Verify file layout (UPDATED to include design-substrate/)
Runbook §4: Bootstrap session (LLM-assisted)
```

### 8.3 Updated §3.6 verification command

Replace Runbook §3.6.1 with this updated command:

```bash
find . -type f -name "*.md" | sort
```

**Expected result (mandatory transfer only — Categories A + B):**

- 11 bootstrap artifacts at root + subdirectories
- 32 design substrate files at `./design-substrate/`
- **Total: 43 markdown files** (before Bootstrap Runbook Part 3 generates any new artifacts)

**Expected result (mandatory + Category C archive):** 43 + 26 = 69 markdown files.

---

## 9. Citation Discipline Preservation

### 9.1 Existing bootstrap citation grammar

Bootstrap CLAUDE.md / SKILL.md / Sub-Agent Boundary Spec / Entry Directive files cite design artifacts by filename only (e.g., `per Spec_Information_Substrate_v1.md §X`). Path prefix is not specified.

### 9.2 Resolution at Claude Code

When Claude Code encounters a filename-only citation, it resolves via:

```
9.2.1 First attempt: Read('./design-substrate/<filename>')
9.2.2 If 9.2.1 fails: Glob('**/<filename>') + Read(matched_path)
9.2.3 If 9.2.2 returns multiple matches: prefer paths under design-substrate/
       over paths under design-substrate/archive/ (canonical > historical)
```

### 9.3 Bootstrap session orientation prompt update

Update Bootstrap Runbook §4.3 orientation prompt to include the following text appended at the end of the prompt:

```
Additionally: the workspace contains a design-substrate/ directory at
the workspace root. All design-phase markdown artifacts (ADRs, ADD, PRD,
specs, plans, CXA, Workflow, Meta-Architecture, Target Stack Commitment,
Plan Executability Audit, Persona Document, Canonical Substrate Inventory)
live there as flat files. When a citation in a bootstrap CLAUDE.md or
SKILL.md file references a filename without a path prefix, look first in
./design-substrate/ for that file.

A design-substrate/archive/ subdirectory may also exist with historical
context artifacts. Treat archive/ content as supplementary; canonical
substrate at design-substrate/ takes precedence.
```

### 9.4 No bootstrap artifact modification required

The current bootstrap CLAUDE.md §2 phrasing ("All canonical artifacts reside at the design-phase workspace ... consult the design-phase workspace copy") is now operationally reinterpreted as: "The design-phase workspace copy is the local copy at `./design-substrate/`." This semantic shift is captured in §9.3 orientation prompt update; no bootstrap artifact re-issue is triggered.

**Class 3 informational item C3-β-2:** Workspace root `CLAUDE.md` §2 phrasing implies cross-workspace reference is functionally available; in practice, all design substrate is locally co-resident. Future workspace root `CLAUDE.md` revision pass may clarify the local-co-residence semantics. Non-blocking; route to future Phase 6.5 Session 6 (ε) revision pass OR Phase 7 sub-phase 7d closure record acknowledgment.

---

## 10. Decision Boundary — Why Not All Files

### 10.1 Token-budget considerations

Loading 70+ markdown files at session open consumes Claude Code's context window aggressively. Phase 7 atomic unit landings each require focused reading of 2–5 relevant design artifacts, not all 32+. On-demand citation resolution per §9.2 keeps token consumption bounded.

### 10.2 Architectural integrity

Categories C and D contain process artifacts (review history) and superseded versions. Including them as if they were canonical risks Claude Code confusing review iterations with canonical decisions. Strict Category-A + Category-B selection preserves the canonical-only operative scope.

### 10.3 Workspace hygiene

Categories C and D total ~50 files. Including all of them inflates the workspace ~4× without operative benefit. The `archive/` subdirectory at §7.1 accommodates Category C selectively if operator-discretion favors retention.

---

## 11. Verification

### 11.1 Post-transfer verification commands

```bash
cd ~/harness-build

echo "=== Category A files (must total 29) ==="
ls design-substrate/ADR-*.md design-substrate/Architectural_*.md \
   design-substrate/PRD_*.md design-substrate/Spec_*.md \
   design-substrate/Implementation_Plan_*.md \
   design-substrate/Cross_Axis_*.md design-substrate/Project_Workflow_*.md \
   design-substrate/Phase_7_*.md design-substrate/Target_*.md \
   design-substrate/Plan_Executability_*.md design-substrate/Persona_*.md \
   design-substrate/Canonical_*.md 2>/dev/null | wc -l

echo "=== Category B files (must total 3) ==="
ls design-substrate/F2-12_Closure_Declaration.md \
   design-substrate/Phase_6_5_Pre_Transition_Arc_Manifest.md \
   design-substrate/Phase_6_5_Session_7_Close_Handoff.md 2>/dev/null | wc -l

echo "=== Aggregate (mandatory — must total 32) ==="
find design-substrate -maxdepth 1 -type f -name "*.md" | wc -l

echo "=== Total workspace markdown (mandatory transfer; must total 43) ==="
find . -type f -name "*.md" -not -path "./design-substrate/archive/*" -not -path "./.venv/*" | wc -l
```

### 11.2 Acceptance criteria

| Check | Expected count |
|---|---|
| Category A files at `design-substrate/` | 29 |
| Category B files at `design-substrate/` | 3 |
| Total markdown at `design-substrate/` (excluding archive subdirectory) | 32 |
| Total workspace markdown (excluding archive + .venv) | 43 |
| Category C files at `design-substrate/archive/` (if operator transferred) | 0–26 (operator-discretion) |

---

## 12. Citation Audit (Bootstrap Artifacts → Required Files)

### 12.1 Workspace root `CLAUDE.md` citation audit

| Citation surface | Cites filename | Required at workspace |
|---|---|---|
| §1.1 Project framing | `Cross_Axis_Composition_Document_v2_1.md` | A.22 |
| §1.3 Authority chain | F1–F5 + D1–D6 ADRs; ADD v1.3; PRD v1.1; per-axis spec v1.x; per-axis plan v2.x; CXA v2.1 | A.1–A.11, A.12, A.13, A.14–A.17, A.18–A.21, A.22 |
| §2.4 Per-axis plans | All 4 plan filenames | A.18–A.21 |
| §3.1 Stack discipline | `Target_Stack_Commitment_v1.md`; ADR-F1 v1.2 | A.25, A.1 |
| §3.2 Framework-pull discipline | `Plan_Executability_Audit_v1.md` | A.26 |
| §3.3 Repo layout | (declarative; no file citations) | — |
| §4 Back-flow channels | `Project_Workflow_v1_8.md` §2.7.6; Meta-Architecture §10 | A.23, A.24 |

### 12.2 Per-axis `harness-is/CLAUDE.md` citation audit

| Citation surface | Cites filename | Required at workspace |
|---|---|---|
| §1.2 Spec + plan authority | `Spec_Information_Substrate_v1.md`; `Implementation_Plan_Information_Substrate_v2_2.md` | A.14, A.18 |
| §1.3 Scope inclusion | (preserved verbatim from IS plan v2.1 §4 coverage matrix) | A.18 |
| §2 Cross-axis edge inventory | `Cross_Axis_Composition_Document_v2_1.md` §2.3.1 | A.22 |
| §3 Topological entry-points | IS plan v2.2 §3.1; IS plan v2.1 §3 (preserved) | A.18 |
| §4 Substitution + anti-leakage | `Phase_7_Meta_Architecture_v1.md` §5.2 + §7.2 | A.24 |
| §5 Back-flow channels | `Project_Workflow_v1_8.md` §2.7.6 | A.23 |

### 12.3 Per-axis `harness-as/CLAUDE.md` citation audit

| Citation surface | Cites filename | Required at workspace |
|---|---|---|
| Spec + plan authority | `Spec_Action_Surface_v1.md`; `Implementation_Plan_Action_Surface_v1.md` | A.15, A.19 |
| Cross-axis edges | `Cross_Axis_Composition_Document_v2_1.md` §2.3.1 + §2.3.4 + §2.3.6 | A.22 |
| Substitution + anti-leakage | `Phase_7_Meta_Architecture_v1.md` §5.3 + §7.3 | A.24 |
| Back-flow | `Project_Workflow_v1_8.md` §2.7.6 | A.23 |

### 12.4 Per-axis `harness-cp/CLAUDE.md` citation audit

| Citation surface | Cites filename | Required at workspace |
|---|---|---|
| Anchoring ADRs | ADR-F1/F2/F3/F5 + ADR-D1/D2/D3/D4/D5/D6 | A.1, A.2, A.3, A.5, A.6, A.7, A.8, A.9, A.10, A.11 |
| ADD attestation | `Architectural_Design_Document_v1_3.md` | A.12 |
| Spec + plan | `Spec_Control_Plane_v1_3.md`; `Implementation_Plan_Control_Plane_v2_3.md` | A.16, A.20 |
| Cross-axis | `Cross_Axis_Composition_Document_v2_1.md` §2.3.2/3/4 | A.22 |
| Substitution + anti-leakage | `Phase_7_Meta_Architecture_v1.md` §5.4 + §7.4 + §9 | A.24 |
| Carry-forward closure | `F2-12_Closure_Declaration.md` | B.1 |
| Class 2 carry-forward visibility | `Project_Workflow_v1_8.md` §2.7.7; `Phase_6_5_Session_4_Close_Handoff.md` §5.2 | A.23 + C.4 (Session 4 close) |
| Back-flow | `Project_Workflow_v1_8.md` §2.7.6 | A.23 |
| Framework-pull discipline | `Plan_Executability_Audit_v1.md` | A.26 |

**Note:** The `Phase_6_5_Session_4_Close_Handoff.md` citation falls under Category C historical context. Without transfer, the citation resolves to absent. Operator may choose to elevate Session 4 close handoff to Category B for traceability completeness.

### 12.5 Per-axis `harness-od/CLAUDE.md` citation audit

| Citation surface | Cites filename | Required at workspace |
|---|---|---|
| Anchoring ADRs | ADR-D1/D4/D5/D6 + ADR-F2/F3 | A.6, A.9, A.10, A.11, A.2, A.3 |
| ADD attestation | `Architectural_Design_Document_v1_3.md` | A.12 |
| Spec + plan | `Spec_Operational_Discipline_v1_3.md`; `Implementation_Plan_Operational_Discipline_v2_4.md` | A.17, A.21 |
| Cross-axis | `Cross_Axis_Composition_Document_v2_1.md` §2.3.3/5/6 | A.22 |
| Substitution + anti-leakage | `Phase_7_Meta_Architecture_v1.md` §5.5 + §7.5 | A.24 |
| F2-12 cascade closure | `F2-12_Closure_Declaration.md` | B.1 |
| Back-flow | `Project_Workflow_v1_8.md` §2.7.6 | A.23 |

### 12.6 `Sub_Agent_Boundary_Specification_v1.md` citation audit

| Citation surface | Cites filename | Required at workspace |
|---|---|---|
| Sub-agent count rationale | `Phase_7_Meta_Architecture_v1.md` §10.2.3 | A.24 |
| Per-sub-agent responsibility | IS plan v2.2 §3.4; AS plan v1 §3.5; CP plan v2.3; OD plan v2.4 §3 | A.18, A.19, A.20, A.21 |
| Per-sub-agent substitution authority | Meta-Architecture §5.2–§5.6 | A.24 |
| CP-AL-1 verbatim | Meta-Architecture §7.4 | A.24 |
| Cross-cutting anti-leakage | Meta-Architecture §7.7 (X-AL-1/2/3) | A.24 |
| Operator-orchestrator coordination | Meta-Architecture §10.2.4 | A.24 |
| Back-flow | `Project_Workflow_v1_8.md` §2.7.6 | A.23 |
| `phase-7-back-flow-routing` skill | `<workspace_root>/.claude/skills/phase-7-back-flow-routing/SKILL.md` | (bootstrap transferred) |

### 12.7 Phase 7-specific SKILL.md citation audit

| Skill | Citations | Required at workspace |
|---|---|---|
| `phase-7-implementation` | Per-axis specs v1.x; per-axis plans v2.x; ADD v1.3; PRD v1.1; CXA v2.1; Meta-Architecture; Workflow v1.8 | A.12, A.13, A.14–A.17, A.18–A.21, A.22, A.23, A.24 |
| `phase-7-cross-axis-composition` | CXA v2.1; per-axis plans v2.x (terminal exporter manifests); Meta-Architecture §5.6 + §6.3 + §7.6 | A.18–A.21, A.22, A.24 |
| `phase-7-substitution-retirement` | Meta-Architecture §5 + §6 + §7.7 (X-AL-2); per-axis plans v2.x | A.18–A.21, A.24 |
| `phase-7-back-flow-routing` | Workflow v1.8 §2.7.6 + §2.6.5.3; `Phase_7_Kickoff_Prompt.md` §6; Meta-Architecture §10.5.3 + §7.7; `Canonical_Substrate_Inventory.md` | A.23, A.24, A.28, A.29 |

### 12.8 `Phase_7_Session_1_Entry_Directive_v1.md` citation audit

The Entry Directive cites: all 11 ADRs (§2.2.1), ADD v1.3 (§2.2.2), PRD v1.1 (§2.2.2), 4 specs (§2.2.3), 4 plans (§2.2.4), CXA v2.1 (§2.2.2), Workflow v1.8 (§2.2.5), Meta-Architecture v1 (§2.2.5), `Phase_7_Kickoff_Prompt.md` (§2.2.5), `Target_Stack_Commitment_v1.md` (§2.2.5), `Plan_Executability_Audit_v1.md` (§2.2.5), `Canonical_Substrate_Inventory.md` (§2.2.5), `Phase_6_5_Pre_Transition_Arc_Manifest.md` (§2.2.6), `Phase_6_5_Session_7_Close_Handoff.md` (§3 entry-gate criterion 7), and (implicitly via close handoff cross-reference) the Phase 6.5 Session 4 close handoff for OD-S4-4.A.

| Required at workspace | All of: A.1–A.29, B.1–B.3 + (optional) Phase 6.5 Session 4 close handoff |
|---|---|

### 12.9 Citation coverage verification

| Category A files | Citation coverage | Required by |
|---|---|---|
| All 29 Category A files | 100% | At least one bootstrap artifact citation site |
| All 3 Category B files | 100% | At least one bootstrap artifact citation site |
| Category C — Phase 6.5 Session 4 close handoff (if elevated to mandatory) | 1 site | `harness-cp/CLAUDE.md` §5.2 "Class 2 carry-forward visibility" |

**Recommendation:** Elevate `Phase_6_5_Session_4_Close_Handoff.md` from Category C to Category B (closure records), making **Category B total = 4 files**. This preserves citation traceability for the H_T-CP-1 Class 2 substitution-risk surface at full fidelity.

---

## 13. Updated Category B (Post-Recommendation §12.9)

If §12.9 recommendation is adopted:

| # | Source filename | Citation site | Target path |
|---|---|---|---|
| B.1 | `F2-12_Closure_Declaration.md` | `harness-cp/CLAUDE.md` §5.2; `harness-od/CLAUDE.md` §5.2 | `design-substrate/F2-12_Closure_Declaration.md` |
| B.2 | `Phase_6_5_Pre_Transition_Arc_Manifest.md` | Multiple Phase 7-specific SKILL.md + workspace root CLAUDE.md + Entry Directive | `design-substrate/Phase_6_5_Pre_Transition_Arc_Manifest.md` |
| B.3 | `Phase_6_5_Session_7_Close_Handoff.md` | Entry Directive §3 entry-gate criterion 7 | `design-substrate/Phase_6_5_Session_7_Close_Handoff.md` |
| B.4 | `Phase_6_5_Session_4_Close_Handoff.md` (newly elevated) | `harness-cp/CLAUDE.md` §5.2 H_T-CP-1 Class 2 carry-forward visibility; Entry Directive §4.2 OD-S4-4.A rationale | `design-substrate/Phase_6_5_Session_4_Close_Handoff.md` |

**Category B revised total: 4 files.**

**Aggregate mandatory transfer (Category A + revised Category B): 29 + 4 = 33 files.**

If operator declines §12.9 elevation, retain B.1–B.3 only (3 files; aggregate mandatory transfer = 32 files); the Session 4 close handoff citation in `harness-cp/CLAUDE.md` §5.2 will resolve as "absent at lookup" — Claude Code will infer the carry-forward from `F2-12_Closure_Declaration.md` and the Meta-Architecture §9 statement.

---

## 14. Filing Footer

| Field | Value |
|---|---|
| Artifact | `Phase_7_Workspace_Design_Substrate_Manifest_v1.md` |
| Type | Specification — design substrate transfer manifest for Phase 7 workspace |
| Authoring authority | Operator directive 2026-05-15 (cross-workspace reference infeasibility at Claude Code CLI; all context must be locally co-resident) |
| Predecessor | `Phase_7_Workspace_Bootstrap_Runbook_v1.md`; 11 bootstrap artifacts |
| Successor consumption | Insert into Bootstrap Runbook execution between §3.5 and §3.6 per §8.2 sequencing |
| Class 3 informational | C3-β-2 surfaced at §9.4 (workspace root CLAUDE.md §2 cross-workspace phrasing); non-blocking; future revision pass routing |
| Mandatory file count | 32 files (Category A + B.1–B.3) OR 33 files (Category A + B.1–B.4 if §12.9 adopted) |
| Optional file count | 26 files (Category C archive) |
| Recommended path | §12.9 recommendation: elevate Phase 6.5 Session 4 close handoff to Category B for full citation traceability |
| Date | 2026-05-15 |

---

*End of Phase 7 Workspace Design Substrate Manifest v1. Use in conjunction with `Phase_7_Workspace_Bootstrap_Runbook_v1.md` per §8.2 sequencing. Operator-discretion at §5 Category C transfer subset selection and at §12.9 Category B elevation.*

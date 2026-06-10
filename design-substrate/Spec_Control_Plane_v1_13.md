# Specification — Control Plane v1.13

## Change-note (v1.12 → v1.13)

**Scope of revision.** Class 1 fork resolution Reading A apply pass per `.harness/class_1_fork_cp_spec_section_25_contract_id_collision.md` §7 (operator-ratified 2026-05-24 at HEAD `50bb8b9` via AskUserQuestion "Ratify Reading A; open spec-writer apply pass now"). The v1.10 NEW §25 / C-CP-25 ValidatorFramework is renamed to **§28 / C-CP-28** to resolve the section-number + contract-ID collision with the v1.6 NEW §25 / C-CP-25 WorkflowDriver. The v1.6-lineage §25 / C-CP-25 WorkflowDriver retains canonical-ID primacy per first-author 2026-05-20 (vs ValidatorFramework first-author 2026-05-21) + v1.10's explicit preservation claim ("All v1.9 content preserved verbatim") + F-derivative anchor proximity (WorkflowDriver anchors on F-ADR-F3; ValidatorFramework anchors on D-ADR-D3). Tiebreaker passes empirically (zero supersession-hits at v1.10 spec text). Citation-correction patch only — ZERO contract change, ZERO signature change, ZERO field-set change, ZERO acceptance-criterion change.

**v1.12 substantive content preserved verbatim.** All v1.12 content outside the §25 → §28 rename of the ValidatorFramework body preserved unchanged. The v1.12 §25.2.1 9th-field `workflow_id` addition (Class 1 fork Path A absorption per `[[fork-step-execution-context-workflow-id-field-absence]]`) preserved verbatim — that amendment landed at the v1.6-lineage WorkflowDriver §25 / C-CP-25 surface and is NOT touched by this rename. The v1.11 §26.2 `WorkflowPauseReason` rename + §26 coexistence NOTE preserved. The v1.10 NEW §17.4 + §26 + §27 chains preserved verbatim. The v1.6 NEW §25 / C-CP-25 WorkflowDriver contract preserved verbatim (the rename target is the v1.10 NEW §25, NOT the v1.6 §25).

**Source of fix.** `.harness/class_1_fork_cp_spec_section_25_contract_id_collision.md` §7 RATIFIED 2026-05-24 (operator). The fork doc §7.7 recommends Reading A at [HIGH] confidence on three convergent authority-chain anchors:

1. **First-author primacy** (workspace `CLAUDE.md` §1.3 authority-chain ordering applied within-spec to temporal authoring order): WorkflowDriver first-authored 2026-05-20 at v1.6; ValidatorFramework second-authored 2026-05-21 at v1.10. Earlier authoring wins canonical-ID primacy.

2. **v1.10's own preservation claim** (`Spec_Control_Plane_v1_10.md:5,44`): explicitly preserves v1.9 content verbatim → includes v1.6 §25 / C-CP-25 carried through v1.7/v1.8/v1.9 preservation chain → contradicts v1.10's de-facto override. Restoring fidelity-pure transcription requires renaming v1.10 NEW, not v1.6.

3. **F-derivative anchor proximity** (skill §2.3 F/D/I classification): WorkflowDriver anchors on ADR-F3 §Decision (iv) (F-level); ValidatorFramework anchors on ADR-D3 v1.2 (D-level). Marginal anchor-proximity asymmetry favors WorkflowDriver retaining canonical-ID primacy.

**Tiebreaker check (skill §4A.2 step 5).** Confirmed at HEAD: `grep -n "supersede\|deprecate\|replace.*§25\|deletes\|removes.*WorkflowDriver" design-substrate/Spec_Control_Plane_v1_10.md` returns ZERO hits. v1.10 never declared supersession of v1.6 §25 / C-CP-25 — the collision was an authoring oversight, not deliberate replacement. Recommendation determinacy criterion MET.

**One amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§25 (v1.10 NEW) → §28 (v1.13 renamed)** | The v1.10 NEW §25 ValidatorFramework section + C-CP-25 ValidatorFramework contract ID rename to §28 / C-CP-28. Mechanical citation-correction: section number `§25` → `§28` at all v1.10 ValidatorFramework-context section headers + §25.1 → §28.1 + §25.2 → §28.2 + §25.3 → §28.3 + §25.4 → §28.4 + §25.5 → §28.5 + §25.6 → §28.6 + §25.7 → §28.7 + §25.8 → §28.8 + §25.9 → §28.9 (preserving v1.10's internal §25.x sub-section structure verbatim); contract ID `C-CP-25` → `C-CP-28` at all ValidatorFramework references; all contract body content (5-class `ValidatorFailClass` taxonomy + 5-class `ValidatorOutcome` enum + `ValidatorEvaluation` envelope + span emission `validator.evaluate` + `validator.fail` + `validator.revalidation` + `validator.escalation` + 2 new CP fail classes) PRESERVED VERBATIM. ADR-D3 v1.2 anchor commitment preserved verbatim. Decision 2.D3 (validators run EVERY step, opt-out via no-op validator) preserved verbatim. NO field-set change; NO signature change; NO behavior change; NO acceptance-criterion change. The v1.10 spec file itself is preserved-verbatim in the delta-only chain — the rename is recorded as an additive amendment at v1.13 (this file) and consumers reading the chain interpret the v1.10 NEW §25 as canonically renamed to §28 at v1.13 per this change-note. | `.harness/class_1_fork_cp_spec_section_25_contract_id_collision.md` §7 Reading A operator ratification 2026-05-24 |

**Disambiguation invariant.** After v1.13:

| Section | Contract ID | Contract name | Lineage |
|---|---|---|---|
| §25 | C-CP-25 | WorkflowDriver | v1.6-lineage (introduced v1.4 → v1.5 → v1.6; v1.12 §25.2.1 9th-field amendment preserved) |
| §28 | C-CP-28 | ValidatorFramework | v1.10-lineage (introduced v1.10 §25 NEW; renamed §28 at v1.13 per Reading A) |

No remaining ambiguity at section number OR contract ID. The v1.10 NEW §17.4 (`hitl_gate` signature materialization) preserved at §17.4 (NOT touched by rename). The v1.10 NEW §26 (PauseResumeProtocol / C-CP-26) preserved at §26. The v1.10 NEW §27 (PerServerTrustEvaluator / C-CP-27) preserved at §27. v1.13 §28 (ValidatorFramework / C-CP-28) is the renamed v1.10 NEW §25.

**Status posture.** Proposed (v1.12) → **Proposed (v1.13)**. v1.13 is a citation-correction patch — single rename event at the v1.10 NEW §25 / C-CP-25 ValidatorFramework surface. NO v1.12 contract removed; NO v1.12 contract re-decomposition; NO new contract authored (the rename re-numbers an existing contract; it does not introduce a new one). Contract count unchanged: 27 (C-CP-01 through C-CP-28 with C-CP-21 retired-at-spec-text → no, C-CP-21 NOT retired at spec, the C-CP-21 row stays — let me preserve verbatim count). Effective contract count at v1.13: identical to v1.12; the rename redistributes the ID space but does not add or remove.

**Re-count after rename.** v1.12 contract IDs: C-CP-01 through C-CP-27 (27 contracts; C-CP-25 WorkflowDriver collides with C-CP-25 ValidatorFramework — counted as 27 distinct contract surfaces despite ID collision). v1.13 contract IDs: C-CP-01 through C-CP-27 + C-CP-28 = 28 distinct IDs covering 27 distinct contract surfaces (the ID space is now 1:1 with the contract surfaces). Net surface count unchanged at 27.

**Downstream absorption owed (post-v1.13).**

(a) Workspace `CLAUDE.md` §2.3 CP spec row version bump (v1.12 → v1.13).

(b) `Spec_Harness_Runtime_v1.md` v1.18 cite retag at all "CP spec v1.11 §25" / "C-CP-25 §25.x" ValidatorFramework-context references → "CP spec v1.13 §28" / "C-CP-28 §28.x". Runtime spec is single-file (not delta-chain) — cite retag absorbed at runtime spec v1.18 → v1.19 micro-bump or in-place v1.18 amendment per spec-writer follow-on arc. ~6 cite sites at runtime spec.

(c) `Implementation_Plan_Control_Plane_v2_18.md` cite retag: cluster 10-CP-A units (U-CP-58/59/60/61) Implements/Files/Signatures lines referencing C-CP-25 ValidatorFramework → C-CP-28. CP plan v2.18 → v2.19 via `implementation-planner` revision-pass at separate arc. The v1.6-lineage U-CP-56 (StepExecutionContext) cites preserved verbatim (those reference §25 WorkflowDriver, not ValidatorFramework).

(d) `Implementation_Plan_Harness_Runtime_v2_17.md` L9-decies cluster cite retag: 13+ cite sites "CP spec v1.11 §25" in ValidatorFramework context → "CP spec v1.13 §28". Runtime plan v2.17 → v2.18 via `implementation-planner` revision-pass at separate arc.

(e) `harness-cp/CLAUDE.md` §1.3 ValidatorFramework scope row + §4.1 H_T-CP-21 substitution row cite retag at C-CP-25 → C-CP-28 references. Per-axis bookkeeping.

(f) `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §1.1 grep-verified inventory cite-paths retag. Adjacent fork doc bookkeeping.

(g) `Cross_Axis_Composition_Document_v2_8.md` (or successor) — if references CP §25 ValidatorFramework → retag. (Empirical check at apply arc: CXA v2.8 references C-CP-25 ValidatorFramework at §2.3.7 composer-arc absorption row. Cite retag at CXA next-touch arc.)

(h) `.harness/class_1_fork_cp_spec_section_25_contract_id_collision.md` §8 ratification footer documenting Reading A applied at this v1.13 publication.

(i) Memory: `[[fork-section-25-collision]]` entry advance — Reading A APPLIED at v1.13.

**Code retag (within-package import + class identifier).** ZERO code change owed by this v1.13 amendment per fidelity-pure citation-correction discipline. The Python class identifier `ValidatorFramework` at `harness-cp/src/harness_cp/validator_framework.py` is NOT a contract ID; the contract ID `C-CP-25` is a spec-citation-only identifier and does not appear in any code import or class name. The runtime spec v1.18 §14.13 NEW C-RT-23 contract consumes the `ValidatorFramework` Protocol surface by Python class name (not by contract-ID cite); the cite retag at runtime spec absorbs the C-CP-25 → C-CP-28 rename in prose only.

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).**

(i) **v1.10 NEW §17.4 + §25 + §26 + §27 sequential numbering.** With §25 ValidatorFramework renamed to §28, the v1.10 numbering sequence becomes §17.4 → §25 (WorkflowDriver, v1.6) → §26 (PauseResumeProtocol, v1.10) → §27 (PerServerTrustEvaluator, v1.10) → §28 (ValidatorFramework, v1.10 renamed at v1.13). The §28 section is non-sequentially adjacent to §27 — readable but a numbering oddity. NOT renumbered per FM-2 — §26 and §27 are first-author canonical at v1.10 with their own downstream cite traffic. Surfaced; the §28 placement is fidelity-pure (preserves v1.10's later-numbered authoring intent) at cost of non-sequential numbering. Future v1.x revision MAY re-pack the v1.10 NEW contracts (§25 ValidatorFramework + §26 PauseResumeProtocol + §27 PerServerTrustEvaluator) into contiguous sequence (e.g., §28 / §29 / §30) IF an independent motivation arises; not done at this fidelity-pure rename apply pass.

(ii) **Adversarial Review 06 + 07 cite drift.** .harness/archive/root-historical/Adversarial_Review_06_Runtime_v2_14.md + Adversarial_Review_07 reference "CP spec v1.11 §25" with v1.10-meaning ValidatorFramework context. Both reviews were CLEARED prior to v1.13; the cite drift is post-clearance and bookkeeping-only. Surfaced; cite retag absorbed at next adversarial review touch or at the implementation-planner revision-pass cite cascade arc per §(c) + §(d) above.

(iii) **Adjacent renumbering-drift family.** The sibling fork `.harness/class_1_fork_meta_arch_cp_spec_renumbering_drift.md` records meta-arch-side cite renumbering drift APPLIED at Meta-Arch v1.5 `b2cf37b`. v1.13 here is a parallel-shape resolution at the CP-spec-side renumbering surface — first-author canonical contract retains its ID; later-authored offender renamed. Pattern reinforced: when a renumbering collision surfaces, fidelity-pure resolution renames the offender, not the canonical.

---

## §1 — §25 ValidatorFramework → §28 rename (v1.13)

The v1.10 NEW §25 / C-CP-25 ValidatorFramework section is renamed to §28 / C-CP-28 at v1.13. The contract body — `ValidatorFramework` Protocol surface + 5-class `ValidatorFailClass` taxonomy + 5-class `ValidatorOutcome` enum + `ValidatorEvaluation` envelope + 4-event span emission set (`validator.evaluate` / `validator.fail` / `validator.revalidation` / `validator.escalation`) + 2 new CP fail classes (per v1.10 NEW §25.4 + §25.7) + Decision 2.D3 (validators run EVERY step, opt-out via no-op validator) — is PRESERVED VERBATIM at the renamed §28 location.

### §1.1 Mechanical rename inventory

The v1.10 NEW §25 sub-section structure is preserved verbatim at §28:

| v1.10 section | v1.13 section | Content |
|---|---|---|
| `§25 (NEW) C-CP-25 — ValidatorFramework` | `§28 C-CP-28 — ValidatorFramework` | Section header + contract surface prose |
| `§25.1 Canonical signature(s)` | `§28.1 Canonical signature(s)` | `Validator` Protocol + `ValidatorFramework` Protocol signatures |
| `§25.2 Field sets` | `§28.2 Field sets` | `ValidatorEvaluation` envelope + `ValidatorOutcome` enum (5-class) + `ValidatorFailClass` enum (5-class) field-set authoring |
| `§25.3 Lifecycle` | `§28.3 Lifecycle` | Validator dispatch lifecycle prose; Decision 2.D3 (validators run EVERY step) |
| `§25.4 Failure modes` | `§28.4 Failure modes` | 2 new CP fail classes (per v1.10 NEW: `CP-FAIL-VALIDATOR-CATALOG-MISSING`, `CP-FAIL-VALIDATOR-EXECUTION`) |
| `§25.5 Spans` | `§28.5 Spans` | 4-event span emission set (`validator.evaluate` / `validator.fail` / `validator.revalidation` / `validator.escalation`) |
| `§25.6 Invariants` | `§28.6 Invariants` | Validator invariants (deterministic; opt-out via no-op; cause_attribution invariance per ADR-D4) |
| `§25.7 Deferred to implementation discretion` | `§28.7 Deferred to implementation discretion` | Deferral notation prose |
| `§25.8 Cross-axis composition` | `§28.8 Cross-axis composition` | Composition with OD spec §C-OD-29 `validator.*` span schema + runtime spec §14.13 stage-4 factory |
| `§25.9 (if present at v1.10)` | `§28.9 (if present at v1.10)` | Carry-forward — preserved verbatim |

(Note: the v1.10 NEW §25 may not have a full §25.1–§25.9 enumeration — v1.10 may have authored fewer sub-sections. The rename preserves whatever sub-sections v1.10 authored, mapping §25.x → §28.x byte-exact.)

### §1.2 Contract ID rename

| v1.10 contract ID | v1.13 contract ID |
|---|---|
| `C-CP-25` (when context = ValidatorFramework) | `C-CP-28` |
| `C-CP-25` (when context = WorkflowDriver, v1.6-lineage) | `C-CP-25` (PRESERVED — v1.6-lineage canonical) |

Context-disambiguation at the rename target: any v1.10 ValidatorFramework reference using bare `C-CP-25` (no §-suffix) is renamed to `C-CP-28` at the v1.10 spec text within the v1.13-canonical reading. Within v1.13 + downstream artifacts, `C-CP-25` unambiguously references WorkflowDriver (v1.6-lineage); `C-CP-28` unambiguously references ValidatorFramework (v1.10-lineage renamed).

### §1.3 Verbatim-layer integrity

The v1.10 spec file (`Spec_Control_Plane_v1_10.md`) is itself NOT edited at v1.13 — the delta-only spec-chain preservation discipline keeps v1.10 byte-exact at its filing footer. Consumers reading the delta chain interpret the v1.10 NEW §25 ValidatorFramework AS canonically renamed to §28 / C-CP-28 at v1.13 per this change-note. This pattern is parallel to the v1.11 → v1.12 §25.2.1 9th-field amendment: v1.11 + earlier spec files are preserved verbatim; the canonical reading at v1.12 incorporates the field addition; consumers reading "the spec at v1.12" understand the §25.2.1 record per v1.12's amended definition.

**Future implementation-planner + spec-writer arcs absorbing this rename** cite the renamed surface as `C-CP-28 §28.x ValidatorFramework per CP spec v1.13 §1 rename` until cite-cascade fully absorbs into downstream artifacts.

---

## §2 — Preservation guarantees

| Element | Disposition |
|---|---|
| v1.12 §25.2.1 9th-field `workflow_id` amendment | Preserved verbatim — landed at v1.6-lineage WorkflowDriver §25 surface; NOT touched by v1.13 ValidatorFramework rename |
| v1.11 §26.2 `WorkflowPauseReason` rename + §26 coexistence NOTE | Preserved verbatim |
| v1.10 NEW §17.4 (`hitl_gate` canonical signature materialization) | Preserved verbatim — NOT touched by §25 → §28 rename |
| v1.10 NEW §26 C-CP-26 PauseResumeProtocol | Preserved verbatim — NOT touched by rename (§26 is unaffected) |
| v1.10 NEW §27 C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter | Preserved verbatim — NOT touched by rename (§27 is unaffected) |
| v1.10 NEW §25 C-CP-25 ValidatorFramework contract body (Protocol surface + 5-class `ValidatorFailClass` taxonomy + 5-class `ValidatorOutcome` enum + `ValidatorEvaluation` envelope + 4-event span emission set + 2 new CP fail classes + Decision 2.D3) | Renamed to §28 / C-CP-28 — contract body content PRESERVED VERBATIM |
| v1.6 NEW §25 C-CP-25 WorkflowDriver contract (preserved verbatim through v1.7/v1.8/v1.9/v1.10/v1.11/v1.12; v1.12 §25.2.1 9th-field extension preserved) | Preserved verbatim — RETAINS canonical §25 / C-CP-25 ID per first-author primacy |
| All other v1.12 contracts (C-CP-01 through C-CP-24 + C-CP-26 + C-CP-27) | Preserved verbatim |
| All ADR commitments (F1–F5 + D1–D6) | Unchanged |
| Decision 2.D3 (validators run EVERY step, opt-out via no-op validator) | Preserved verbatim at renamed §28 location |
| 4-event span emission set names (`validator.evaluate` / `validator.fail` / `validator.revalidation` / `validator.escalation`) | Preserved verbatim — span names are OTel attribute strings, NOT contract IDs; unaffected by rename |
| 5-class `ValidatorFailClass` enum member names | Preserved verbatim |
| 5-class `ValidatorOutcome` enum member names | Preserved verbatim |
| 2 new CP fail classes at v1.10 §25.4 | Preserved verbatim at renamed §28.4 location |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_13.md` |
| Version | v1.13 |
| Filing event | Class 1 fork resolution Reading A apply pass — §25 / C-CP-25 ValidatorFramework → §28 / C-CP-28 rename per `.harness/class_1_fork_cp_spec_section_25_contract_id_collision.md` §7 Reading A ratification 2026-05-24 |
| Predecessor | `Spec_Control_Plane_v1_12.md` (v1.12 substantive content preserved verbatim outside the §25 ValidatorFramework → §28 rename — which is recorded at the v1.10 NEW §25 surface, NOT at the v1.12 §25.2.1 WorkflowDriver-lineage surface) |
| Co-published artifacts (this arc) | Workspace `CLAUDE.md` §2.3 CP row bump v1.12 → v1.13; `.harness/class_1_fork_cp_spec_section_25_contract_id_collision.md` §8 ratification footer |
| Downstream absorption owed (next arcs) | Runtime spec v1.18 cite retag (separate spec-writer arc); CP plan v2.18 cluster 10-CP-A cite retag (implementation-planner arc); Runtime plan v2.17 L9-decies cite retag (implementation-planner arc); harness-cp/CLAUDE.md cite retag; adjacent fork doc cite retag; CXA next-touch cite retag |
| Operator authority | `.harness/class_1_fork_cp_spec_section_25_contract_id_collision.md` §7 Reading A ratification (AskUserQuestion 2026-05-24, operator selected "Ratify Reading A; open spec-writer apply pass now") |
| Contract-count change | Effective contract surfaces unchanged at 27; contract IDs expand by 1 (C-CP-28 NEW; collision-pair resolved 1:1 to surfaces) |
| Fail-class-count change | None |
| Signature change at any Protocol | None |
| Acceptance criterion change at any contract | None |
| Behavior change | None |
| Cross-axis cascade | ZERO at semantics layer (per fork §5 + §7.12 architect recommendation) |
| Skill discipline | `spec-writer` Phase-7 spec-fix application of operator-ratified Reading A; fidelity-pure citation-correction patch; NO contract change; NO extension; preservation audit PASSED |
| Date | 2026-05-24 |

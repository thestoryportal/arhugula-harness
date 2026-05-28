# Implementation Plan — Control Plane (v2.25)

*Delta over v2.24. v2.25 absorbs CP spec v1.19 → v1.20 NEW §6.1.Y `WorkflowManifestEntry.default_gate_level: GateLevel | None = None` field at U-CP-13 (the WorkflowManifestEntry carrier unit). Single-unit-body amendment at delta-only-plan-chain layer; 73 → 73 unit count unchanged; ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO coverage matrix structural delta; ZERO cross-axis cascade.*

## §0 Change note (v2.24 → v2.25)

### §0.1 Revision context — U-CP-13 absorbing CP spec v1.20 §6.1.Y

Per CP spec v1.19 → v1.20 NEW §6.1.Y `WorkflowManifestEntry.default_gate_level` field addition (Reading A absorption per `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` operator-ratified 2026-05-27 Q1=A + Q2=apply-now + Q3=defer-layer-3-e2e): U-CP-13 (the WorkflowManifestEntry carrier unit per CP plan v2.10 Cluster 2 — F3 lifecycle event emission + workflow manifest schema + per-step override evaluator) absorbs the field-set extension at the carrier layer.

### §0.2 Sections revised

§0 (this change note); U-CP-13 canonical-reading amendment table for the field-set + AC + Tests-line refresh. All other unit bodies preserved verbatim from v2.24 (which preserved verbatim from v2.23 + ... per delta-only-plan-chain convention).

### §0.3 U-CP-13 canonical-reading amendment (NEW v2.25)

Per delta-only convention, U-CP-13 unit body at the v2.x base file (canonical at `Implementation_Plan_Control_Plane_v2_1.md` §2 preserved through v2.24) is NOT edited byte-exact; v2.25 publishes a canonical-reading amendment table that downstream readers apply when interpreting U-CP-13.

**Field-set amendment:**

| Pre-v2.25 reading (v2.24 + prior) | v2.25 canonical reading | Cite |
|---|---|---|
| WorkflowManifestEntry: 11 fields (v2.12 `entry_version` addition) | WorkflowManifestEntry: **12 fields** (v2.25 `default_gate_level` addition per CP spec v1.20 §6.1.Y Reading A absorption) | CP spec v1.20 §6.1.Y + fork `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` Q1=A ratification |
| AC #1 11-field assertion | AC #1 12-field assertion (extends v2.12 11-field assertion with `default_gate_level` at position-end) | Same |
| Tests-line covered AC #1 via `test_workflow_manifest_entry_eleven_fields` | Tests-line **renamed** to `test_workflow_manifest_entry_twelve_fields` + 3 NEW tests: `test_workflow_manifest_entry_has_default_gate_level_field` + `test_workflow_manifest_entry_default_gate_level_is_none` + `test_workflow_manifest_entry_accepts_explicit_default_gate_level` | Co-published at `harness-cp/tests/test_workflow_manifest_entry.py` |
| Signatures line preserved v2.12 fields | Signatures line **adds** `default_gate_level: GateLevel | None = None` at position-end; preserves `entry_version: int = 1` + all 10 v2.11 fields verbatim | Same |
| Imports preserved | NEW import `from harness_cp.gate_level_rule import GateLevel` at `harness-cp/src/harness_cp/workflow_manifest_entry.py` | Same |

**AC count delta:** +0 net (AC #1 text amended in canonical-reading layer; no new AC introduced at v2.25; the 3 NEW tests are coverage extensions of AC #1, not new ACs).

**Test-name delta:** +3 (`_has_default_gate_level_field`, `_default_gate_level_is_none`, `_accepts_explicit_default_gate_level`); +1 rename (`_eleven_fields` → `_twelve_fields`).

### §0.4 Cross-axis dependency edges — preserved

U-CP-13 cross-axis edges per CP plan v1 §3.3 baseline: depends on `harness_core.WorkloadClass` + `harness_core.PersonaTier` + `harness_core.StepID` (Pattern-D imports). v2.25 adds an intra-axis import: `harness_cp.gate_level_rule.GateLevel`. NO new cross-axis edge; NO CXA bucket touch; NO CP→AS / CP→IS / CP→OD / OD→CP edge change.

### §0.5 DAG topology — preserved

U-CP-13 sits at L2 per CP plan v2.10 §3.1 DAG topology (L0 13 cluster-bearing entry-points; L1 8; L2 includes U-CP-13). v2.25 preserves L2 placement — the new intra-axis import dependency on `harness_cp.gate_level_rule.GateLevel` (which is at L0 per gate_level_rule's `Depends on: (none)` status) does NOT inversion-create a level violation.

### §0.6 Status posture

Proposed (v2.24) → **Proposed (v2.25)**. v2.25 is a single-unit-body canonical-reading amendment at U-CP-13. No prior unit body change; no DAG topology change; no cluster reorganization; no coverage matrix structural delta.

### §0.7 Adjacent defects surfaced (not patched per FM-2)

(i) **U-CP-13 `Depends on:` line update.** U-CP-13's `Depends on:` declaration at v2.1 §2 base file does NOT cite `gate_level_rule` (the GateLevel import is intra-axis but the GateLevel type was added to CP plan at U-CP-43's gate_level_rule.py landing at v2.5+). The intra-axis import is canonical reading at v2.25 but the `Depends on:` line should grow to `[U-CP-43]` at a future revision-pass arc. NOT patched at v2.25 per FM-2 single-focus-arc scope (the `Depends on:` line is a Class 3 informational drift; the canonical-reading amendment table at v2.25 §0.3 documents the dependency).

### §0.8 Downstream absorption owed (post-v2.25)

(a) Workspace `CLAUDE.md` §2.4 CP plan row bump (v2.24 → v2.25). **Patched at v2.25 co-publication.**
(b) Co-published at v2.25 arc (CP spec v1.20 + impl + tests + workflow_driver.py composition site + fork doc Status refresh). **Patched at v2.25 co-publication.**
(c) Retirement event filing — H_T-CP-19 PARTIAL → RETIRE-READY transit at batch-21 (separate retirement-event filing arc; operator-discretion timing per existing 7d cadence).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_25.md` |
| Version | v2.25 |
| Filing event | U-CP-13 absorbing CP spec v1.20 §6.1.Y NEW `default_gate_level` field per `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` Reading A absorption. 2026-05-27 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_24.md` (preserved verbatim outside the §0 amendment at v2.25) |
| Successor | (none — current canonical) |
| Unit count | 73 (unchanged from v2.24) |
| DAG topology | Preserved per v2.10 §3.1 (L2 placement of U-CP-13 unchanged) |
| AC count delta | +0 net (AC #1 text amended via canonical-reading layer; +3 test names; +1 test rename) |
| Cross-axis cascade | ZERO per §0.4 |
| H_T-CP-19 status | Plan-side absorption **APPLIED at v2.25**; production binding **APPLIED at v2.25 co-publication** (workflow_driver.py:738 composition site read); H_T-CP-19 PARTIAL → RETIRE-READY transit owed at batch-21. |
| Operator authority | `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` Q1=A + Q2=apply-now + Q3=defer-layer-3-e2e ratification 2026-05-27 |
| Date | 2026-05-27 |

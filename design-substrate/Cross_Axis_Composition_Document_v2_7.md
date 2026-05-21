# Cross-Axis Composition Document (v2.7)

*Delta over v2.6. v2.7 is a citation-bookkeeping patch absorbing the path-β rename of the C-CP-21 §21.1 `ValidatorFailClass` Python identifier to `ValidatorRetryExitClass` (operator-ratified 2026-05-21 per `.harness/class_1_fork_u_cp_58_validator_fail_class_collision.md`). Single-line cited-identifier update at §0.11 promotion-candidate row 1. No edge cardinality change; no classification change; no bucket count change. The v2.6 §0.11 row 2 (U-OD-29 → U-AS-15 §12.4 arm) preserved verbatim. The v2.6 aggregate (99 cross-axis relationships; 29 genuine-typed-seam; 46 convention-level; 24 phase-2-runtime) preserved verbatim. All other v2.6 substantive content preserved verbatim by reference.*

## §0 Change note (v2.6 → v2.7)

### §0.1 Revision context — path β citation reconciliation

Per `.harness/class_1_fork_u_cp_58_validator_fail_class_collision.md` (operator-ratified path β, 2026-05-21): the OLD C-CP-21 §21.1 Python identifier `ValidatorFailClass` (5-class retry-exit taxonomy: TRANSIENT_RETRY / REFLEXION_RECOVERABLE / HITL_RECOVERABLE / PERMANENT_FAIL_EXIT / TERMINAL_FAIL_EXIT) was renamed at the landed code layer to `ValidatorRetryExitClass` to disambiguate from the NEW C-CP-25 §25.2 `ValidatorFailClass` (5-class pre-emit fail-categorization: SCHEMA_VIOLATION / SEMANTIC_INCONSISTENCY / SAFETY_POLICY / RESOURCE_CONSTRAINT / EXTERNAL_REJECTION) introduced at CP spec v1.10. The CXA v2.6 §0.11 promotion-candidate note for the U-OD-26 → U-CP-47 §2.3.6 convention-level edge cited the OLD identifier; v2.7 updates the citation to the renamed identifier.

### §0.2 Sections revised

§0 (this change note); §0.11 row 1 (U-OD-26 → U-CP-47 promotion-candidate citation). All other sections preserved verbatim from v2.6.

### §0.3 §0.11 amendment

Row 1 (U-OD-26 → U-CP-47 §2.3.6) of the v2.6 §0.11 promotion candidates is amended to:

> U-OD-26 → U-CP-47 (§2.3.6): could import `harness_cp.validator_fail_taxonomy.ValidatorRetryExitClass` (renamed at v2.7 from `ValidatorFailClass` per path β disambiguation against CP spec v1.10 §25.2 NEW C-CP-25 `ValidatorFailClass`). **Note v2.7:** the OLD C-CP-21 §21.1 retry-exit taxonomy at landed code retains its 5-member surface verbatim (TRANSIENT_RETRY / REFLEXION_RECOVERABLE / HITL_RECOVERABLE / PERMANENT_FAIL_EXIT / TERMINAL_FAIL_EXIT); only the class identifier is renamed. The NEW C-CP-25 §25.2 `ValidatorFailClass` is the formalized type per CP spec v1.10 — promotion remains operator-decision.

Row 2 (U-OD-29 → U-AS-15 §12.4 arm) preserved verbatim from v2.6.

### §0.4 Status posture

Proposed (v2.6) → **Proposed (v2.7)**. v2.7 is a citation-bookkeeping patch — single-line cited-identifier update at §0.11 row 1. No new edge, no classification change, no acceptance criterion change.

**NOTE:** the cost-attribution audit-write seam (§2.3.7 row 8) amendment owed per `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` §6 is NOT part of this v2.7 — that amendment is deferred to a future v2.8 when paired with U-CP-72 implementation.

### §0.5 Downstream absorption owed (post-v2.7)

(a) Workspace `CLAUDE.md` §2.4 CXA row version bump (v2.6 → v2.7).
(b) Co-published artifacts at the path-β rename arc:
- `Spec_Harness_Runtime_v1.md` v1.13 → v1.14 (§14.6 citation update)
- `Implementation_Plan_Control_Plane_v2.16.md` (CP plan §0 change-note absorbing U-CP-47 rename — owed)
- 10 landed code files (already renamed at commit `744848c`)

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_7.md` |
| Version | v2.7 |
| Filing event | Path β citation reconciliation, 2026-05-21 |
| Predecessor | `Cross_Axis_Composition_Document_v2_6.md` (preserved verbatim outside §0.11 row 1) |
| Successor | (none — current canonical) |
| Date | 2026-05-21 |
